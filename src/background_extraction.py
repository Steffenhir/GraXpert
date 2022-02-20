# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 10:01:31 2022

@author: Steffen
"""



import numpy as np
from scipy import interpolate
from scipy.ndimage import gaussian_filter
from radialbasisinterpolation import RadialBasisInterpolation
from scipy import linalg
from pykrige.ok import OrdinaryKriging
from skimage.transform import resize
from skimage import img_as_float32
from gpr_cuda import GPRegression




def extract_background(imarray, background_points,interpolation_type,smoothing,downscale_factor):
    
    imarray_scaled, background_points = downscale(imarray, background_points, downscale_factor)
    
    num_colors = imarray_scaled.shape[2]
    x_size = imarray_scaled.shape[1]
    y_size = imarray_scaled.shape[0]
    
    # Blur image with Gaussian blur
    s = 5   # sigma
    w = 50  # Kernel width
    t = (((w - 1)/2)-0.5)/s
    
    blur = gaussian_filter(imarray_scaled,sigma=(s,s,0),truncate = t)
    
    background = np.zeros((y_size,x_size,num_colors), dtype=np.float32)
    
    for c in range(num_colors):
        

        x_sub = np.array(background_points[:,0],dtype=int)
        y_sub = np.array(background_points[:,1],dtype=int)
        subsample=np.array(blur[y_sub,x_sub,c])


        background[:,:,c] = interpol(x_sub,y_sub,subsample,(y_size,x_size),interpolation_type,smoothing)
        
    if downscale_factor != 1:
        background = resize(background, imarray.shape, preserve_range=True)
    
    #Subtract background from image
    mean = np.mean(background)
    imarray[:,:,:] = (imarray[:,:,:] - background[:,:,:] + mean).clip(min=0,max=np.max(imarray))
        
    return background

    

def interpol(x_sub,y_sub,subsample,shape,kind,smoothing):
    
    if(kind=='RBF'):
        points_stacked = np.stack([x_sub,y_sub],-1)
        interp = RadialBasisInterpolation(points_stacked,subsample,kernel="thin_plate",smooth=smoothing*1e-10*linalg.norm(subsample)/np.sqrt(len(subsample)))   
    
        # Create background from interpolation
        x_new = np.arange(0,shape[1],1)
        y_new = np.arange(0,shape[0],1)
    
        xx, yy = np.meshgrid(x_new,y_new)
        points_new_stacked = np.stack([xx.ravel(),yy.ravel()],-1)
    
        return interp(points_new_stacked).reshape(shape)
    
    if(kind=='Splines'):
        interp = interpolate.bisplrep(y_sub,x_sub,subsample,s=smoothing*np.sum(subsample**2)/100)
        
        # Create background from interpolation
        x_new = np.arange(0,shape[1],1)
        y_new = np.arange(0,shape[0],1)
        return interpolate.bisplev(y_new,x_new,interp)
    
    if(kind=='Kriging'):
        OK = OrdinaryKriging(
            x=x_sub,
            y=y_sub,
            z=subsample,
            variogram_model="spherical",
            verbose=False,
            enable_plotting=False,
        )
    
        # Create background from interpolation
        x_new = np.arange(0,shape[1],1).astype("float64")
        y_new = np.arange(0,shape[0],1).astype("float64")


        result, var = OK.execute("grid", xpoints=x_new, ypoints=y_new, backend="C")
        return result

    if(kind=='GPR_CUDA'):
        # A likelihood in GPyTorch specifies the mapping from latent function values f(X) to observed labels y.
        gpr = GPRegression(
            x_sub=x_sub,
            y_sub=y_sub,
            subsample=subsample, 
            shape=shape
        )
        result = gpr.run()
        del gpr
        return result


def downscale(imarray, background_points, downscale_factor):
    
    if downscale_factor == 1:
        return imarray, background_points
    else:
        background_points = background_points//downscale_factor
        imarray = resize(imarray, (imarray.shape[0]//downscale_factor,imarray.shape[1]//downscale_factor), mode="reflect", preserve_range=True)
        return imarray, background_points
    


    
    

