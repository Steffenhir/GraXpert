import multiprocessing
multiprocessing.freeze_support()

import logging
from concurrent.futures import wait
# from gpr_cuda import GPRegression
from multiprocessing import shared_memory

import numpy as np
from astropy.stats import sigma_clipped_stats
from pykrige.ok import OrdinaryKriging
from scipy import interpolate, linalg

from skimage.transform import resize
from skimage.filters import  gaussian

import tensorflow as tf
import os
import sys

from graxpert.mp_logging import get_logging_queue, worker_configurer
from graxpert.parallel_processing import executor
from graxpert.radialbasisinterpolation import RadialBasisInterpolation


def extract_background(in_imarray, background_points, interpolation_type, smoothing, 
                       downscale_factor, sample_size, RBF_kernel, spline_order, corr_type, AI_dir, progress=None):
    
    shm_imarray = shared_memory.SharedMemory(create=True, size=in_imarray.nbytes)
    shm_background = shared_memory.SharedMemory(create=True, size=in_imarray.nbytes)
    imarray = np.ndarray(in_imarray.shape, dtype=np.float32, buffer=shm_imarray.buf)
    background = np.ndarray(in_imarray.shape, dtype=np.float32, buffer=shm_background.buf)
    np.copyto(imarray, in_imarray)
    
    num_colors = imarray.shape[-1]
    
    if interpolation_type == 'AI':
        # Shrink and pad to avoid artifacts on borders
        padding = 8
        imarray_shrink = tf.image.resize(imarray,size=(256 - 2*padding,256 - 2*padding))
        imarray_shrink = np.pad(imarray_shrink, ((padding,padding),(padding,padding),(0,0)), mode='edge')

        median = []
        mad = []

        if progress is not None:
            progress.update(8)
        
        for c in range(num_colors):
            median.append(np.median(imarray_shrink[:,:,c]))
            mad.append(np.median(np.abs(imarray_shrink[:,:,c] - median[c])))

        if progress is not None:
            progress.update(8)
        
        imarray_shrink = (imarray_shrink - median) / mad * 0.04
        imarray_shrink = np.clip(imarray_shrink, -1.0, 1.0)
        
        if progress is not None:
            progress.update(8)
        
        if num_colors == 1:
            imarray_shrink = np.array([imarray_shrink[:,:,0],imarray_shrink[:,:,0],imarray_shrink[:,:,0]])
            imarray_shrink = np.moveaxis(imarray_shrink, 0, -1)
        
        if progress is not None:
            progress.update(8)
            
        model = tf.keras.models.load_model(AI_dir)

        background = np.array(model(np.expand_dims(imarray_shrink, axis=0))[0])
        background = background / 0.04 * mad + median
        
        if progress is not None:
            progress.update(8)
        
        if smoothing != 0:
            sigma = smoothing * 20
            background = gaussian(background,sigma)
        
        if progress is not None:
            progress.update(8)
        
        if num_colors == 1:
            background = np.array([background[:,:,0]])
            background = np.moveaxis(background, 0, -1)
        
        if progress is not None:
            progress.update(8)
        
        # Slice to unpadded size of shrinked image, then resize to original size
        if padding != 0:
            background = background[padding:-padding,padding:-padding,:]
        
        if progress is not None:
            progress.update(8)
        
        background = tf.image.resize(background,size=(in_imarray.shape[0],in_imarray.shape[1]),method='gaussian')
        
        if progress is not None:
            progress.update(8)
              
    
    else:    
        x_sub = np.array(background_points[:,0],dtype=int)
        y_sub = np.array(background_points[:,1],dtype=int)
        
        if progress is not None:
            progress.update(24)
            
        futures = []
        logging_queue = get_logging_queue()
        for c in range(num_colors):
            futures.insert(c, executor.submit(interpol, shm_imarray.name, shm_background.name, c, x_sub, y_sub, in_imarray.shape, interpolation_type, smoothing, downscale_factor, sample_size, RBF_kernel, spline_order, imarray.dtype, logging_queue, worker_configurer))
        wait(futures)
        
        if progress is not None:
            progress.update(48)
    
    #Correction
    if(corr_type == "Subtraction"):
        mean = np.mean(background)
        imarray[:,:,:] = imarray[:,:,:] - background[:,:,:] + mean
    elif(corr_type == "Division"):
        for c in range(num_colors):
            mean = np.mean(imarray[:,:,c])
            imarray[:,:,c] = imarray[:,:,c] / background[:,:,c] * mean
    
    if progress is not None:
        progress.update(8)

    #clip image
    imarray[:,:,:] = imarray.clip(min=0.0,max=1.0)

    in_imarray[:] = imarray[:]
    background = np.copy(background)
    
    if progress is not None:
        progress.update(8)
    
    shm_imarray.close()
    shm_background.close()
    shm_imarray.unlink()
    shm_background.unlink()
    
    return background


