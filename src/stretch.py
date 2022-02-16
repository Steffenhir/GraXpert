# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 16:44:29 2022

@author: steff
"""

import numpy as np

def stretch(data, bg, sigma):
    
    data = data/np.max(data)
    median = np.median(data)
    deviation_from_median = np.mean(np.abs(data-median))

    
    shadow_clipping = np.clip(median - sigma*deviation_from_median, 0, 1.0)
    highlight_clipping = 1.0

    midtone = MTF(median-shadow_clipping,bg)


    data[data <= shadow_clipping] = 0.0
    data[data >= highlight_clipping] = 1.0
    
    indx_inside = data > shadow_clipping
    
    data[indx_inside] = (data[indx_inside]-shadow_clipping)/(highlight_clipping - shadow_clipping)
    
    
    
    data = MTF(data, midtone)
    
    data = np.clip(data,0,1)
    
    return data
    

def MTF(data, midtone):
    
  
    
    data = (midtone-1)*data/((2*midtone-1)*data-midtone)

    
    return data


