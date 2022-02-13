# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 10:01:31 2022

@author: Steffen
"""


from PIL import Image
import numpy as np
from scipy import interpolate
from scipy.ndimage import gaussian_filter




# Load image
im = Image.open('M81.tiff')
imarray = np.array(im)



def extract_background(imarray, background_points,interpolation_type):

    num_colors = imarray.shape[2]
    x_size = imarray.shape[1]
    y_size = imarray.shape[0]
    
    # Blur image with Gaussian blur
    s = 5   # sigma
    w = 50  # Kernel width
    t = (((w - 1)/2)-0.5)/s
    
    blur = gaussian_filter(imarray,sigma=(s,s,0),truncate = t)
    
    background = np.zeros((y_size,x_size,num_colors))
    
    for c in range(num_colors):
        

        x_sub = np.array(background_points[:,0],dtype=int)
        y_sub = np.array(background_points[:,1],dtype=int)
        subsample=np.array(blur[y_sub,x_sub,c])


        background[:,:,c] = interpol(x_sub,y_sub,subsample,(y_size,x_size),interpolation_type)

        
        #Subtract background from image
        imarray[:,:,c] = (imarray[:,:,c] - background[:,:,c] + np.std(background[:,:,c])).clip(min=0,max=np.max(imarray[:,:,c]))

    

def interpol(x_sub,y_sub,subsample,shape,kind):
    
    if(kind=='RBF'):
        points_stacked = np.stack([x_sub,y_sub],-1)
        interp = interpolate.RBFInterpolator(points_stacked,subsample,kernel='thin_plate_spline')   
    
        # Create background from interpolation
        x_new = np.arange(0,shape[1],1)
        y_new = np.arange(0,shape[0],1)
    
        xx, yy = np.meshgrid(x_new,y_new)
        points_new_stacked = np.stack([xx.ravel(),yy.ravel()],-1)
    
        return interp(points_new_stacked).reshape(shape)
    
    if(kind=='Splines'):
        interp = interpolate.interp2d(x_sub,y_sub,subsample,kind='cubic')
        
        # Create background from interpolation
        x_new = np.arange(0,shape[1],1)
        y_new = np.arange(0,shape[0],1)
        return interp(x_new,y_new)