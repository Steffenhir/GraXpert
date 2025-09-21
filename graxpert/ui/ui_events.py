from enum import Enum, auto


class UiEvents(Enum):
    # main ui requests
    RESET_ZOOM_REQUEST = auto()
    # menu requests
    SHOW_MENU_REQUEST = auto()
    # crop
    TURN_ON_CROP_MODE = auto()
    TURN_OFF_CROP_MODE = auto()
    APPLY_CROP_REQUEST = auto()
    # right sidebar requests
    HELP_FRAME_TOGGLED = auto()
    ADVANCED_FRAME_TOGGLED = auto()
    # mouse events
    MOUSE_MOVED = auto()
    # cosmetics
    DISPLAY_START_BADGE_REQUEST = auto()
