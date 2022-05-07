from enum import Enum

import numpy as np
from scipy.spatial import KDTree
from skimage.color import rgb2gray

from astroimage import AstroImage


class Direction(Enum):
    NORTH = 1
    WEST = 2
    SOUTH = 3
    EAST = 4


def overlap(p1, p2, sample_size):

    if abs(p1[0] - p2[0]) <= sample_size * 2 and abs(p1[1] - p2[1]) <= sample_size * 2:
        return True
    return False


def median_at(point, sample_size, data_mono):
    x_size = len(data_mono[0])
    y_size = len(data_mono)
    x1 = int(point[0] - sample_size / 2)
    y1 = int(point[1] - sample_size / 2)
    x2 = int(point[0] + sample_size / 2 + 1)
    y2 = int(point[1] + sample_size / 2 + 1)
    if x1 < 0:
        x1 = 0
    if y1 < 0:
        y1 = 0
    if x2 >= x_size:
        x2 = x_size
    if y2 >= y_size:
        y2 = y_size
    return np.median(data_mono[y1:y2, x1:x2])


def valid(candidate, valid_interval, sample_size, data_mono):
    x_size = len(data_mono[0])
    y_size = len(data_mono)
    # check out of bounds
    if (
        candidate[0] < 0
        or candidate[1] < 0
        or candidate[0] >= x_size
        or candidate[1] >= y_size
    ):
        return False
    # check tolerance
    candidate_value = median_at(candidate, sample_size, data_mono)

    if not (valid_interval[0] <= candidate_value <= valid_interval[1]):
        return False
    return True


def contains(found_points, point):
    for f in found_points:
        if f[0] == point[0] and f[1] == point[1]:
            return True
    return False


def collect_points(
    found_points,
    from_direction,
    point,
    step_size,
    valid_interval,
    sample_size,
    data_mono,
):
    found_points = np.array(found_points, copy=True, dtype=int)
    point_valid = valid(point, valid_interval, sample_size, data_mono)
    point_in_found_points = contains(found_points, point)
    first_point = from_direction is None

    if not first_point and (not point_valid or point_in_found_points):
        return found_points
    if not first_point and point_in_found_points:
        return found_points
    if not first_point and not point_in_found_points:
        found_points = np.append(found_points, [point], axis=0)

    pt_north = np.copy(point)
    pt_west = np.copy(point)
    pt_south = np.copy(point)
    pt_east = np.copy(point)
    pt_north[1] = int(point[1] - step_size)
    pt_west[0] = int(point[0] - step_size)
    pt_south[1] = int(point[1] + step_size)
    pt_east[0] = int(point[0] + step_size)

    if not from_direction == Direction.NORTH:
        found_points = collect_points(
            found_points,
            Direction.SOUTH,
            pt_north,
            step_size,
            valid_interval,
            sample_size,
            data_mono,
        )
    if not from_direction == Direction.WEST:
        found_points = collect_points(
            found_points,
            Direction.EAST,
            pt_west,
            step_size,
            valid_interval,
            sample_size,
            data_mono,
        )
    if not from_direction == Direction.SOUTH:
        found_points = collect_points(
            found_points,
            Direction.NORTH,
            pt_south,
            step_size,
            valid_interval,
            sample_size,
            data_mono,
        )
    if not from_direction == Direction.EAST:
        found_points = collect_points(
            found_points,
            Direction.WEST,
            pt_east,
            step_size,
            valid_interval,
            sample_size,
            data_mono,
        )

    return found_points


def compute_samples_flooded(
    selected_point, background_points, tol, bg_pts, sample_size, image: AstroImage
):
    found_points = np.array([selected_point], dtype=int)

    selected_point[0] = int(selected_point[0])
    selected_point[1] = int(selected_point[1])

    # Convert to mono
    data_mono = np.copy(image.img_display)
    if data_mono.shape[-1] == 3:
        data_mono = rgb2gray(data_mono)
    else:
        data_mono = data_mono[:, :, 0]

    step_size = int(data_mono.shape[1] / bg_pts)
    range = np.max(data_mono) - np.min(data_mono)

    selected_median = data_mono[int(selected_point[1]), int(selected_point[0])]
    range_lower = selected_median - range * ((tol + 2) / 12) / 2
    range_upper = selected_median + range * ((tol + 2) / 12) / 2

    valid_interval = (range_lower, range_upper)

    found_points = collect_points(
        found_points,
        None,
        selected_point,
        step_size,
        valid_interval,
        sample_size,
        data_mono,
    )

    if background_points is None or len(background_points) == 0:
        return np.copy(found_points)

    confirmed_points = np.array([selected_point], dtype=int)

    background_tree = KDTree(background_points)

    for f in found_points:
        f_neighbors = background_tree.query_ball_point(f, step_size * 2)
        overlaps = False
        for n_idx in f_neighbors:
            if overlap(background_points[n_idx], f, sample_size):
                overlaps = True
        if not overlaps:
            confirmed_points = np.append(confirmed_points, [f], axis=0)

    return confirmed_points
