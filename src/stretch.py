# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 16:44:29 2022

@author: steff
"""

import numpy as np
from astropy.visualization import AsinhStretch
from scipy.optimize import root

def stretch(data, bg, sigma):

    copy = np.copy(data)
    
    for c in range(copy.shape[-1]):
        
        copy_color = copy[:,:,c]
        
        median = np.median(copy_color)
        deviation_from_median = np.mean(np.abs(copy_color-median))

    
        shadow_clipping = np.clip(median - sigma*deviation_from_median, 0, 1.0)
        highlight_clipping = 1.0

        midtone = MTF((median-shadow_clipping)/(highlight_clipping - shadow_clipping),bg)


        copy_color[copy_color <= shadow_clipping] = 0.0
        copy_color[copy_color >= highlight_clipping] = 1.0
    
        indx_inside = np.logical_and(copy_color > shadow_clipping, copy_color < highlight_clipping)
    
        copy_color[indx_inside] = (copy_color[indx_inside]-shadow_clipping)/(highlight_clipping - shadow_clipping)
    
        copy_color = MTF(copy_color, midtone)
    
        copy[:,:,c] = copy_color
    
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
    
