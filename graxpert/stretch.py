import multiprocessing
multiprocessing.freeze_support()

import logging
from concurrent.futures import wait
from multiprocessing import shared_memory

import numpy as np
from astropy.visualization import AsinhStretch
from scipy.optimize import root

from graxpert.mp_logging import get_logging_queue, worker_configurer
from graxpert.parallel_processing import executor


def stretch_channel(shm_name, c, bg, sigma, shape, dtype, logging_queue, logging_configurer, median=None, mad=None):

    logging_configurer(logging_queue)
    logging.info("stretch.stretch_channel started")

    existing_shm = shared_memory.SharedMemory(name=shm_name)
    channels = np.ndarray(shape, dtype, buffer=existing_shm.buf) #[:,:,channel_idx]
    channel = channels[:,:,c]
    
    try:
        indx_clip = np.logical_and(channel < 1.0, channel > 0.0)
        
        if median is None or mad is None:
            median = np.median(channel[indx_clip])
            mad = np.median(np.abs(channel[indx_clip]-median))
        else:
            median = median[c]
            mad = mad[c]

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

def stretch(data, bg, sigma, median=None, mad=None):

    shm = shared_memory.SharedMemory(create=True, size=data.nbytes)
    copy = np.ndarray(data.shape, dtype=data.dtype, buffer=shm.buf)
    np.copyto(copy, data)

    futures = []
    logging_queue = get_logging_queue()
    for c in range(copy.shape[-1]):
        if (median is None and mad is None):
            futures.insert(c, executor.submit(stretch_channel, shm.name, c, bg, sigma, copy.shape, copy.dtype, logging_queue, worker_configurer, median, mad))
    wait(futures)

    copy = np.copy(copy)

    shm.close()
    shm.unlink()

    return copy

def stretch_all(datas, stretch_params):
    
    if stretch_params is None:
        datas = [data.clip(min=0, max=1) for data in datas]
        return datas
    
    bg = stretch_params[0]
    sigma = stretch_params[1]
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


def asinh_stretch(data, bg, sigma):
    
    data = data/np.max(data)
    median = np.median(data)
    deviation_from_median = np.mean(np.abs(data-median))
    
    shadow_clipping = np.clip(median - sigma*deviation_from_median, 0, 1.0)
    highlight_clipping = 1.0
    
    # Use rootfinding to find correct factor a
    a = root(asinhfunc_root, 0.5, ((median-shadow_clipping)/(highlight_clipping - shadow_clipping),bg), method='lm')
    a = np.abs(a.x)
       
    data[data <= shadow_clipping] = 0.0
    data[data >= highlight_clipping] = 1.0
    
    indx_inside = data > shadow_clipping
    
    data[indx_inside] = (data[indx_inside]-shadow_clipping)/(highlight_clipping - shadow_clipping)
    
    asinh = AsinhStretch(a)
    data = asinh(data)

    return data


def asinhfunc_root(a,x,y):
    
    return np.arcsinh(x/a)/np.arcsinh(1/a) - y
    
