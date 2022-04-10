# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 16:44:29 2022

@author: steff
"""

import numpy as np
from astropy.visualization import AsinhStretch
from scipy.optimize import root
import concurrent
import multiprocessing as mp

def stretch_channel(channel, bg, sigma):
    
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

    return channel

def stretch(data, bg, sigma):

    copy = np.copy(data)
    #copy = data
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=3, mp_context=mp.get_context('spawn')) as executor:

        parallel_compute = False

        if parallel_compute == False:
            for c in range(copy.shape[-1]):
                copy[:,:,c] = stretch_channel(copy[:,:,c], bg, sigma)
        else:
            futures = []
            for c in range(copy.shape[-1]):
                futures.insert(c, executor.submit(stretch_channel, copy[:,:,c], bg, sigma))
                print("submitted stretch_channel {}".format(c))
            for c in range(copy.shape[-1]):
                copy[:,:,c] = futures[c].result()
                print("received stretch_channel {}".format(c))

    copy = copy.clip(min=0,max=1)

    return copy
    

def MTF(data, midtone):
    
    data = (midtone-1)*data/((2*midtone-1)*data-midtone)

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
    
