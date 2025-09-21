import logging

import numpy as np

"""
Find the mode of a distribution using a route based on the SKYALL as described in
https://articles.adsabs.harvard.edu//full/1993MNRAS.265..641A/0000643.000.html
"""

def mode(distribution):
    
    # Find appropriate intensity range
    
    clip = np.logical_and(distribution > 0.0, distribution < 1.0)

    median = np.median(distribution[clip])

    left_of_median = np.where(distribution < median)
    right_of_median = np.where(distribution > median)
    
    rms_left = np.sqrt(np.sum((distribution[left_of_median] - median)**2)/distribution.size)
    rms_right= np.sqrt(np.sum((distribution[right_of_median] - median)**2)/distribution.size)
    
    rms = np.min([rms_left,rms_right])

    lower_bound = np.max([0.0, median - 2*rms])
    upper_bound = np.min([1.0, median + 2*rms])
    
    
    # Set initial number of bins
    
    num_bins = 8
    histo, bin_edges = np.histogram(distribution, bins=num_bins, range=(lower_bound,upper_bound), density=True)
    
    found = False
    iterations = 0
    
    while(not found and iterations <= 20):
        
        max_bin = np.argmax(histo)
        max_value = histo[max_bin]
        
        left_pointer = max_bin
        right_pointer = max_bin
        
        while(histo[left_pointer] > max_value/1.75):
            left_pointer = left_pointer - 1
            if(left_pointer < 0):
                left_pointer = 0
                break
            
        while(histo[right_pointer] > max_value/1.75):
            right_pointer = right_pointer + 1
            if(right_pointer >= bin_edges.size - 1):
                right_pointer = bin_edges.size - 2
                break
            
        if(right_pointer - left_pointer > 5):
            found = True

        else:
            found = False
            num_bins = int(num_bins * 1.5)
            histo, bin_edges = np.histogram(distribution, bins=num_bins, range=(lower_bound,upper_bound), density=True)
            
        iterations = iterations + 1

        if(iterations > 20):
            logging.debug("More than 20 iterations in second step of SKYALL. Return median instead.")
            return median
    
    #print(bin_edges[left_pointer])
    #print(bin_edges[right_pointer])
    lower_bound = (bin_edges[left_pointer] + bin_edges[left_pointer+1])/2
    upper_bound = (bin_edges[right_pointer] + bin_edges[right_pointer+1])/2
    histo, bin_edges = np.histogram(distribution, bins=num_bins, range=(lower_bound,upper_bound), density=True)
    
    # Find best fit
    
    best_coeff = np.array([0,0,0])
    best_err = -1
    
    iterations = 0
    
    while(iterations < 20):
        
        x = averaged_histo(distribution, bin_edges)
        coeff, err, misc1, misc2, misc3 = np.polyfit(x, histo, deg=2, full=True)
        err = err/x.size
        
        if(err < best_err or best_err == -1):
            best_err = err
            best_coeff = coeff
            
        if(err > 1.3*best_err and best_err != -1):
            break
    
        iterations = iterations + 1

        if(iterations >= 20):
            
            logging.debug("More than 20 iterations in third step of SKYAL. Return median instead.")
            return median
            
        num_bins = int(num_bins*1.5)
        histo, bin_edges = np.histogram(distribution, bins=num_bins, range=(lower_bound,upper_bound), density=True)
        

    
    mode = -best_coeff[1]/2/best_coeff[0]
    
    # Testing
    #plt.hist(distribution.ravel(),50,range=(0.1,0.5), density=True)
    #plt.hist(distribution.ravel(),10,range=(bin_edges[0],bin_edges[-1]), density=True)
    #plt.plot(np.arange(bin_edges[0],bin_edges[-1],0.01), f(np.arange(bin_edges[0],bin_edges[-1],0.01),best_coeff), color="g")
    #plt.axvline(np.mean(distribution), color='r', label="Mean")
    #plt.axvline(np.median(distribution), color='k', label="Median")
    #plt.axvline(mode, color='g', label="Mode")
    #plt.legend()
    #plt.savefig("vergleich.jpg")
    return mode
        
    
    
    
def averaged_histo(distribution, bin_edges):
    
    x = np.zeros(bin_edges.shape[0]-1)
    
    for i in range(x.shape[0]):
        idx = np.logical_and(distribution >= bin_edges[i], distribution < bin_edges[i+1])
        
        if(distribution[idx].shape[0] == 0):
            x[i] = (bin_edges[i] + bin_edges[i+1])/2.0
        else:
            x[i] = np.mean(distribution[idx])
        
    return x

def f(x, coeff):
    return coeff[0]*x**2 + coeff[1]*x + coeff[2]



# Testing
# from skimage import img_as_float32, io
#y=3100
#x=483
#size=25
#im = img_as_float32(io.imread("../../milchstr.tif")[x-size:x+size,y-size:y+size,0])

#mode(im)
