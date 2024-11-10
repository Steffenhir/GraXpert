from enum import Enum, auto


class AppEvents(Enum):
    # image loading
    OPEN_FILE_DIALOG_REQUEST = auto()
    LOAD_IMAGE_REQUEST = auto()
    LOAD_IMAGE_BEGIN = auto()
    LOAD_IMAGE_END = auto()
    LOAD_IMAGE_ERROR = auto()
    # image stretching
    STRETCH_IMAGE_BEGIN = auto()
    STRETCH_IMAGE_END = auto()
    STRETCH_IMAGE_ERROR = auto()
    # image saturation
    CHANGE_SATURATION_REQUEST = auto()
    CHANGE_SATURATION_BEGIN = auto()
    CHANGE_SATURATION_END = auto()
    # image display
    UPDATE_DISPLAY_TYPE_REEQUEST = auto()
    DISPLAY_TYPE_CHANGED = auto()
    REDRAW_POINTS_REQUEST = auto()
    # stretch options
    STRETCH_OPTION_CHANGED = auto()
    CHANNELS_LINKED_CHANGED = auto()
    # sample selection
    DISPLAY_PTS_CHANGED = auto()
    BG_FLOOD_SELECTION_CHANGED = auto()
    BG_PTS_CHANGED = auto()
    BG_TOL_CHANGED = auto()
    CREATE_GRID_REQUEST = auto()
    CREATE_GRID_BEGIN = auto()
    CREATE_GRID_END = auto()
    RESET_POITS_REQUEST = auto()
    RESET_POITS_BEGIN = auto()
    RESET_POITS_END = auto()
    # calculation
    INTERPOL_TYPE_CHANGED = auto()
    SMOTTHING_CHANGED = auto()
    CALCULATE_REQUEST = auto()
    CALCULATE_BEGIN = auto()
    CALCULATE_PROGRESS = auto()
    CALCULATE_END = auto()
    CALCULATE_SUCCESS = auto()
    CALCULATE_ERROR = auto()
    # deconvolution
    DECONVOLUTION_TYPE_CHANGED = auto()
    DECONVOLUTION_STRENGTH_CHANGED = auto()
    DECONVOLUTION_PSFSIZE_CHANGED = auto()
    DECONVOLUTION_OPERATION_CHANGED = auto()
    DECONVOLUTION_REQUEST = auto()
    DECONVOLUTION_BEGIN = auto()
    DECONVOLUTION_PROGRESS = auto()
    DECONVOLUTION_END = auto()
    DECONVOLUTION_SUCCESS = auto()
    DECONVOLUTION_ERROR = auto()
    # denoising
    DENOISE_STRENGTH_CHANGED = auto()
    DENOISE_THRESHOLD_CHANGED = auto()
    DENOISE_REQUEST = auto()
    DENOISE_BEGIN = auto()
    DENOISE_PROGRESS = auto()
    DENOISE_END = auto()
    DENOISE_SUCCESS = auto()
    DENOISE_ERROR = auto()
    # saving
    SAVE_AS_CHANGED = auto()
    SAVE_STRETCHED_CHANGED = auto()
    SAVE_REQUEST = auto()
    SAVE_BEGIN = auto()
    SAVE_END = auto()
    SAVE_ERROR = auto()
    # ai model handling
    AI_DOWNLOAD_BEGIN = auto()
    AI_DOWNLOAD_PROGRESS = auto()
    AI_DOWNLOAD_END = auto()
    AI_DOWNLOAD_ERROR = auto()
    # bge ai model handling
    BGE_AI_VERSION_CHANGED = auto()
    # denoise ai model handling
    DECONVOLUTION_OBJECT_AI_VERSION_CHANGED = auto()
    DECONVOLUTION_STARS_AI_VERSION_CHANGED = auto()
    # denoise ai model handling
    DENOISE_AI_VERSION_CHANGED = auto()
    # advanced settings
    SAMPLE_SIZE_CHANGED = auto()
    SAMPLE_COLOR_CHANGED = auto()
    RBF_KERNEL_CHANGED = auto()
    SPLINE_ORDER_CHANGED = auto()
    CORRECTION_TYPE_CHANGED = auto()
    LANGUAGE_CHANGED = auto()
    SCALING_CHANGED = auto()
    AI_BATCH_SIZE_CHANGED = auto()
    AI_GPU_ACCELERATION_CHANGED = auto()
    # process control
    CANCEL_PROCESSING = auto()
