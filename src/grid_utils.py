# -*- coding: utf-8 -*-
"""
Created on Sat Oct 01 19:31:00 2022

@author: David
"""

import numpy as np
import math


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
                print("oha")
            median.append(m)

    min_idx = np.argmin(median)

    return cords[min_idx], median[min_idx]
