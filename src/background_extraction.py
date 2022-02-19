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
from gpytorch.likelihoods import GaussianLikelihood
from gpr_cuda import GPRegressionModel
from gpr_cuda import train as gpr_train
from gpr_cuda import predict as gpr_predict




def extract_background(imarray, background_points,interpolation_type,smoothing):

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


        background[:,:,c] = interpol(x_sub,y_sub,subsample,(y_size,x_size),interpolation_type,smoothing)

        
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

        result, var = OK.execute("grid", xpoints=x_new, ypoints=y_new, n_closest_points=16, backend="C")
        return result
    
    if(kind=='GPR_CUDA'):
        # A likelihood in GPyTorch specifies the mapping from latent function values f(X) to observed labels y.
        likelihood = GaussianLikelihood()
        model = GPRegressionModel(
            x_sub=x_sub,
            y_sub=y_sub,
            subsample=subsample, 
            shape=shape,
            likelihood=likelihood
        )

        gpr_train(model, likelihood)
        result =gpr_predict(model,likelihood)
        del model, likelihood
        return result
