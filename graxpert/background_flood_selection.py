import logging
from concurrent.futures.process import _ResultItem

import numpy as np
from scipy.spatial import KDTree
from skimage.color import rgb2gray

from graxpert.astroimage import AstroImage
from graxpert.grid_utils import find_darkest_quadrant


def idx_to_coords(idx, dist):
    return int(idx[0] * dist + dist / 2), int(idx[1] * dist + dist / 2)


def candidate_visited(candidate_idx, found_row_segments):

    for segment in found_row_segments:
        if (
            candidate_idx[1] == segment["y"]
            and segment["xl"] <= candidate_idx[0]
            and candidate_idx[0] <= segment["xr"]
        ):
            return True

    return False


def candidate_valid(
    candidate_idx,
    width,
    height,
    dist,
    selected_median,
    tol,
    mad,
    data_mono_padded,
    halfsize,
):
    x_pt, y_pt = idx_to_coords(candidate_idx, dist)

    if x_pt < 0 or x_pt >= width or y_pt < 0 or y_pt >= height:
        return False

    pt, local_median = find_darkest_quadrant(x_pt, y_pt, data_mono_padded, halfsize)

    if (selected_median - tol * mad / 10) <= local_median and local_median <= (selected_median + tol * mad / 10):
        return True

    return False


def overlap(p1, p2, sample_size):

    if abs(p1[0] - p2[0]) <= sample_size * 2 and abs(p1[1] - p2[1]) <= sample_size * 2:
        return True
    return False


def background_flood_selection(
    selected_point,
    current_background_points,
    tol,
    bg_pts,
    sample_size,
    image: AstroImage,
):
    # Convert to mono
    data_mono = np.copy(image.img_display)
    if data_mono.shape[-1] == 3:
        data_mono = rgb2gray(data_mono)

    global_median = np.median(data_mono)

    grid_pts = []
    dist = data_mono.shape[1] / bg_pts

    # Create grid
    x_start = int(0.5 * dist)
    y_start = int(0.5 * (data_mono.shape[0] % dist))
    x = x_start
    y = y_start

    while y < data_mono.shape[0]:
        x = x_start
        while x < data_mono.shape[1]:
            grid_pts.append([y, x])
            x = int(x + dist)
        y = int(y + dist)

    # Calculate median around each grid point
    local_median = np.zeros(len(grid_pts))
    halfsize = sample_size
    data_mono_padded = np.pad(array=data_mono, pad_width=(halfsize,), mode="reflect")

    r = range(len(grid_pts))
    for i in r:
        x_pt = grid_pts[i][0]
        y_pt = grid_pts[i][1]

        pt, median = find_darkest_quadrant(x_pt, y_pt, data_mono_padded, halfsize)

        grid_pts[i][0] = pt[0]
        grid_pts[i][1] = pt[1]
        local_median[i] = median

    # Calculate median average deviation
    mad = np.median(np.abs(local_median - global_median))

    pt, candidate_median = find_darkest_quadrant(
        int(selected_point[0]), int(selected_point[1]), data_mono_padded, sample_size
    )

    width = image.width
    height = image.height

    # distance between grid points
    dist = width / bg_pts

    # first candidate row index
    x_candidate_idx = int(((selected_point[0] - x_start) / dist))
    y_candidate_idx = int(((selected_point[1] - y_start) / dist))

    # stack that contains candidate bg_point indices
    candidate_idxs = [
        [x_candidate_idx + 1, y_candidate_idx + 1],
        [x_candidate_idx, y_candidate_idx + 1],
        [x_candidate_idx + 1, y_candidate_idx],
        [x_candidate_idx, y_candidate_idx],
    ]

    # list of valid row segments
    found_row_segments = []

    # step 1: compute row segments with valid bg_point indices
    # valid means: bg_point is in tolerance and in image bounds
    # row segments are computed by scanning each grid line to left and right, starting from the manually selected point as reference
    # candidate bg_point indices are stored on a stack

    while candidate_idxs:

        candidate_idx = candidate_idxs.pop()

        if candidate_visited(candidate_idx, found_row_segments):
            logging.debug("candidate_valid")
            continue

        if not candidate_valid(
            candidate_idx,
            width,
            height,
            dist,
            candidate_median,
            tol,
            mad,
            data_mono_padded,
            halfsize,
        ):
            logging.debug("candidate_valid")
            continue

        row_segment = {
            "xl": candidate_idx[0],
            "xr": candidate_idx[0],
            "y": candidate_idx[1],
        }

        next_candidate_idx = [candidate_idx[0] - 1, candidate_idx[1]]
        while candidate_valid(
            next_candidate_idx,
            width,
            height,
            dist,
            candidate_median,
            tol,
            mad,
            data_mono_padded,
            halfsize,
        ):
            row_segment["xl"] = next_candidate_idx[0]
            candidate_idxs.append([next_candidate_idx[0], next_candidate_idx[1] - 1])
            candidate_idxs.append([next_candidate_idx[0], next_candidate_idx[1] + 1])
            next_candidate_idx = [next_candidate_idx[0] - 1, next_candidate_idx[1]]

        next_candidate_idx = [candidate_idx[0] + 1, candidate_idx[1]]
        while candidate_valid(
            next_candidate_idx,
            width,
            height,
            dist,
            candidate_median,
            tol,
            mad,
            data_mono_padded,
            halfsize,
        ):
            row_segment["xr"] = next_candidate_idx[0]
            candidate_idxs.append([next_candidate_idx[0], next_candidate_idx[1] - 1])
            candidate_idxs.append([next_candidate_idx[0], next_candidate_idx[1] + 1])
            next_candidate_idx = [next_candidate_idx[0] + 1, next_candidate_idx[1]]

        found_row_segments.append(row_segment)

    # step 2: compute actual points from found row segments

    found_points = [selected_point]

    for segment in found_row_segments:
        y_idx = segment["y"]
        for x_idx in range(segment["xl"], segment["xr"] + 1):
            x, y = idx_to_coords([x_idx, y_idx], dist)
            pt, median = find_darkest_quadrant(x, y, data_mono_padded, sample_size)
            found_points.append([pt[0], pt[1], 1])

    # step 3: check for and eliminate duplicates

    if current_background_points is None or len(current_background_points) == 0:
        result = []
        for p in found_points:
            result.append(np.array(p, dtype=int))
        return result

    confirmed_points = []

    background_tree = KDTree(current_background_points)

    for f in found_points:
        f_neighbors = background_tree.query_ball_point(f, dist * 2)
        overlaps = False
        for n_idx in f_neighbors:
            if overlap(current_background_points[n_idx], f, sample_size):
                overlaps = True
        if not overlaps:
            confirmed_points.append(f)
    
    result = []
    for p in confirmed_points:
        result.append(np.array(p, dtype=int))
    
    return result
