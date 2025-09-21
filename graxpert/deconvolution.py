import copy
import logging

import numpy as np
import onnxruntime as ort

from graxpert.ai_model_handling import get_execution_providers_ordered
from graxpert.application.app_events import AppEvents
from graxpert.application.eventbus import eventbus


def deconvolve(image, ai_path, strength, psfsize, batch_size=4, window_size=512, stride=448, progress=None, ai_gpu_acceleration=True):

    logging.info("Starting deconvolution")
    if "stars" in ai_path:
        type = "Stellar"
    elif "obj" in ai_path:
        type = "Obj"
    strength = 0.95 * strength  # TODO : strenght of exactly 1.0 brings no results, to fix

    if type == "Stellar":
        psfsize = np.clip((psfsize / 2.355 - 1.5) / 3.0, 0.05, 0.95)  # Stellar
    else:
        if "1.0.0" in ai_path:
            psfsize = np.clip((psfsize / 2.355 - 1.0) / 5.0, 0.05, 0.95)  # Object v1.0.0
        else:
            psfsize = np.clip((psfsize / 2.355 - 0.5) / 5.5, 0.05, 0.95)  # Object v1.0.1

    logging.info(f"Calculated normalized PSFsize value: {psfsize}")

    if batch_size < 1:
        logging.info(f"mapping batch_size of {batch_size} to 1")
        batch_size = 1
    elif batch_size > 32:
        logging.info(f"mapping batch_size of {batch_size} to 32")
        batch_size = 32
    elif not (batch_size & (batch_size - 1) == 0):  # check if batch_size is power of two
        logging.info(f"mapping batch_size of {batch_size} to {2 ** (batch_size).bit_length() // 2}")
        batch_size = 2 ** (batch_size).bit_length() // 2  # map batch_size to power of two

    if batch_size >= 4 and image.shape[-1] == 3:
        batch_size = batch_size // 4

    num_colors = image.shape[-1]

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

    output = copy.deepcopy(image)

    providers = get_execution_providers_ordered(ai_gpu_acceleration)
    session = ort.InferenceSession(ai_path, providers=providers)

    logging.info(f"Available inference providers : {providers}")
    logging.info(f"Used inference providers : {session.get_providers()}")

    cancel_flag = False

    def cancel_listener(event):
        nonlocal cancel_flag
        cancel_flag = True

    eventbus.add_listener(AppEvents.CANCEL_PROCESSING, cancel_listener)

    last_progress = 0
    for b in range(0, ith * itw + batch_size, batch_size):

        if cancel_flag:
            logging.info("Deconvolution cancelled")
            eventbus.remove_listener(AppEvents.CANCEL_PROCESSING, cancel_listener)
            return None

        input_tiles = []
        input_tile_copies = []
        params = []
        for t_idx in range(0, batch_size):

            index = b + t_idx
            i = index % ith
            j = index // ith

            if i >= ith or j >= itw:
                break

            x = stride * i
            y = stride * j

            tile = image[x : x + window_size, y : y + window_size, :]

            _min = np.min(tile, axis=(0, 1))
            tile = tile - _min + 1e-5
            tile = np.log(tile)

            _mean = tile.mean()
            _std = tile.std()
            _mean, _std = _mean.astype(np.float32), _std.astype(np.float32)
            tile = (tile - _mean) / _std * 0.1
            params.append([_mean, _std, _min])

            input_tile_copies.append(np.copy(tile))

            input_tiles.append(tile)

        if not input_tiles:
            continue

        input_tiles = np.array(input_tiles)
        input_tiles = np.moveaxis(input_tiles, -1, 1)
        input_tiles = np.reshape(input_tiles, [input_tiles.shape[0] * num_colors, 1, window_size, window_size])

        output_tiles = []
        sigma = np.full(shape=(input_tiles.shape[0], 1), fill_value=psfsize, dtype=np.float32)
        strenght_p = np.full(shape=(input_tiles.shape[0], 1), fill_value=strength, dtype=np.float32)
        conds = np.concatenate([sigma, strenght_p], axis=-1)
        if type == "Obj" and "1.0.0" in ai_path:
            session_result = session.run(None, {"gen_input_image": input_tiles, "sigma": sigma, "strenght": strenght_p})[0]
        else:
            session_result = session.run(None, {"gen_input_image": input_tiles, "params": conds})[0]
        for e in session_result:
            output_tiles.append(e)

        output_tiles = np.array(output_tiles)
        output_tiles = input_tiles - output_tiles
        output_tiles = np.reshape(output_tiles, [output_tiles.shape[0] // num_colors, num_colors, window_size, window_size])
        output_tiles = np.moveaxis(output_tiles, 1, -1)

        for idx in range(len(params)):
            output_tiles[idx] = output_tiles[idx] * params[idx][1] / 0.1 + params[idx][0]
            output_tiles[idx] = np.exp(output_tiles[idx])
            output_tiles[idx] = output_tiles[idx] + params[idx][2] - 1e-5

        for t_idx, tile in enumerate(output_tiles):

            index = b + t_idx
            i = index % ith
            j = index // ith

            if i >= ith or j >= itw:
                break

            x = stride * i
            y = stride * j
            tile = tile[offset : offset + stride, offset : offset + stride, :]
            output[x + offset : stride * (i + 1) + offset, y + offset : stride * (j + 1) + offset, :] = tile

        p = int(b / (ith * itw + batch_size) * 100)
        if p > last_progress:
            if progress is not None:
                progress.update(p - last_progress)
            else:
                logging.info(f"Progress: {p}%")
            last_progress = p

    output = output[offset : H + offset, offset : W + offset, :]
    output = np.clip(output, 0.0, 1.0)

    eventbus.remove_listener(AppEvents.CANCEL_PROCESSING, cancel_listener)
    logging.info("Finished deconvolution")

    return output
