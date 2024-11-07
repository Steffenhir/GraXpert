import numpy as np
from skimage import color

import graxpert.skyall
import graxpert.stretch
from graxpert.grid_utils import find_darkest_quadrant


def background_grid_selection(data, num_pts_per_row, tol, sample_size):

    # Convert to mono
    data_mono = np.copy(data)
    if(data_mono.shape[-1] == 3):
        data_mono = color.rgb2gray(data_mono)
    else:
        data_mono = data_mono[:,:,0]
        
    global_median = np.median(data_mono)
    
    background_pts = []
    dist = data_mono.shape[1] / num_pts_per_row
    
    # Create grid
    x_start = int(0.5 * dist)
    y_start = int(0.5 * (data_mono.shape[0] % dist))
    x = x_start
    y = y_start
    
    while(y < data_mono.shape[0]):
        x = x_start
        while(x < data_mono.shape[1]):
            background_pts.append([x,y,1])
            x = int(x + dist)           
        y = int(y+dist)
    
    # Calculate median around each grid point
    local_median = np.zeros(len(background_pts))
    halfsize = sample_size
    data_mono_padded = np.pad(array=data_mono, pad_width=(halfsize,), mode="reflect")

    
    for i in range(len(background_pts)):
        x_pt = background_pts[i][0]
        y_pt = background_pts[i][1]
        
        pt, median = find_darkest_quadrant(x_pt, y_pt, data_mono_padded, halfsize)

        background_pts[i][0] = pt[0]
        background_pts[i][1] = pt[1]
        local_median[i] = median

    # Calculate median average deviation and remove points not within tolerance 
    mad = np.median(np.abs(local_median - global_median))
    
    background_pts_sliced = []
    for i in range(len(background_pts)):
        if(local_median[i] < global_median + tol*mad):
            background_pts_sliced.append(background_pts[i])

    result = []
    for p in background_pts_sliced:
        result.append(np.array(p, dtype=int))
    
    return result
