# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 10:01:31 2022

@author: Steffen
"""



import numpy as np
from scipy import interpolate
from scipy.ndimage import gaussian_filter
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel,RBF
from radialbasisinterpolation import RadialBasisInterpolation




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
        
    return background

    

def interpol(x_sub,y_sub,subsample,shape,kind):
    
    if(kind=='RBF'):
        points_stacked = np.stack([x_sub,y_sub],-1)
        interp = RadialBasisInterpolation(points_stacked,subsample,kernel="thin_plate")   
    
        # Create background from interpolation
        x_new = np.arange(0,shape[1],1)
        y_new = np.arange(0,shape[0],1)
    
        xx, yy = np.meshgrid(x_new,y_new)
        points_new_stacked = np.stack([xx.ravel(),yy.ravel()],-1)
    
        return interp(points_new_stacked).reshape(shape)
    
    if(kind=='Splines'):
        interp = interpolate.bisplrep(y_sub,x_sub,subsample,s=10*len(x_sub))
        
        # Create background from interpolation
        x_new = np.arange(0,shape[1],1)
        y_new = np.arange(0,shape[0],1)
        return interpolate.bisplev(y_new,x_new,interp)
    
    if(kind=='Kriging'):
        points_stacked = np.stack([x_sub,y_sub],-1)
        
        kernel = ConstantKernel(1.0, constant_value_bounds=(1e-5,1e10)) * RBF(1.0, length_scale_bounds=(1e-5,1e10)) + ConstantKernel(1.0, constant_value_bounds=(1e-5,1e10))
        gp = GaussianProcessRegressor(kernel=kernel)
        gp.fit(points_stacked, subsample)
    
        # Create background from interpolation
        x_new = np.arange(0,shape[1],1)
        y_new = np.arange(0,shape[0],1)
        xx, yy = np.meshgrid(x_new,y_new)
        points_new_stacked = np.stack([xx.ravel(),yy.ravel()],-1)
        
        return gp.predict(points_new_stacked).reshape(shape)