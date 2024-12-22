import logging
import os
import tkinter as tk
from tkinter import messagebox

import numpy as np
from appdirs import user_config_dir

from graxpert.ai_model_handling import (
    ai_model_path_from_version,
    bge_ai_models_dir,
    deconvolution_object_ai_models_dir,
    deconvolution_stars_ai_models_dir,
    denoise_ai_models_dir,
    download_version,
    validate_local_version,
)
from graxpert.app_state import INITIAL_STATE
from graxpert.application.app_events import AppEvents
from graxpert.application.eventbus import eventbus
from graxpert.astroimage import AstroImage
from graxpert.AstroImageRepository import AstroImageRepository, ImageTypes
from graxpert.background_extraction import extract_background
from graxpert.commands import INIT_HANDLER, RESET_POINTS_HANDLER, RM_POINT_HANDLER, SEL_POINTS_HANDLER, Command
from graxpert.deconvolution import deconvolve
from graxpert.denoising import denoise
from graxpert.localization import _
from graxpert.mp_logging import logfile_name
from graxpert.preferences import fitsheader_2_app_state, load_preferences, prefs_2_app_state
from graxpert.s3_secrets import bge_bucket_name, deconvolution_object_bucket_name, deconvolution_stars_bucket_name, denoise_bucket_name
from graxpert.stretch import StretchParameters, stretch_all
from graxpert.ui.loadingframe import DynamicProgressThread


