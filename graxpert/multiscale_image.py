import logging
import multiprocessing
multiprocessing.freeze_support()
from multiprocessing import shared_memory


from concurrent.futures import wait
from parallel_processing import executor

from mp_logging import get_logging_queue, worker_configurer


import numpy as np
import scipy as sp
import skimage as sk
from PIL import Image
import cv2

downsample_threshold_scale = 10

# build up circular-like masks for median filter
median_filter_masks = []

for i in range(downsample_threshold_scale+1):
    median_filter_masks.append(sk.morphology.disk(2**i))




# Represents an image consisting of different scales (fine to coarse details) and a residual image. Different scales are extracted using a modified median filtering.
# For details we refer to "Image Processing and Data Analysis - The Multiscale Approach" by J.L. Starck, F. Murtagh and A. Bijaoui.

class MultiScaleImage:

    def __init__(self, num_scales):
        self.img_scales = None
        self.img_residual = None
        self.num_scales = num_scales
        self.detail_boost = np.ones(num_scales)
        self.residual_detail_boost = 0.0
        self.denoise_amount = np.zeros(num_scales)
        self.denoise_threshold = np.ones(num_scales)

    def set_scales(self, img_scales):
        self.img_scales = img_scales

    def set_residual(self, img_residual):
        self.img_residual = img_residual

    def set_detail_boost(self, detail_boost):
        self.detail_boost = detail_boost

    def set_denoise_amount(self, denoise_amount):
        self.denoise_amount = denoise_amount

    def set_denoise_threshold(self, denoise_threshold):
        self.denoise_threshold = denoise_threshold

    def set_residual_detail_boost(self, detail_boost):
        self.residual_detail_boost = detail_boost


    @staticmethod
    def decompose_image(img_orig, num_scales):
        orig_shape = np.copy(img_orig.shape)
        
        img_orig = sk.transform.rescale(img_orig, scale=1/10, order = 3, channel_axis=2)
        shm_img_scales = shared_memory.SharedMemory(create=True, size=img_orig.nbytes*num_scales)
        # First image should be original, last image the residual
        shm_img_filtered = shared_memory.SharedMemory(create=True, size=img_orig.nbytes*(num_scales+1))

        img_scales_array = np.ndarray(np.concatenate([[num_scales], img_orig.shape]), dtype=np.float32, buffer=shm_img_scales.buf)
        img_filtered_array = np.ndarray(np.concatenate([[num_scales+1], img_orig.shape]), dtype=np.float32, buffer=shm_img_filtered.buf)

        np.copyto(img_filtered_array[0,:,:,:], img_orig)

        num_colors = img_filtered_array.shape[3]

        futures_median_filtering = []
        logging_queue = get_logging_queue()

        for color_channel in range(num_colors):
            for layer in range(num_scales):
                futures_median_filtering.insert(color_channel*num_scales + layer, executor.submit(MultiScaleImage.apply_median_filters, shm_img_filtered.name, np.float32, img_orig.shape, color_channel, layer, num_scales, logging_queue, worker_configurer))

        wait(futures_median_filtering)

        futures_layer_extraction = []

        for color_channel in range(num_colors):
            futures_layer_extraction.insert(color_channel, executor.submit(MultiScaleImage.extract_layers, shm_img_filtered.name, shm_img_scales.name, np.float32, img_orig.shape, color_channel, num_scales, logging_queue, worker_configurer))

        wait(futures_layer_extraction)

        img_scales = np.copy(img_scales_array)
        img_residual = np.copy(img_filtered_array[num_scales,:,:,:])
        
        img_residual_upscaled = np.ones(orig_shape)
        for c in range(num_colors):
            img_residual_upscaled[:,:,c] = sk.transform.resize(img_residual[:,:,c], orig_shape[:2])

        shm_img_filtered.close()
        shm_img_scales.close()
        shm_img_filtered.unlink()
        shm_img_scales.unlink()

        multiscale_image = MultiScaleImage(num_scales)
        multiscale_image.set_scales(img_scales)
        multiscale_image.set_residual(img_residual_upscaled)

        return multiscale_image

    def recompose_image(self):
        logging.info("Recompose image")
        img_processed = np.copy(self.img_residual)
        img_processed = img_processed * self.residual_detail_boost
        
        num_colors = self.img_scales.shape[3]

        variances = []

        for i in range(self.num_scales):
            variances.append(np.var(self.img_scales[i,:,:,:]))

        for i in range(self.num_scales):
            for color_channel in range(num_colors):
                logging.info("Add layer {} with detail factor {}".format(i, self.detail_boost[i]))
                img_processed[:,:,color_channel] = img_processed[:,:,color_channel] + self.detail_boost[i] * np.multiply(np.ones(self.img_scales[i,:,:,color_channel].shape) - (np.absolute(self.img_scales[i,:,:,color_channel]) < (self.denoise_threshold[i])) * self.denoise_amount[i], self.img_scales[i,:,:,color_channel])
                #img_processed[:,:,color_channel] = img_processed[:,:,color_channel] +  self.img_scales[i,:,:,color_channel]
        return img_processed

    @staticmethod
    def extract_layers(shm_img_filtered_name, shm_img_scales_name, dtype, shape, color_channel, num_scales, logging_queue, logging_configurer):

        logging_configurer(logging_queue)
        logging.info("layer extraction started for color channel {}".format(color_channel))

        try:
            ex_shm_img_filtered = shared_memory.SharedMemory(name=shm_img_filtered_name)
            ex_shm_img_scales = shared_memory.SharedMemory(name=shm_img_scales_name)

            img_filtered_array = np.ndarray(np.concatenate([[num_scales+1], shape]), dtype, buffer=ex_shm_img_filtered.buf)
            img_scales_array = np.ndarray(np.concatenate([[num_scales], shape]), dtype=np.float32, buffer=ex_shm_img_scales.buf)

            img_filtered_array = img_filtered_array[:,:,:,color_channel]
            img_scales_array = img_scales_array[:,:,:,color_channel]

            for i in range(num_scales):
                img_scales_array[i,:,:] = img_filtered_array[i,:,:] - img_filtered_array[i+1,:,:]
                logging.info("Statistics of extracted scale: {} color: {} min: {} max: {}".format(i, color_channel, np.min(img_scales_array[i,:,:]), np.max(img_scales_array[i,:,:])))
        except:
            logging.exception("Error during image decomposition")

        ex_shm_img_filtered.close()
        ex_shm_img_scales.close()

        logging.info("layer extraction finished for color channel {}".format(color_channel))

    def apply_median_filters(shm_img_filtered_name, dtype, shape, color_channel, selected_scale, num_scales, logging_queue, logging_configurer):

        logging_configurer(logging_queue)
        logging.info("median filtering of level {} for color channel {} started".format(selected_scale, color_channel))

        try:
            ex_shm_img_filtered = shared_memory.SharedMemory(name=shm_img_filtered_name)

            img_filtered_array = np.ndarray(np.concatenate([[num_scales+1], shape]), dtype, buffer=ex_shm_img_filtered.buf)
            img_filtered_array = img_filtered_array[:,:,:,color_channel]

            if selected_scale <= downsample_threshold_scale:
                img_filtered_array[selected_scale+1,:,:] = sp.ndimage.median_filter(img_filtered_array[0,:,:], footprint=median_filter_masks[selected_scale])
            else:
                orig_shape = img_filtered_array[0,:,:].shape
                img_downsampled = sk.transform.rescale(img_filtered_array[0,:,:], scale=1/(2**(selected_scale-downsample_threshold_scale)), order = 3)
                logging.info("Downscale image before median calculation of level {} for color channel {} to size {}".format(selected_scale, color_channel, img_downsampled.shape))
                img_filtered = sp.ndimage.median_filter(img_downsampled, footprint=median_filter_masks[downsample_threshold_scale])
                #img_filtered_array[selected_scale+1,:,:] = sk.transform.resize_local_mean(img_filtered, orig_shape)
                
                img_filtered_array[selected_scale+1,:,:] = sk.transform.resize(img_filtered, orig_shape, order = 3)
                #img_filtered_array[selected_scale+1,:,:] = np.transpose(cv2.resize(np.transpose(img_filtered), orig_shape, interpolation = cv2.INTER_LANCZOS4))


        except:
            logging.exception("Error during median filtering")

        ex_shm_img_filtered.close()
        logging.info("median filtering of level {} for color channel {} finished".format(selected_scale, color_channel))
        


    

    
