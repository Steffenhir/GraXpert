import multiprocessing
multiprocessing.freeze_support()

import logging
from concurrent.futures import wait
from multiprocessing import shared_memory

import numpy as np

from graxpert.mp_logging import get_logging_queue, worker_configurer
from graxpert.parallel_processing import executor


class StretchParameters:
    stretch_option: str
    bg: float
    sigma: float
    do_stretch: bool = True
    channels_linked: bool = False
    images_linked: bool = False
    
    def __init__(self, stretch_option: str): 
        self.stretch_option = stretch_option
        
        if stretch_option == "No Stretch":
            self.do_stretch = False
        
        elif stretch_option == "10% Bg, 3 sigma":
            self.bg = 0.1
            self.sigma = 3.0

        elif stretch_option == "15% Bg, 3 sigma":
            self.bg = 0.15
            self.sigma = 3.0

        elif stretch_option == "20% Bg, 3 sigma":
            self.bg = 0.2
            self.sigma = 3.0

        elif stretch_option == "30% Bg, 2 sigma":
            self.bg = 0.3
            self.sigma = 2.0
            

def stretch_channel(shm_name, c, bg, sigma, shape, dtype, logging_queue, logging_configurer):

    logging_configurer(logging_queue)
    logging.info("stretch.stretch_channel started")

    existing_shm = shared_memory.SharedMemory(name=shm_name)
    channels = np.ndarray(shape, dtype, buffer=existing_shm.buf) #[:,:,channel_idx]
    channel = channels[:,:,c]
    
    try:
        indx_clip = np.logical_and(channel < 1.0, channel > 0.0)
        median = np.median(channel[indx_clip])
        mad = np.median(np.abs(channel[indx_clip]-median))

        shadow_clipping = np.clip(median - sigma*mad, 0, 1.0)
        highlight_clipping = 1.0

        midtone = MTF((median-shadow_clipping)/(highlight_clipping - shadow_clipping), bg)

        channel[channel <= shadow_clipping] = 0.0
        channel[channel >= highlight_clipping] = 1.0

        indx_inside = np.logical_and(channel > shadow_clipping, channel < highlight_clipping)

        channel[indx_inside] = (channel[indx_inside]-shadow_clipping)/(highlight_clipping - shadow_clipping)

        channel = MTF(channel, midtone)

    except:
        logging.exception("An error occured while stretching a color channel")
    finally:
        existing_shm.close()
    
    logging.info("stretch.stretch_channel finished")

def stretch(data, stretch_params: StretchParameters):
    return stretch_all([data], stretch_params)[0]

def stretch_all(datas, stretch_params: StretchParameters):
    
    if not stretch_params.do_stretch:
        datas = [data.clip(min=0, max=1) for data in datas]
        return datas
    
    bg = stretch_params.bg
    sigma = stretch_params.sigma
    futures = []
    shms = []
    copies = []
    result = []

    logging_queue = get_logging_queue()
    for data in datas:
        shm = shared_memory.SharedMemory(create=True, size=data.nbytes)
        copy = np.ndarray(data.shape, dtype=data.dtype, buffer=shm.buf)
        np.copyto(copy, data)
        shms.append(shm)
        copies.append(copy)
        for c in range(copy.shape[-1]):
            futures.insert(c, executor.submit(stretch_channel, shm.name, c, bg, sigma, copy.shape, copy.dtype, logging_queue, worker_configurer))
    wait(futures)

    for copy in copies:
        copy = np.copy(copy)
        result.append(copy)
    
    for shm in shms:
        shm.close()
        shm.unlink()
    
    return result
    

def MTF(data, midtone):

    if type(data) is np.ndarray:
        data[:] = (midtone-1)*data[:]/((2*midtone-1)*data[:]-midtone)
    else:
        data = (midtone-1) * data / ((2*midtone-1) * data - midtone)

    return data

    
