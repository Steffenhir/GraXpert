from enum import Enum


class FitsKeys(Enum):
    BG_EXTR = "Application used for Background Extraction"
    GXSTRETCH = "Applied stretch value, Application GraXpert"
    GXINTOPT = "BGE interpolation type, GraXpert"
    GXSMOOTH = "BGE smoothing value, GraXpert"
    GXCORRT = "BGE correction type, GraXpert"
    GXBGEAIV = "BGE ai version, GraXpert"
    GXSAMPSZ = "Sample points size, GraXpert"
    GXRBFK = "RBF kernel type, GraXpert"
    GXSPLORD = "BGE spline order, GraXpert"
    GXBGPTS = "Sample points coordinates, GraXpert"
