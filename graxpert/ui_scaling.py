import sys

from screeninfo import get_monitors

scaling_factor = None


def get_scaling_factor(master):
    global scaling_factor

    if scaling_factor is not None:
        return scaling_factor

    try:
        monitors = get_monitors()
        primary_monitor = next(mon for mon in monitors if mon.is_primary)
        dpi = primary_monitor.width / (master.winfo_screenmmwidth() / 24.0)
        scaling_factor = dpi / 72.0
    except AttributeError as e:
        print("WARNING: could not calculate monitor dpi, ", e)
        scaling_factor = 1.0

    return scaling_factor
