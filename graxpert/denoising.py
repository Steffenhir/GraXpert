import numpy as np
import copy
import tensorflow as tf

def denoise(image, window_size, stride, AI_dir = "", strength=1.0):
    input = copy.deepcopy(image)
    
    H, W, _ = image.shape 
    offset = int((window_size - stride) / 2)
    
    h, w, _ = image.shape
    
    ith = int(h / stride) + 1
    itw = int(w / stride) + 1
    
    dh = ith * stride - h
    dw = itw * stride - w
    
    image = np.concatenate((image, image[(h - dh) :, :, :]), axis = 0)
    image = np.concatenate((image, image[:, (w - dw) :, :]), axis = 1)
    
    h, w, _ = image.shape
    image = np.concatenate((image, image[(h - offset) :, :, :]), axis = 0)
    image = np.concatenate((image[: offset, :, :], image), axis = 0)
    image = np.concatenate((image, image[:, (w - offset) :, :]), axis = 1)
    image = np.concatenate((image[:, : offset, :], image), axis = 1)
    
    median = np.median(image[::4,::4,:], axis=[0,1])
    mad = np.median(np.abs(image[::4,::4,:]-median), axis=[0,1])
    
    output = copy.deepcopy(image)
    model = tf.keras.models.load_model(AI_dir)
    
    for i in range(ith):
        print(str(i) + " of " + str(ith))
        for j in range(itw):
            x = stride * i
            y = stride * j
            
            tile = image[x:x+window_size, y:y+window_size, :]
            tile = (tile - median) / mad * 0.04
            tile_copy = tile.copy()
            tile = np.clip(tile, -1.0, 1.0)
            
            tile = np.expand_dims(tile, axis = 0)
            tile = np.array(model(tile)[0])
            
            tile = np.where(tile_copy < 0.95, tile, tile_copy)
            tile = tile / 0.04 * mad + median
            tile = tile[offset:offset+stride, offset:offset+stride, :]
            output[x+offset:stride*(i+1)+offset, y+offset:stride*(j+1)+offset, :] = tile
    
    output = np.clip(output, 0, 1)
    output = output[offset:H+offset,offset:W+offset,:]
    
    return output * strength + input * (strength - 1)