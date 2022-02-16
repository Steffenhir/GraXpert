# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 15:09:15 2022

@author: Steffen
"""


from skimage import color
from skimage.transform import rescale
import numpy as np
import stretch

def background_selection(data, num_pts):
    
    background_pts = []
    
    if(num_pts <= 0):
        return background_pts
    
    
    
    # Normalize and downscale data
    data_norm = color.rgb2gray(data)
    data_norm = rescale(data_norm,1/64, mode="reflect")
    data_norm = stretch.stretch(data_norm,0.3,2)
    data_norm = data_norm + 0.1*np.max(data_norm)
    
    # First point is darkest point in picture
    background_pts.append(np.array(np.unravel_index(data_norm.argmin(),data_norm.shape)))

    pts_current = 1
    

    while(pts_current < num_pts):
        data_map = np.zeros(data_norm.shape)
        for pt in background_pts:
            for x in range(data_map.shape[0]):
                for y in range(data_map.shape[1]):
                
                    dist = (x-pt[0])**2 + (y-pt[1])**2
                    if(dist==0):
                        dist=1e-15
                    
                    data_map[x,y] += data_norm[x,y] / dist
                    
                    
        background_pts.append(np.array(np.unravel_index(data_map.argmin(),data_map.shape)))
        pts_current += 1
    
    for i in range(len(background_pts)):
        background_pts[i] = background_pts[i]*64
    

    return background_pts



# Test

#arr = np.array([[[10,11,12],[13,14,15]],[[1,2,3],[4,5,6]]])

#background_selection(arr,2)
    
    
    