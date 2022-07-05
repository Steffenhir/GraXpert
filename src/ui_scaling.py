from screeninfo import get_monitors
from platform import system

scaling_factor = None


def get_scaling_factor(master):
    global scaling_factor

    if scaling_factor is not None:
        return scaling_factor

    try:
        monitors = get_monitors()

        monitor = None
        if len(monitors) == 1:
            # use the only available monitor
            monitor = monitors[0]
        else:
            try:
                # try to query the primary monitor...
                monitor = next(mon for mon in monitors if mon.is_primary)
            except:
                # ... if that fails try the first one in the list
                monitor = monitors[0]
        
        dpi = monitor.width / (monitor.width_mm / 25.4)
        scaling_factor = dpi / 96.0
        
    except BaseException as e:
        print("WARNING: could not calculate monitor dpi:", e)
        scaling_factor = 1.0

    return scaling_factor