class GraXpert:

    def __init__(self):
        self.initialize()

    def initialize(self):
        # app preferences
        prefs_filename = os.path.join(user_config_dir(appname="GraXpert"), "preferences.json")
        self.prefs = load_preferences(prefs_filename)

        self.filename = ""
        self.data_type = ""

        self.images = AstroImageRepository()
        self.display_type = ImageTypes.Original

        self.mat_affine = np.eye(3)

        # state handling
        tmp_state = prefs_2_app_state(self.prefs, INITIAL_STATE)

        self.cmd: Command = Command(INIT_HANDLER, background_points=tmp_state.background_points)
        self.cmd.execute()

        # image loading
        eventbus.add_listener(AppEvents.OPEN_FILE_DIALOG_REQUEST, self.on_open_file_dialog_request)
        eventbus.add_listener(AppEvents.LOAD_IMAGE_REQUEST, self.on_load_image)
        # image display
        eventbus.add_listener(AppEvents.DISPLAY_TYPE_CHANGED, self.on_display_type_changed)
        # stretch options
        eventbus.add_listener(AppEvents.STRETCH_OPTION_CHANGED, self.on_stretch_option_changed)
        eventbus.add_listener(AppEvents.CHANGE_SATURATION_REQUEST, self.on_change_saturation_request)
        eventbus.add_listener(AppEvents.CHANNELS_LINKED_CHANGED, self.on_channels_linked_option_changed)
        # sample selection
        eventbus.add_listener(AppEvents.DISPLAY_PTS_CHANGED, self.on_display_pts_changed)
        eventbus.add_listener(AppEvents.BG_FLOOD_SELECTION_CHANGED, self.on_bg_floot_selection_changed)
        eventbus.add_listener(AppEvents.BG_PTS_CHANGED, self.on_bg_pts_changed)
        eventbus.add_listener(AppEvents.BG_TOL_CHANGED, self.on_bg_tol_changed)
        eventbus.add_listener(AppEvents.CREATE_GRID_REQUEST, self.on_create_grid_request)
        eventbus.add_listener(AppEvents.RESET_POITS_REQUEST, self.on_reset_points_request)
        # calculation
        eventbus.add_listener(AppEvents.INTERPOL_TYPE_CHANGED, self.on_interpol_type_changed)
        eventbus.add_listener(AppEvents.SMOTTHING_CHANGED, self.on_smoothing_changed)
        eventbus.add_listener(AppEvents.CALCULATE_REQUEST, self.on_calculate_request)
        # deconvolution
        eventbus.add_listener(AppEvents.DECONVOLUTION_TYPE_CHANGED, self.on_deconvolution_type_changed)
        eventbus.add_listener(AppEvents.DECONVOLUTION_STRENGTH_CHANGED, self.on_deconvolution_strength_changed)
        eventbus.add_listener(AppEvents.DECONVOLUTION_PSFSIZE_CHANGED, self.on_deconvolution_psfsize_changed)
        eventbus.add_listener(AppEvents.DECONVOLUTION_REQUEST, self.on_deconvolution_request)
        # denoising
        eventbus.add_listener(AppEvents.DENOISE_STRENGTH_CHANGED, self.on_denoise_strength_changed)
        eventbus.add_listener(AppEvents.DENOISE_REQUEST, self.on_denoise_request)
        # saving
        eventbus.add_listener(AppEvents.SAVE_AS_CHANGED, self.on_save_as_changed)
        eventbus.add_listener(AppEvents.SAVE_STRETCHED_CHANGED, self.on_save_stretched_changed)
        eventbus.add_listener(AppEvents.SAVE_REQUEST, self.on_save_request)
        # advanced settings
        eventbus.add_listener(AppEvents.SAMPLE_SIZE_CHANGED, self.on_sample_size_changed)
        eventbus.add_listener(AppEvents.SAMPLE_COLOR_CHANGED, self.on_sample_color_changed)
        eventbus.add_listener(AppEvents.RBF_KERNEL_CHANGED, self.on_rbf_kernel_changed)
        eventbus.add_listener(AppEvents.SPLINE_ORDER_CHANGED, self.on_spline_order_changed)
        eventbus.add_listener(AppEvents.CORRECTION_TYPE_CHANGED, self.on_correction_type_changed)
        eventbus.add_listener(AppEvents.LANGUAGE_CHANGED, self.on_language_selected)
        eventbus.add_listener(AppEvents.BGE_AI_VERSION_CHANGED, self.on_bge_ai_version_changed)
        eventbus.add_listener(AppEvents.DECONVOLUTION_OBJECT_AI_VERSION_CHANGED, self.on_deconvolution_object_ai_version_changed)
        eventbus.add_listener(AppEvents.DECONVOLUTION_STARS_AI_VERSION_CHANGED, self.on_deconvolution_stars_ai_version_changed)
        eventbus.add_listener(AppEvents.DENOISE_AI_VERSION_CHANGED, self.on_denoise_ai_version_changed)
        eventbus.add_listener(AppEvents.SCALING_CHANGED, self.on_scaling_changed)
        eventbus.add_listener(AppEvents.AI_BATCH_SIZE_CHANGED, self.on_ai_batch_size_changed)
        eventbus.add_listener(AppEvents.AI_GPU_ACCELERATION_CHANGED, self.on_ai_gpu_acceleration_changed)

    # event handling
    def on_ai_batch_size_changed(self, event):
        self.prefs.ai_batch_size = event["ai_batch_size"]

    def on_ai_gpu_acceleration_changed(self, event):
        self.prefs.ai_gpu_acceleration = event["ai_gpu_acceleration"]

    def on_bge_ai_version_changed(self, event):
        self.prefs.bge_ai_version = event["bge_ai_version"]

    def on_bg_floot_selection_changed(self, event):
        self.prefs.bg_flood_selection_option = event["bg_flood_selection_option"]

    def on_bg_pts_changed(self, event):
        self.prefs.bg_pts_option = event["bg_pts_option"]

    def on_bg_tol_changed(self, event):
        self.prefs.bg_tol_option = event["bg_tol_option"]

    def on_calculate_request(self, event=None):
        if self.images.get(ImageTypes.Original) is None:
            messagebox.showerror("Error", _("Please load your picture first."))
            return

        background_points = self.cmd.app_state.background_points

        # Error messages if not enough points
        if len(background_points) == 0 and self.prefs.interpol_type_option != "AI":
            messagebox.showerror("Error", _("Please select background points with left click."))
            return

        if len(background_points) < 2 and self.prefs.interpol_type_option == "Kriging":
            messagebox.showerror("Error", _("Please select at least 2 background points with left click for the Kriging method."))
            return

        if len(background_points) < 16 and self.prefs.interpol_type_option == "Splines":
            messagebox.showerror("Error", _("Please select at least 16 background points with left click for the Splines method."))
            return

        if self.prefs.interpol_type_option == "AI":
            if not self.validate_bge_ai_installation():
                return

        eventbus.emit(AppEvents.CALCULATE_BEGIN)

        progress = DynamicProgressThread(callback=lambda p: eventbus.emit(AppEvents.CALCULATE_PROGRESS, {"progress": p}))

        downscale_factor = 1

        if self.prefs.interpol_type_option == "Kriging" or self.prefs.interpol_type_option == "RBF":
            downscale_factor = 4

        try:
            self.prefs.images_linked_option = False

            img_array_to_be_processed = np.copy(self.images.get(ImageTypes.Original).img_array)

            background = AstroImage()
            background.set_from_array(
                extract_background(
                    img_array_to_be_processed,
                    np.array(background_points),
                    self.prefs.interpol_type_option,
                    self.prefs.smoothing_option,
                    downscale_factor,
                    self.prefs.sample_size,
                    self.prefs.RBF_kernel,
                    self.prefs.spline_order,
                    self.prefs.corr_type,
                    ai_model_path_from_version(bge_ai_models_dir, self.prefs.bge_ai_version),
                    progress,
                    self.prefs.ai_gpu_acceleration,
                )
            )

            gradient_corrected = AstroImage()
            gradient_corrected.set_from_array(img_array_to_be_processed)

            # Update fits header and metadata
            background_mean = np.mean(background.img_array)
            gradient_corrected.update_fits_header(self.images.get(ImageTypes.Original).fits_header, background_mean, self.prefs, self.cmd.app_state)
            gradient_corrected.update_fits_header(self.images.get(ImageTypes.Original).fits_header, background_mean, self.prefs, self.cmd.app_state)

            gradient_corrected.copy_metadata(self.images.get(ImageTypes.Original))
            background.copy_metadata(self.images.get(ImageTypes.Original))

            self.images.set(ImageTypes.Gradient_Corrected, gradient_corrected)
            self.images.set(ImageTypes.Background, background)

            self.images.stretch_all(StretchParameters(self.prefs.stretch_option, self.prefs.channels_linked_option), self.prefs.saturation)

            eventbus.emit(AppEvents.CALCULATE_SUCCESS)
            eventbus.emit(AppEvents.UPDATE_DISPLAY_TYPE_REEQUEST, {"display_type": "Gradient-Corrected"})

        except Exception as e:
            logging.exception(e)
            eventbus.emit(AppEvents.CALCULATE_ERROR)
            messagebox.showerror("Error", _("An error occured during background calculation. Please see the log at {}.".format(logfile_name)))
        finally:
            progress.done_progress()
            eventbus.emit(AppEvents.CALCULATE_END)

    def on_change_saturation_request(self, event):
        if self.images.get(ImageTypes.Original) is None:
            return

        self.prefs.saturation = event["saturation"]

        eventbus.emit(AppEvents.CHANGE_SATURATION_BEGIN)

        self.images.update_saturation(self.prefs.saturation)

        eventbus.emit(AppEvents.CHANGE_SATURATION_END)

    def on_correction_type_changed(self, event):
        self.prefs.corr_type = event["corr_type"]

    def on_create_grid_request(self, event=None):
        if self.images.get(ImageTypes.Original) is None:
            messagebox.showerror("Error", _("Please load your picture first."))
            return

        eventbus.emit(AppEvents.CREATE_GRID_BEGIN)

        self.cmd = Command(
            SEL_POINTS_HANDLER, self.cmd, data=self.images.get(ImageTypes.Original).img_array, num_pts=self.prefs.bg_pts_option, tol=self.prefs.bg_tol_option, sample_size=self.prefs.sample_size
        )
        self.cmd.execute()

        eventbus.emit(AppEvents.CREATE_GRID_END)

    def on_deconvolution_type_changed(self, event):
        self.prefs.deconvolution_type_option = event["deconvolution_type_option"]

    def on_deconvolution_strength_changed(self, event):
        self.prefs.deconvolution_strength = event["deconvolution_strength"]

    def on_deconvolution_psfsize_changed(self, event):
        self.prefs.deconvolution_psfsize = event["deconvolution_psfsize"]

    def on_deconvolution_object_ai_version_changed(self, event):
        self.prefs.deconvolution_object_ai_version = event["deconvolution_object_ai_version"]

    def on_deconvolution_stars_ai_version_changed(self, event):
        self.prefs.deconvolution_stars_ai_version = event["deconvolution_stars_ai_version"]

    def on_deconvolution_request(self, event):
        if self.images.get(ImageTypes.Original) is None:
            messagebox.showerror("Error", _("Please load your picture first."))
            return

        if not self.validate_deconvolution_ai_installation():
            return

        eventbus.emit(AppEvents.DECONVOLUTION_BEGIN)

        progress = DynamicProgressThread(callback=lambda p: eventbus.emit(AppEvents.DECONVOLUTION_PROGRESS, {"progress": p}))

        deconvolution_type_option = self.prefs.deconvolution_type_option

        try:
            img_array_to_be_processed = np.copy(self.images.get(ImageTypes.Original).img_array)
            if self.images.get(ImageTypes.Gradient_Corrected) is not None:
                img_array_to_be_processed = np.copy(self.images.get(ImageTypes.Gradient_Corrected).img_array)

            self.prefs.images_linked_option = True

            if deconvolution_type_option == "Object-only":
                ai_model_path = ai_model_path_from_version(deconvolution_object_ai_models_dir, self.prefs.deconvolution_object_ai_version)
            else:
                ai_model_path = ai_model_path_from_version(deconvolution_stars_ai_models_dir, self.prefs.deconvolution_stars_ai_version)
            imarray = deconvolve(
                img_array_to_be_processed,
                ai_model_path,
                self.prefs.deconvolution_strength,
                self.prefs.deconvolution_psfsize,
                batch_size=self.prefs.ai_batch_size,
                progress=progress,
                ai_gpu_acceleration=self.prefs.ai_gpu_acceleration,
            )

            if imarray is not None:

                deconvolved = AstroImage()
                deconvolved.set_from_array(imarray)

                # Update fits header and metadata
                background_mean = np.mean(self.images.get(ImageTypes.Original).img_array)
                deconvolved.update_fits_header(self.images.get(ImageTypes.Original).fits_header, background_mean, self.prefs, self.cmd.app_state)

                deconvolved.copy_metadata(self.images.get(ImageTypes.Original))

                self.images.set(f"Deconvolved {deconvolution_type_option}", deconvolved)

                self.images.stretch_all(StretchParameters(self.prefs.stretch_option, self.prefs.channels_linked_option, self.prefs.images_linked_option), self.prefs.saturation)

                eventbus.emit(AppEvents.DECONVOLUTION_SUCCESS, {"deconvolution_type_option": f"Deconvolved {deconvolution_type_option}"})
                eventbus.emit(AppEvents.UPDATE_DISPLAY_TYPE_REEQUEST, {"display_type": f"Deconvolved {deconvolution_type_option}"})

        except Exception as e:
            logging.exception(e)
            eventbus.emit(AppEvents.DECONVOLUTION_ERROR)
            messagebox.showerror("Error", _("An error occured during deconvolution. Please see the log at {}.".format(logfile_name)))
        finally:
            progress.done_progress()
            eventbus.emit(AppEvents.DECONVOLUTION_END)

    def on_denoise_ai_version_changed(self, event):
        self.prefs.denoise_ai_version = event["denoise_ai_version"]

    def on_display_pts_changed(self, event):
        self.prefs.display_pts = event["display_pts"]
        eventbus.emit(AppEvents.REDRAW_POINTS_REQUEST)

    def on_display_type_changed(self, event):
        self.display_type = event["display_type"]

        eventbus.emit(AppEvents.STRETCH_IMAGE_END)

    def on_interpol_type_changed(self, event):
        self.prefs.interpol_type_option = event["interpol_type_option"]

    def on_language_selected(self, event):
        self.prefs.lang = event["lang"]
        messagebox.showerror("", _("Please restart the program to change the language."))

    def on_load_image(self, event):
        eventbus.emit(AppEvents.LOAD_IMAGE_BEGIN)
        filename = event["filename"]
        self.display_type = ImageTypes.Original

        try:
            image = AstroImage()
            image.set_from_file(filename, StretchParameters(self.prefs.stretch_option, self.prefs.channels_linked_option), self.prefs.saturation)

        except Exception as e:
            eventbus.emit(AppEvents.LOAD_IMAGE_ERROR)
            msg = _("An error occurred while loading your picture.")
            logging.exception(msg)
            messagebox.showerror("Error", _(msg))
            return

        self.filename = os.path.splitext(os.path.basename(filename))[0]

        self.data_type = os.path.splitext(filename)[1]
        self.images.reset()
        self.images.set(ImageTypes.Original, image)
        self.prefs.working_dir = os.path.dirname(filename)

        os.chdir(os.path.dirname(filename))

        width = self.images.get(ImageTypes.Original).img_display.width
        height = self.images.get(ImageTypes.Original).img_display.height

        if self.prefs.width != width or self.prefs.height != height:
            self.reset_backgroundpts()

        self.prefs.width = width
        self.prefs.height = height

        tmp_state = fitsheader_2_app_state(self, self.cmd.app_state, self.images.get(ImageTypes.Original).fits_header)
        self.cmd: Command = Command(INIT_HANDLER, background_points=tmp_state.background_points)
        self.cmd.execute()

        eventbus.emit(AppEvents.LOAD_IMAGE_END, {"filename": filename})

    def on_open_file_dialog_request(self, evet):
        if self.prefs.working_dir != "" and os.path.exists(self.prefs.working_dir):
            initialdir = self.prefs.working_dir
        else:
            initialdir = os.getcwd()

        filename = tk.filedialog.askopenfilename(
            filetypes=[
                ("Image file", ".bmp .png .jpg .jpeg .tif .tiff .fit .fits .fts .xisf"),
                ("Bitmap", ".bmp"),
                ("PNG", ".png"),
                ("JPEG", ".jpg .jpeg"),
                ("Tiff", ".tif .tiff"),
                ("Fits", ".fit .fits .fts"),
                ("XISF", ".xisf"),
            ],
            initialdir=initialdir,
        )

        if filename == "":
            return

        eventbus.emit(AppEvents.LOAD_IMAGE_REQUEST, {"filename": filename})

    def on_rbf_kernel_changed(self, event):
        self.prefs.RBF_kernel = event["RBF_kernel"]

    def on_reset_points_request(self, event):
        eventbus.emit(AppEvents.RESET_POITS_BEGIN)

        if len(self.cmd.app_state.background_points) > 0:
            self.cmd = Command(RESET_POINTS_HANDLER, self.cmd)
            self.cmd.execute()

        eventbus.emit(AppEvents.RESET_POITS_END)

    def on_sample_color_changed(self, event):
        self.prefs.sample_color = event["sample_color"]
        eventbus.emit(AppEvents.REDRAW_POINTS_REQUEST)

    def on_sample_size_changed(self, event):
        self.prefs.sample_size = event["sample_size"]
        eventbus.emit(AppEvents.REDRAW_POINTS_REQUEST)

    def on_save_as_changed(self, event):
        self.prefs.saveas_option = event["saveas_option"]

    def on_save_stretched_changed(self, event):
        self.prefs.saveas_stretched = event["saveas_stretched"]

    def on_smoothing_changed(self, event):
        self.prefs.smoothing_option = event["smoothing_option"]

    def on_denoise_strength_changed(self, event):
        self.prefs.denoise_strength = event["denoise_strength"]

    def on_denoise_request(self, event):
        if self.images.get(ImageTypes.Original) is None:
            messagebox.showerror("Error", _("Please load your picture first."))
            return

        if not self.validate_denoise_ai_installation():
            return

        eventbus.emit(AppEvents.DENOISE_BEGIN)

        progress = DynamicProgressThread(callback=lambda p: eventbus.emit(AppEvents.DENOISE_PROGRESS, {"progress": p}))

        try:

            if self.images.get(ImageTypes.Deconvolved_Object_only) is not None:
                img_array_to_be_processed = np.copy(self.images.get(ImageTypes.Deconvolved_Object_only).img_array)
            elif self.images.get(ImageTypes.Gradient_Corrected) is not None:
                img_array_to_be_processed = np.copy(self.images.get(ImageTypes.Gradient_Corrected).img_array)
            else:
                img_array_to_be_processed = np.copy(self.images.get(ImageTypes.Original).img_array)

            self.prefs.images_linked_option = True
            ai_model_path = ai_model_path_from_version(denoise_ai_models_dir, self.prefs.denoise_ai_version)
            imarray = denoise(
                img_array_to_be_processed,
                ai_model_path,
                self.prefs.denoise_strength,
                batch_size=self.prefs.ai_batch_size,
                progress=progress,
                ai_gpu_acceleration=self.prefs.ai_gpu_acceleration,
            )

            if imarray is not None:

                denoised = AstroImage()
                denoised.set_from_array(imarray)

                # Update fits header and metadata
                background_mean = np.mean(self.images.get(ImageTypes.Original).img_array)
                denoised.update_fits_header(self.images.get(ImageTypes.Original).fits_header, background_mean, self.prefs, self.cmd.app_state)

                denoised.copy_metadata(self.images.get(ImageTypes.Original))

                self.images.set(ImageTypes.Denoised, denoised)

                self.images.stretch_all(StretchParameters(self.prefs.stretch_option, self.prefs.channels_linked_option, self.prefs.images_linked_option), self.prefs.saturation)

                eventbus.emit(AppEvents.DENOISE_SUCCESS)
                eventbus.emit(AppEvents.UPDATE_DISPLAY_TYPE_REEQUEST, {"display_type": "Denoised"})

        except Exception as e:
            logging.exception(e)
            eventbus.emit(AppEvents.DENOISE_ERROR)
            messagebox.showerror("Error", _("An error occured during denoising. Please see the log at {}.".format(logfile_name)))
        finally:
            progress.done_progress()
            eventbus.emit(AppEvents.DENOISE_END)

    def on_save_request(self, event):

        suffix_1 = "_graxpert"

        match self.display_type:
            case ImageTypes.Gradient_Corrected:
                suffix_2 = "_bge"
            case ImageTypes.Background:
                suffix_2 = "_background"
            case ImageTypes.Deconvolved_Object_only:
                suffix_2 = "_obj_decon"
            case ImageTypes.Deconvolved_Stars_only:
                suffix_2 = "_stars_decon"
            case ImageTypes.Denoised:
                suffix_2 = "_denoised"
            case _:
                suffix_2 = ""

        match self.prefs.saveas_stretched:
            case True:
                suffix_3 = "_stretched"
            case _:
                suffix_3 = ""

        if self.prefs.saveas_option == "16 bit Tiff" or self.prefs.saveas_option == "32 bit Tiff":
            dir = tk.filedialog.asksaveasfilename(
                initialfile=self.filename + f"{suffix_1}{suffix_2}{suffix_3}.tiff", filetypes=[("Tiff", ".tiff")], defaultextension=".tiff", initialdir=self.prefs.working_dir
            )
        elif self.prefs.saveas_option == "16 bit XISF" or self.prefs.saveas_option == "32 bit XISF":
            dir = tk.filedialog.asksaveasfilename(
                initialfile=self.filename + f"{suffix_1}{suffix_2}{suffix_3}.xisf", filetypes=[("XISF", ".xisf")], defaultextension=".xisf", initialdir=self.prefs.working_dir
            )
        else:
            dir = tk.filedialog.asksaveasfilename(
                initialfile=self.filename + f"{suffix_1}{suffix_2}{suffix_3}.fits", filetypes=[("Fits", ".fits")], defaultextension=".fits", initialdir=self.prefs.working_dir
            )

        if dir == "":
            return

        eventbus.emit(AppEvents.SAVE_BEGIN)

        try:
            if self.prefs.saveas_stretched:
                self.images.get(self.display_type).save_stretched(dir, self.prefs.saveas_option, StretchParameters(self.prefs.stretch_option, self.prefs.channels_linked_option))
            else:
                self.images.get(self.display_type).save(dir, self.prefs.saveas_option)

        except Exception as e:
            logging.exception(e)
            eventbus.emit(AppEvents.SAVE_ERROR)
            messagebox.showerror("Error", _("Error occured when saving the image."))

        eventbus.emit(AppEvents.SAVE_END)

    def on_scaling_changed(self, event):
        self.prefs.scaling = event["scaling"]

    def on_spline_order_changed(self, event):
        self.prefs.spline_order = event["spline_order"]

    def on_stretch_option_changed(self, event):
        self.prefs.stretch_option = event["stretch_option"]
        self.do_stretch()

    def on_channels_linked_option_changed(self, event):
        self.prefs.channels_linked_option = event["channels_linked"]
        self.do_stretch()

    # application logic
    def do_stretch(self):
        eventbus.emit(AppEvents.STRETCH_IMAGE_BEGIN)

        try:
            self.images.stretch_all(StretchParameters(self.prefs.stretch_option, self.prefs.channels_linked_option, self.prefs.images_linked_option), self.prefs.saturation)
        except Exception as e:
            eventbus.emit(AppEvents.STRETCH_IMAGE_ERROR)
            logging.exception(e)

        eventbus.emit(AppEvents.STRETCH_IMAGE_END)

    def remove_pt(self, event):
        if len(self.cmd.app_state.background_points) == 0 or not self.prefs.display_pts:
            return False

        point_im = self.to_image_point(event.x, event.y)
        if len(point_im) == 0:
            return False

        eventx_im = point_im[0]
        eventy_im = point_im[1]

        background_points = self.cmd.app_state.background_points

        min_idx = -1
        min_dist = -1

        for i in range(len(background_points)):
            x_im = background_points[i][0]
            y_im = background_points[i][1]

            dist = np.max(np.abs([x_im - eventx_im, y_im - eventy_im]))

            if min_idx == -1 or dist < min_dist:
                min_dist = dist
                min_idx = i

        if min_idx != -1 and min_dist <= self.prefs.sample_size:
            point = background_points[min_idx]
            self.cmd = Command(RM_POINT_HANDLER, self.cmd, idx=min_idx, point=point)
            self.cmd.execute()
            return True
        else:
            return False

    def reset_backgroundpts(self):
        if len(self.cmd.app_state.background_points) > 0:
            self.cmd = Command(RESET_POINTS_HANDLER, self.cmd)
            self.cmd.execute()

    def reset_transform(self):
        self.mat_affine = np.eye(3)

    def scale_at(self, scale: float, cx: float, cy: float):
        self.translate(-cx, -cy)
        self.scale(scale)
        self.translate(cx, cy)

    def scale(self, scale: float):
        mat = np.eye(3)
        mat[0, 0] = scale
        mat[1, 1] = scale
        self.mat_affine = np.dot(mat, self.mat_affine)

    def to_canvas_point(self, x, y):
        return np.dot(self.mat_affine, (x, y, 1.0))

    def to_image_point(self, x, y):
        if self.images.get(self.display_type) is None:
            return []

        mat_inv = np.linalg.inv(self.mat_affine)
        image_point = np.dot(mat_inv, (x, y, 1.0))

        width = self.images.get(self.display_type).width
        height = self.images.get(self.display_type).height

        if image_point[0] < 0 or image_point[1] < 0 or image_point[0] > width or image_point[1] > height:
            return []

        return image_point

    def to_image_point_pinned(self, x, y):
        if self.images.get(self.display_type) is None:
            return []

        mat_inv = np.linalg.inv(self.mat_affine)
        image_point = np.dot(mat_inv, (x, y, 1.0))

        width = self.images.get(self.display_type).width
        height = self.images.get(self.display_type).height

        if image_point[0] < 0:
            image_point[0] = 0
        if image_point[1] < 0:
            image_point[1] = 0
        if image_point[0] > width:
            image_point[0] = width
        if image_point[1] > height:
            image_point[1] = height

        return image_point

    def translate(self, offset_x, offset_y):
        mat = np.eye(3)
        mat[0, 2] = float(offset_x)
        mat[1, 2] = float(offset_y)

        self.mat_affine = np.dot(mat, self.mat_affine)

    def validate_bge_ai_installation(self):
        if self.prefs.bge_ai_version is None or self.prefs.bge_ai_version == "None":
            messagebox.showerror("Error", _("No Background Extraction AI-Model selected. Please select one from the Advanced panel on the right."))
            return False

        if not validate_local_version(bge_ai_models_dir, self.prefs.bge_ai_version):
            if not messagebox.askyesno(_("Install AI-Model?"), _("Selected Background Extraction AI-Model is not installed. Should I download it now?")):
                return False
            else:
                eventbus.emit(AppEvents.AI_DOWNLOAD_BEGIN)

                def callback(p):
                    eventbus.emit(AppEvents.AI_DOWNLOAD_PROGRESS, {"progress": p})

                download_version(bge_ai_models_dir, bge_bucket_name, self.prefs.bge_ai_version, progress=callback)
                eventbus.emit(AppEvents.AI_DOWNLOAD_END)
        return True

    def validate_deconvolution_ai_installation(self):

        if self.prefs.deconvolution_type_option == "Object-only":

            if self.prefs.deconvolution_object_ai_version is None or self.prefs.deconvolution_object_ai_version == "None":
                messagebox.showerror("Error", _("No Object-only Deconvolution AI-Model selected. Please select one from the Advanced panel on the right."))
                return False

            if not validate_local_version(deconvolution_object_ai_models_dir, self.prefs.deconvolution_object_ai_version):
                if not messagebox.askyesno(_("Install AI-Model?"), _("Selected Object-only Deconvolution AI-Model is not installed. Should I download it now?")):
                    return False
                else:
                    eventbus.emit(AppEvents.AI_DOWNLOAD_BEGIN)

                    def callback(p):
                        eventbus.emit(AppEvents.AI_DOWNLOAD_PROGRESS, {"progress": p})

                    download_version(deconvolution_object_ai_models_dir, deconvolution_object_bucket_name, self.prefs.deconvolution_object_ai_version, progress=callback)
                    eventbus.emit(AppEvents.AI_DOWNLOAD_END)
            return True
        else:
            if self.prefs.deconvolution_stars_ai_version is None or self.prefs.deconvolution_stars_ai_version == "None":
                messagebox.showerror("Error", _("No Stars-only Denoising AI-Model selected. Please select one from the Advanced panel on the right."))
                return False

            if not validate_local_version(deconvolution_stars_ai_models_dir, self.prefs.deconvolution_stars_ai_version):
                if not messagebox.askyesno(_("Install AI-Model?"), _("Selected Stars-only Deconvolution AI-Model is not installed. Should I download it now?")):
                    return False
                else:
                    eventbus.emit(AppEvents.AI_DOWNLOAD_BEGIN)

                    def callback(p):
                        eventbus.emit(AppEvents.AI_DOWNLOAD_PROGRESS, {"progress": p})

                    download_version(deconvolution_stars_ai_models_dir, deconvolution_stars_bucket_name, self.prefs.deconvolution_stars_ai_version, progress=callback)
                    eventbus.emit(AppEvents.AI_DOWNLOAD_END)
            return True

    def validate_denoise_ai_installation(self):
        if self.prefs.denoise_ai_version is None or self.prefs.denoise_ai_version == "None":
            messagebox.showerror("Error", _("No Denoising AI-Model selected. Please select one from the Advanced panel on the right."))
            return False

        if not validate_local_version(denoise_ai_models_dir, self.prefs.denoise_ai_version):
            if not messagebox.askyesno(_("Install AI-Model?"), _("Selected Denoising AI-Model is not installed. Should I download it now?")):
                return False
            else:
                eventbus.emit(AppEvents.AI_DOWNLOAD_BEGIN)

                def callback(p):
                    eventbus.emit(AppEvents.AI_DOWNLOAD_PROGRESS, {"progress": p})

                download_version(denoise_ai_models_dir, denoise_bucket_name, self.prefs.denoise_ai_version, progress=callback)
                eventbus.emit(AppEvents.AI_DOWNLOAD_END)
        return True


graxpert = GraXpert()
