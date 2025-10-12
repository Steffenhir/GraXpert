import copy
import logging
import time

import numpy as np

from graxpert.ai_model_handling import SessionContext
from graxpert.application.app_events import AppEvents
from graxpert.application.eventbus import eventbus
from graxpert.ui.ui_events import UiEvents


def denoise(image, ai_path, strength, batch_size=4, window_size=256, stride=128, progress=None, ai_gpu_acceleration=True):
    logging.info("Starting denoising")

    if batch_size < 1:
        logging.info(f"mapping batch_size of {batch_size} to 1")
        batch_size = 1
    elif batch_size > 32:
        logging.info(f"mapping batch_size of {batch_size} to 32")
        batch_size = 32
    elif not (batch_size & (batch_size - 1) == 0):  # check if batch_size is power of two
        logging.info(f"mapping batch_size of {batch_size} to {2 ** (batch_size).bit_length() // 2}")
        batch_size = 2 ** (batch_size).bit_length() // 2  # map batch_size to power of two

    input = copy.deepcopy(image)

    median = np.median(image[::4, ::4, :], axis=[0, 1])
    mad = np.median(np.abs(image[::4, ::4, :] - median), axis=[0, 1])
    
    if "1.0.0" in ai_path or "1.1.0" in ai_path:
        model_threshold = 1.0
    else:
        model_threshold = 10.0

    global cached_denoised_image
    if cached_denoised_image is not None:
        return blend_images(input, cached_denoised_image, strength, model_threshold, median, mad)

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

    output = copy.deepcopy(image)

    cancel_flag = False

    def cancel_listener(event):
        nonlocal cancel_flag
        cancel_flag = True

    eventbus.add_listener(AppEvents.CANCEL_PROCESSING, cancel_listener)

    # allow persistent changes to gpu_accel in case of failure
    context = SessionContext(ai_path, gpu_acceleration=ai_gpu_acceleration)
    last_progress = 0
    for b in range(0, ith * itw + batch_size, batch_size):

        if cancel_flag:
            logging.info("Denoising cancelled")
            eventbus.remove_listener(AppEvents.CANCEL_PROCESSING, cancel_listener)
            return None

        input_tiles = []
        input_tile_copies = []
        for t_idx in range(0, batch_size):

            index = b + t_idx
            i = index % ith
            j = index // ith

            if i >= ith or j >= itw:
                break

            x = stride * i
            y = stride * j

            tile = image[x : x + window_size, y : y + window_size, :]
            tile = (tile - median) / mad * 0.04
            input_tile_copies.append(np.copy(tile))
            tile = np.clip(tile, -model_threshold, model_threshold)

            input_tiles.append(tile)

        if not input_tiles:
            continue

        input_tiles = np.array(input_tiles)

        output_tiles = []
        session_result = context.run({ "gen_input_image": input_tiles})
        for e in session_result:
            output_tiles.append(e)

        output_tiles = np.array(output_tiles)

        for t_idx, tile in enumerate(output_tiles):

            index = b + t_idx
            i = index % ith
            j = index // ith

            if i >= ith or j >= itw:
                break

            x = stride * i
            y = stride * j
            tile = np.where(input_tile_copies[t_idx] < model_threshold, tile, input_tile_copies[t_idx])
            tile = tile / 0.04 * mad + median
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

    if num_colors == 1:
        output = np.array([output[:, :, 0]])
        output = np.moveaxis(output, 0, -1)

    cached_denoised_image = output
    output = blend_images(input, output, strength, model_threshold, median, mad)

    eventbus.remove_listener(AppEvents.CANCEL_PROCESSING, cancel_listener)
    logging.info("Finished denoising")

    return output


def blend_images(original_image, denoised_image, strength, threshold, median, mad):
    threshold = threshold / 0.04 * mad + median
    blend = np.where(original_image < threshold, denoised_image, original_image)
    blend = blend * strength + original_image * (1 - strength)
    return np.clip(blend, 0, 1)


def reset_cached_denoised_image(event):
    global cached_denoised_image
    cached_denoised_image = None


cached_denoised_image = None
eventbus.add_listener(AppEvents.LOAD_IMAGE_REQUEST, reset_cached_denoised_image)
eventbus.add_listener(AppEvents.CALCULATE_REQUEST, reset_cached_denoised_image)
eventbus.add_listener(UiEvents.APPLY_CROP_REQUEST, reset_cached_denoised_image)
eventbus.add_listener(AppEvents.DENOISE_AI_VERSION_CHANGED, reset_cached_denoised_image)
