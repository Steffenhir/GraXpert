import copy
import logging

import numpy as np
import onnxruntime as ort


def denoise(image, ai_path, window_size=256, stride=128, strength=1.0, progress=None):

    input = copy.deepcopy(image)

    H, W, _ = image.shape
    offset = int((window_size - stride) / 2)

    h, w, _ = image.shape

    ith = int(h / stride) + 1
    itw = int(w / stride) + 1

    dh = ith * stride - h
    dw = itw * stride - w

    image = np.concatenate((image, image[(h - dh) :, :, :]), axis=0)
    image = np.concatenate((image, image[:, (w - dw) :, :]), axis=1)

    h, w, _ = image.shape
    image = np.concatenate((image, image[(h - offset) :, :, :]), axis=0)
    image = np.concatenate((image[:offset, :, :], image), axis=0)
    image = np.concatenate((image, image[:, (w - offset) :, :]), axis=1)
    image = np.concatenate((image[:, :offset, :], image), axis=1)

    median = np.median(image[::4, ::4, :], axis=[0, 1])
    mad = np.median(np.abs(image[::4, ::4, :] - median), axis=[0, 1])

    output = copy.deepcopy(image)

    session = ort.InferenceSession(ai_path, providers=ort.get_available_providers())

    for i in range(ith):
        for j in range(itw):
            x = stride * i
            y = stride * j

            tile = image[x : x + window_size, y : y + window_size, :]
            tile = (tile - median) / mad * 0.04
            tile_copy = tile.copy()
            tile = np.clip(tile, -1.0, 1.0)

            tile = np.expand_dims(tile, axis=0)
            tile = np.array(session.run(None, {"gen_input_image": tile})[0][0])

            tile = np.where(tile_copy < 0.95, tile, tile_copy)
            tile = tile / 0.04 * mad + median
            tile = tile[offset : offset + stride, offset : offset + stride, :]
            output[x + offset : stride * (i + 1) + offset, y + offset : stride * (j + 1) + offset, :] = tile

        if progress is not None:
            progress.update(int(100 / ith))
        else:
            logging.info(f"Progress: {int(i/ith*100)}%")

    output = np.clip(output, 0, 1)
    output = output[offset : H + offset, offset : W + offset, :]

    return output * strength + input * (strength - 1)
