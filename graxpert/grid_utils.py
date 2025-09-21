import logging
import math

import numpy as np


def find_darkest_quadrant(x, y, data_padded, sample_size):

    cords = [
        [x + 0, y + 0],
        [x + sample_size, y + sample_size],
        [x - sample_size, y + sample_size],
        [x + sample_size, y - sample_size],
        [x - sample_size, y - sample_size],
    ]
    median = []
    for point in cords:
        if (
            point[0] < 0
            or point[0] > (data_padded.shape[1] - 2 * sample_size)
            or point[1] < 0
            or point[1] > (data_padded.shape[0] - 2 * sample_size)
        ):
            median.append(2)
        else:
            m = np.median(
                data_padded[
                    point[1] : point[1] + 2 * sample_size,
                    point[0] : point[0] + 2 * sample_size,
                ]
            )
            if math.isnan(m):
                logging.error("computed median is NaN", stack_info=True)
            median.append(m)

    min_idx = np.argmin(median)

    return cords[min_idx], median[min_idx]