def calc_mode_dataset(data, x_sub, y_sub, halfsize):
    
    n = x_sub.shape[0]
    data_padded = np.pad(array=data, pad_width=(halfsize,), mode="reflect")
    subsample = np.zeros(n)
    
    for i in range(n):
        data_footprint = data_padded[y_sub[i]:y_sub[i]+2*halfsize,x_sub[i]:x_sub[i]+2*halfsize]
        subsample[i] = sigma_clipped_stats(data=data_footprint, cenfunc="median", stdfunc="std", grow=4)[1]
        
    return subsample


def interpol(shm_imarray_name, shm_background_name, c, x_sub, y_sub, shape, kind, smoothing, downscale_factor, sample_size, RBF_kernel, spline_order, dtype, logging_queue, logging_configurer):

    logging_configurer(logging_queue)
    logging.info("background_extraction.interpol started")

    try:
        existing_shm_imarray = shared_memory.SharedMemory(name=shm_imarray_name)
        existing_shm_background = shared_memory.SharedMemory(name=shm_background_name)
        imarray = np.ndarray(shape, dtype, buffer=existing_shm_imarray.buf) #[:,:,channel_idx]
        imarray = imarray[:,:,c]
        background = np.ndarray(shape, dtype, buffer=existing_shm_background.buf)
        # background = background[:,:,c]
        shape = imarray.shape
        
        subsample = calc_mode_dataset(imarray, x_sub, y_sub, sample_size)
        
        if(downscale_factor != 1):
            x_sub = x_sub / shape[1]
            y_sub = y_sub / shape[0]
            
            shape_scaled = (shape[0] // downscale_factor, shape[1] // downscale_factor)
            
            x_sub = x_sub * shape_scaled[1]
            y_sub = y_sub * shape_scaled[0]
        
        else:
            shape_scaled = shape
        
        if(kind=='RBF'):
            points_stacked = np.stack([x_sub,y_sub],-1)
            interp = RadialBasisInterpolation(points_stacked,subsample,kernel=RBF_kernel,smooth=smoothing*linalg.norm(subsample)/np.sqrt(len(subsample)))   
        
            # Create background from interpolation
            x_new = np.arange(0,shape_scaled[1],1)
            y_new = np.arange(0,shape_scaled[0],1)
   
            xx, yy = np.meshgrid(x_new,y_new)
            points_new_stacked = np.stack([xx.ravel(),yy.ravel()],-1)
        
            result = interp(points_new_stacked).reshape(shape_scaled)
        
        elif(kind=='Splines'):
            interp = interpolate.bisplrep(y_sub,x_sub,subsample,w=np.ones(len(x_sub))/np.std(subsample), s=smoothing*len(x_sub), kx=spline_order, ky=spline_order)
            
            # Create background from interpolation
            x_new = np.arange(0,shape_scaled[1],1)
            y_new = np.arange(0,shape_scaled[0],1)
            result = interpolate.bisplev(y_new,x_new,interp)
        
        elif(kind=='Kriging'):
            OK = OrdinaryKriging(
                x=x_sub,
                y=y_sub,
                z=subsample,
                variogram_model="spherical",
                verbose=False,
                enable_plotting=False,
            )
        
            # Create background from interpolation
            x_new = np.arange(0,shape_scaled[1],1).astype("float64")
            y_new = np.arange(0,shape_scaled[0],1).astype("float64")

            result = np.zeros(shape_scaled, dtype=np.float32)
            
            num_it = shape_scaled[0]//50
            
            for i in range(num_it):
                result_i, var = OK.execute("grid", xpoints=x_new, ypoints=y_new[i*50:(i+1)*50], backend="vectorized")
                result[i*50:(i+1)*50,:] = result_i
                
            result_i, var = OK.execute("grid", xpoints=x_new, ypoints=y_new[num_it*50:], backend="vectorized")
            result[num_it*50:,:] = result_i

        
        # if(kind=='GPR_CUDA'):
        #     # A likelihood in GPyTorch specifies the mapping from latent function values f(X) to observed labels y.
        #     gpr = GPRegression(
        #         x_sub=x_sub,
        #         y_sub=y_sub,
        #         subsample=subsample, 
        #         shape=shape_scaled
        #     )
        #     result = gpr.run()
        #     del gpr
        
        else:
            logging.warn("Interpolation method not recognized")
            return
        
        if(downscale_factor != 1):
            result = resize(result, shape, preserve_range=True)
            
        background[:,:,c] = result
    except Exception as e:
        logging.exception("Error occured during background_extraction.interpol")
    
    existing_shm_imarray.close()
    existing_shm_background.close()

    logging.info("background_extraction.interpol finished")
