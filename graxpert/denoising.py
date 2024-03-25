import copy
import logging
import time

import numpy as np
import onnxruntime as ort

from graxpert.ai_model_handling import get_execution_providers_ordered


def denoise(image, ai_path, strength, batch_size=5, window_size=256, stride=128, progress=None):

    logging.info("Starting denoising")

    input = copy.deepcopy(image)
    num_colors = image.shape[-1]

    if num_colors == 1:
        image = np.array([image[:, :, 0], image[:, :, 0], image[:, :, 0]])
        image = np.moveaxis(image, 0, -1)

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

    providers = get_execution_providers_ordered()
    ort_options = ort.SessionOptions()
    ort_options.execution_mode = ort.ExecutionMode.ORT_PARALLEL
    session = ort.InferenceSession(ai_path, providers=providers, sess_options=ort_options)

    logging.info(f"Available inference providers : {providers}")
    logging.info(f"Used inference providers : {session.get_providers()}")

    last_progress = 0

    input_tiles = []
    for i in range(ith):
        for j in range(itw):
            x = stride * i
            y = stride * j

            tile = image[x : x + window_size, y : y + window_size, :]
            tile = (tile - median) / mad * 0.04
            # input_tile_copies.append(tile.copy())
            tile = np.clip(tile, -1.0, 1.0)

            input_tiles.append(tile)

        p = int(i / ith * 10)
        if p > last_progress:
            if progress is not None:
                progress.update(p - last_progress)
            else:
                logging.info(f"Progress: {p}%")
            last_progress = p

    input_tiles = np.array(input_tiles)
    input_tile_copies = np.copy(input_tiles).reshape((ith, itw, window_size, window_size, 3))

    output_tiles = []

    elapsed_time = 0
    for i in range(0, ith * itw, batch_size):
        start = time.time()
        session_result = session.run(None, {"gen_input_image": input_tiles[i : i + batch_size]})[0]
        elapsed_time += time.time() - start
        for e in session_result:
            output_tiles.append(e)

        p = int(10 + i / (ith * itw) * 80)
        if p > last_progress:
            if progress is not None:
                progress.update(p - last_progress)
            else:
                logging.info(f"Progress: {p}%")
            last_progress = p

    output_tiles = np.array(output_tiles)
    output_tiles = output_tiles.reshape((ith, itw, window_size, window_size, 3))

    for i in range(ith):
        for j in range(itw):
            x = stride * i
            y = stride * j

            tile = output_tiles[i, j, :]
            tile = np.where(input_tile_copies[i, j] < 0.95, tile, input_tile_copies[i, j])
            tile = tile / 0.04 * mad + median
            tile = tile[offset : offset + stride, offset : offset + stride, :]
            output[x + offset : stride * (i + 1) + offset, y + offset : stride * (j + 1) + offset, :] = tile

        p = int(90 + i / ith * 10)
        if p > last_progress:
            if progress is not None:
                progress.update(p - last_progress)
            else:
                logging.info(f"Progress: {p}%")
            last_progress = p

    output = np.clip(output, 0, 1)
    output = output[offset : H + offset, offset : W + offset, :]
    output = output * strength + input * (1 - strength)
    #
    if num_colors == 1:
        output = np.array([output[:, :, 0]])
        output = np.moveaxis(output, 0, -1)

    logging.info("Finished denoising")

    return output
