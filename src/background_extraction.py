# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 10:01:31 2022

@author: Steffen
"""

import numpy as np
from scipy import interpolate
from radialbasisinterpolation import RadialBasisInterpolation
from scipy import linalg
from pykrige.ok import OrdinaryKriging
from skimage.transform import resize
from astropy.stats import sigma_clipped_stats
# from gpr_cuda import GPRegression
import multiprocessing as mp
import concurrent


def clip(imarray, max):
    imarray[:,:] = imarray.clip(min=0,max=np.max(imarray))
    return imarray

def subtract_background(imarray, background, mean):
    return imarray[:,:] - background[:,:] + mean

def extract_background(imarray, background_points,interpolation_type,smoothing,downscale_factor):

    num_colors = imarray.shape[2]
    x_size = imarray.shape[1]
    y_size = imarray.shape[0]
    
    background = np.zeros((y_size,x_size,num_colors), dtype=np.float32)
    
    parallel_compute = True

    with concurrent.futures.ProcessPoolExecutor(max_workers=3, mp_context=mp.get_context('spawn')) as executor:

        if parallel_compute == False:
            print("interpolate single core")
            for c in range(num_colors):
                
                x_sub = np.array(background_points[:,0],dtype=int)
                y_sub = np.array(background_points[:,1],dtype=int)
                subsample = calc_mode_dataset(imarray[:,:,c], x_sub, y_sub, 25)

                background[:,:,c] = interpol(imarray[:,:,c],x_sub,y_sub,(y_size,x_size),interpolation_type,smoothing,downscale_factor)

        else:
            print("interpolate multi core")
            x_sub = np.array(background_points[:,0],dtype=int)
            y_sub = np.array(background_points[:,1],dtype=int)
                
            futures = []
            for c in range(num_colors):
                futures.insert(c, executor.submit(interpol, imarray[:,:,c],x_sub,y_sub, (y_size,x_size),interpolation_type,smoothing,downscale_factor))
                print("submitted interpol {}".format(c))
            for c in range(num_colors):
                background[:,:,c] = futures[c].result()
                print("received interpol {}".format(c))
            
        #Subtract background from image
        mean = np.mean(background)
        parallel_compute = False
        if parallel_compute == False:
            print("subtract single core")
            imarray[:,:,:] = (imarray[:,:,:] - background[:,:,:] + mean).clip(min=0,max=np.max(imarray))
        else:
            print("subtract multi core")

            futures = []
            for c in range(num_colors):
                futures.insert(c, executor.submit(subtract_background, imarray[:,:,c], background[:,:,c], mean))
                print("submitted subtract_background {}".format(c))
            for c in range(num_colors):
                imarray[:,:,c] = futures[c].result()
                print("received subtract_background {}".format(c))

        #clip image
        max=np.max(imarray)
        parallel_compute = False
        if parallel_compute == False:
            print("clip single core")
            imarray[:,:,:] = imarray.clip(min=0,max=np.max(imarray))
        else:
            print("clip multi core")
            futures = []
            for c in range(num_colors):
                futures.insert(c, executor.submit(clip, imarray[:,:,c], max))
                print("submitted clip {}".format(c))
            for c in range(num_colors):
                imarray[:,:,c] = futures[c].result()
                print("received clip {}".format(c))
        
    return background


def calc_mode_dataset(data, x_sub, y_sub, halfsize):
    
    n = x_sub.shape[0]
    data_padded = np.pad(array=data, pad_width=(halfsize,), mode="reflect")
    subsample = np.zeros(n)
    
    for i in range(n):
        data_footprint = data_padded[y_sub[i]:y_sub[i]+2*halfsize,x_sub[i]:x_sub[i]+2*halfsize]
        subsample[i] = sigma_clipped_stats(data=data_footprint, cenfunc="median", stdfunc="std", grow=4)[1]
        
    return subsample



def interpol(imarray,x_sub,y_sub,shape,kind,smoothing,downscale_factor):

    subsample = calc_mode_dataset(imarray, x_sub, y_sub, 25)
    
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
        interp = RadialBasisInterpolation(points_stacked,subsample,kernel="thin_plate",smooth=smoothing*linalg.norm(subsample)/np.sqrt(len(subsample)))   
    
        # Create background from interpolation
        x_new = np.arange(0,shape_scaled[1],1)
        y_new = np.arange(0,shape_scaled[0],1)
    
        xx, yy = np.meshgrid(x_new,y_new)
        points_new_stacked = np.stack([xx.ravel(),yy.ravel()],-1)
    
        result = interp(points_new_stacked).reshape(shape_scaled)
    
    elif(kind=='Splines'):
        interp = interpolate.bisplrep(y_sub,x_sub,subsample,w=np.ones(len(x_sub))/np.std(subsample), s=smoothing*len(x_sub))
        
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
    

