# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 10:01:31 2022

@author: Steffen
"""



import numpy as np
from scipy import interpolate
from radialbasisinterpolation import RadialBasisInterpolation
from scipy import linalg, stats, optimize
from pykrige.ok import OrdinaryKriging
from skimage.transform import resize
# from gpr_cuda import GPRegression




def extract_background(imarray, background_points,interpolation_type,smoothing,downscale_factor):
    
    
    num_colors = imarray.shape[2]
    x_size = imarray.shape[1]
    y_size = imarray.shape[0]

    
    background = np.zeros((y_size,x_size,num_colors), dtype=np.float32)
    
    for c in range(num_colors):
        
        x_sub = np.array(background_points[:,0],dtype=int)
        y_sub = np.array(background_points[:,1],dtype=int)
        subsample = calc_median_dataset(imarray[:,:,c], x_sub, y_sub, 25)

        background[:,:,c] = interpol(x_sub,y_sub,subsample,(y_size,x_size),interpolation_type,smoothing,downscale_factor)
        
    
    #Subtract background from image
    mean = np.mean(background)
    imarray[:,:,:] = (imarray[:,:,:] - background[:,:,:] + mean).clip(min=0,max=np.max(imarray))
        
    return background


def calc_median_dataset(data, x_sub, y_sub, halfsize):
    
    n = x_sub.shape[0]
    data_padded = np.pad(array=data, pad_width=(halfsize,), mode="reflect")
    subsample = np.zeros(n)
    
    for i in range(n):
        data_footprint = data_padded[y_sub[i]:y_sub[i]+2*halfsize,x_sub[i]:x_sub[i]+2*halfsize].ravel()
        subsample[i] = np.median(data_footprint)
        
    return subsample



def interpol(x_sub,y_sub,subsample,shape,kind,smoothing,downscale_factor):
    
    if(downscale_factor != 1):
        
        x_sub = x_sub / shape[1]
        y_sub = y_sub / shape[0]
        
        shape_scaled = (shape[0] // downscale_factor, shape[1] // downscale_factor)
        
        x_sub = x_sub * shape_scaled[1]
        y_sub = y_sub * shape_scaled[0]
    
    else:
        
        shape_scaled = shape
        
     
    
    if(kind=='RBF'):
        points_stacked = np.stack([x_sub,y_sub],-1)
        interp = RadialBasisInterpolation(points_stacked,subsample,kernel="thin_plate",smooth=smoothing*1e-10*linalg.norm(subsample)/np.sqrt(len(subsample)))   
    
        # Create background from interpolation
        x_new = np.arange(0,shape_scaled[1],1)
        y_new = np.arange(0,shape_scaled[0],1)
    
        xx, yy = np.meshgrid(x_new,y_new)
        points_new_stacked = np.stack([xx.ravel(),yy.ravel()],-1)
    
        result = interp(points_new_stacked).reshape(shape_scaled)
    
    elif(kind=='Splines'):
        interp = interpolate.bisplrep(y_sub,x_sub,subsample,s=smoothing*np.sum(subsample**2))
        
        # Create background from interpolation
        x_new = np.arange(0,shape_scaled[1],1)
        y_new = np.arange(0,shape_scaled[0],1)
        result = interpolate.bisplev(y_new,x_new,interp)
    
    elif(kind=='Kriging'):
        OK = OrdinaryKriging(
            x=x_sub,
            y=y_sub,
            z=subsample,
            variogram_model="spherical",
            verbose=False,
            enable_plotting=False,
        )
    
        # Create background from interpolation
        x_new = np.arange(0,shape_scaled[1],1).astype("float64")
        y_new = np.arange(0,shape_scaled[0],1).astype("float64")

        result, var = OK.execute("grid", xpoints=x_new, ypoints=y_new, backend="C")
    
    # if(kind=='GPR_CUDA'):
    #     # A likelihood in GPyTorch specifies the mapping from latent function values f(X) to observed labels y.
    #     gpr = GPRegression(
    #         x_sub=x_sub,
    #         y_sub=y_sub,
    #         subsample=subsample, 
    #         shape=shape_scaled
    #     )
    #     result = gpr.run()
    #     del gpr
    
    else:
        
        print("Interpolation method not recognized")
        return
    
    if(downscale_factor != 1):
        result = resize(result, shape, preserve_range=True)
        
    return result
    

