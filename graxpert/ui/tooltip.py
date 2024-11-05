import tkinter as tk
import tkinter.ttk as ttk

from customtkinter import CTkFrame, CTkLabel, CTkToplevel

from graxpert.application.app_events import AppEvents
from graxpert.application.eventbus import eventbus
from graxpert.localization import _
from graxpert.ui_scaling import get_scaling_factor


class Tooltip:
    """
    It creates a tooltip for a given widget as the mouse goes on it.

    see:

    http://stackoverflow.com/questions/3221956/
           what-is-the-simplest-way-to-make-tooltips-
           in-tkinter/36221216#36221216

    http://www.daniweb.com/programming/software-development/
           code/484591/a-tooltip-class-for-tkinter

    - Originally written by vegaseat on 2014.09.09.

    - Modified to include a delay time by Victor Zaccardo on 2016.03.25.

    - Modified
        - to correct extreme right and extreme bottom behavior,
        - to stay inside the screen whenever the tooltip might go out on
          the top but still the screen is higher than the tooltip,
        - to use the more flexible mouse positioning,
        - to add customizable background color, padding, waittime and
          wraplength on creation
      by Alberto Vassena on 2016.11.05.

      Tested on Ubuntu 16.04/16.10, running Python 3.5.2

    TODO: themes styles support
    """

    def __init__(self, widget, *, pad=(5, 3, 5, 3), text="widget info", waittime=500, wraplength=250):
        self.waittime = waittime  # in miliseconds, originally 500
        self.wraplength = wraplength * get_scaling_factor()  # in pixels, originally 180
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.onEnter)
        self.widget.bind("<Leave>", self.onLeave)
        self.widget.bind("<ButtonPress>", self.onLeave)
        self.pad = pad
        self.id = None
        self.tw = None
        self.enable_tt = True
        eventbus.add_listener(AppEvents.CALCULATE_REQUEST, lambda e: self.disable())
        eventbus.add_listener(AppEvents.DENOISE_REQUEST, lambda e: self.disable())
        eventbus.add_listener(AppEvents.CALCULATE_END, lambda e: self.enable())
        eventbus.add_listener(AppEvents.DENOISE_END, lambda e: self.enable())

    def onEnter(self, event=None):
        self.schedule()

    def onLeave(self, event=None):
        self.unschedule()
        self.hide()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.show)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show(self):

        if not self.enable_tt:
            return

        def tip_pos_calculator(widget, label, *, tip_delta=(10, 5), pad=(5, 3, 5, 3)):
            w = widget

            s_width, s_height = w.winfo_screenwidth(), w.winfo_screenheight()

            width, height = (pad[0] + label.winfo_reqwidth() + pad[2], pad[1] + label.winfo_reqheight() + pad[3])

            mouse_x, mouse_y = w.winfo_pointerxy()

            x1, y1 = mouse_x + tip_delta[0], mouse_y + tip_delta[1]
            x2, y2 = x1 + width, y1 + height

            x_delta = x2 - s_width
            if x_delta < 0:
                x_delta = 0
            y_delta = y2 - s_height
            if y_delta < 0:
                y_delta = 0

            offscreen = (x_delta, y_delta) != (0, 0)

            if offscreen:
                if x_delta:
                    x1 = mouse_x - tip_delta[0] - width

                if y_delta:
                    y1 = mouse_y - tip_delta[1] - height

            offscreen_again = y1 < 0  # out on the top

            if offscreen_again:
                # No further checks will be done.

                # TIP:
                # A further mod might automagically augment the
                # wraplength when the tooltip is too high to be
                # kept inside the screen.
                y1 = 0

            return x1, y1

        pad = self.pad
        widget = self.widget

        # creates a toplevel window
        self.tw = CTkToplevel(widget)

        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)

        win = CTkFrame(self.tw, border_width=0)
        label = CTkLabel(win, text=self.text, justify=tk.LEFT, wraplength=self.wraplength)

        label.grid(padx=(pad[0], pad[2]), pady=(pad[1], pad[3]), sticky=tk.NSEW)
        win.grid()

        x, y = tip_pos_calculator(widget, label)

        self.tw.wm_geometry("+%d+%d" % (x, y))

    def hide(self):
        tw = self.tw
        if tw:
            tw.destroy()
        self.tw = None

    def enable(self):
        self.enable_tt = True

    def disable(self):
        self.enable_tt = False
        self.hide()


load_text = _("Load your image you would like to correct. \n" "\n" "Supported formats: .tiff, .fits, .png, .jpg \n" "Supported bitdepths: 16 bit integer, 32 bit float")

stretch_text = _("Automatically stretch the picture to make gradients more visible. " "The saved pictures are unaffected by the stretch.")

reset_text = _("Reset all the chosen background points.")

bg_select_text = _("Creates a grid with the specified amount of points per row " "and rejects points below a threshold defined by the tolerance.")

bg_tol_text = _("The tolerance adjusts the threshold for rejection of background points " "with automatic background selection")

bg_flood_text = _("If enabled, additional grid points are automatically created based on " "1) the luminance of the sample just added and " "2) the grid tolerance slider below.")

num_points_text = _("Adjust the number of points per row for the grid created by" " automatic background selection.")

interpol_type_text = _("Choose between different interpolation methods.")

smoothing_text = _(
    "Adjust the smoothing parameter for the interpolation method. "
    "A too small smoothing parameter may lead to over- and undershooting "
    "inbetween background points, while a too large smoothing parameter "
    "may not be suited for large deviations in gradients."
)

calculate_text = _("Use the specified interpolation method to calculate a background model " "and subtract it from the picture. This may take a while.")

deconvolution_type_text = _("Choose between different deconvolution methods.")
deconvolution_text = _("Use GraXpert's deconvolution AI model to reduce the blur in your image. This may take a while")
deconvolution_strength_text = _("Determines strength of deconvolution.")
deconvolution_psfsize_text = _("Informs the AI on how much blur to expect in the image. The right parameters is found when all artifacts disappear.")

denoise_text = _("Use GraXpert's denoising AI model to reduce the noise in your image. This may take a while")
denoise_strength_text = _("Determines strength of denoising.")
denoise_threshold_text = _("Determines the upper bound up to which pixels are denoised. Pixels above this threshold are not denoised and taken from the original image.")

saveas_text = _("Choose the bitdepth of the saved pictures and the file format. " "If you are working with a .fits image the fits header will " "be preserved.")
saveas_stretched_text = _("Enable to save the stretched image instead of the linear one. The color saturation is not changed.")
save_pic_text = _("Save the currently selected picture")

display_text = _("Switch display between \n" "\n" "Original: Your original picture \n" "Processed: Picture with subtracted background model \n" "Background: The background model")
