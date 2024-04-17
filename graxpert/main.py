import os
import platform
import sys

# ensure sys.stdout and sys.stderr are not None in PyInstaller environments
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")
import argparse
import logging
import multiprocessing
import re
import sys

from packaging import version

from graxpert.ai_model_handling import bge_ai_models_dir, denoise_ai_models_dir, list_local_versions, list_remote_versions
from graxpert.mp_logging import configure_logging
from graxpert.s3_secrets import bge_bucket_name, denoise_bucket_name
from graxpert.version import release as graxpert_release
from graxpert.version import version as graxpert_version


def collect_available_versions(ai_models_dir, bucket_name):

    try:
        available_local_versions = sorted(
            [v["version"] for v in list_local_versions(ai_models_dir)],
            key=lambda k: version.parse(k),
            reverse=True,
        )
    except Exception as e:
        available_local_versions = ""
        logging.exception(e)
    try:
        available_remote_versions = sorted(
            [v["version"] for v in list_remote_versions(bucket_name)],
            key=lambda k: version.parse(k),
            reverse=True,
        )
    except Exception as e:
        available_remote_versions = ""
        logging.exception(e)

    return (available_local_versions, available_remote_versions)


def bge_version_type(arg_value, pat=re.compile(r"^\d+\.\d+\.\d+$")):
    return version_type(bge_ai_models_dir, bge_bucket_name, arg_value, pat=re.compile(r"^\d+\.\d+\.\d+$"))


def version_type(ai_models_dir, bucket_name, arg_value, pat=re.compile(r"^\d+\.\d+\.\d+$")):

    available_versions = collect_available_versions(ai_models_dir, bucket_name)
    available_local_versions = available_versions[0]
    available_remote_versions = available_versions[1]

    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError("invalid version, expected format: n.n.n")
    if arg_value not in available_local_versions and arg_value not in available_remote_versions:
        raise argparse.ArgumentTypeError(
            "provided version neither found locally or remotely; available locally: [{}], available remotely: [{}]".format(
                ", ".join(available_local_versions),
                ", ".join(available_remote_versions),
            )
        )
    if not available_local_versions and not available_remote_versions:
        raise argparse.ArgumentTypeError("no AI versions available locally or remotely")
    return arg_value


def ui_main(open_with_file=None):
    import logging
    import tkinter as tk
    from concurrent.futures import ProcessPoolExecutor
    from datetime import datetime
    from inspect import signature
    from tkinter import messagebox

    import requests
    from appdirs import user_config_dir
    from customtkinter import CTk

    from graxpert.application.app import graxpert
    from graxpert.application.app_events import AppEvents
    from graxpert.application.eventbus import eventbus
    from graxpert.localization import _
    from graxpert.mp_logging import initialize_logging, shutdown_logging
    from graxpert.parallel_processing import executor
    from graxpert.preferences import app_state_2_prefs, save_preferences
    from graxpert.resource_utils import resource_path
    from graxpert.ui.application_frame import ApplicationFrame
    from graxpert.ui.styling import style
    from graxpert.ui.ui_events import UiEvents
    from graxpert.version import release, version

    def on_closing(root: CTk, logging_thread):
        app_state_2_prefs(graxpert.prefs, graxpert.cmd.app_state)

        prefs_filename = os.path.join(user_config_dir(appname="GraXpert"), "preferences.json")
        save_preferences(prefs_filename, graxpert.prefs)
        try:
            if "cancel_futures" in signature(ProcessPoolExecutor.shutdown).parameters:
                executor.shutdown(cancel_futures=True)  # Python > 3.8
            else:
                executor.shutdown()  # Python <= 3.8

        except Exception as e:
            logging.exception("error shutting down ProcessPoolExecutor")
        shutdown_logging(logging_thread)
        root.destroy()
        logging.shutdown()
        sys.exit(0)

    def check_for_new_version():
        try:
            response = requests.get("https://api.github.com/repos/Steffenhir/GraXpert/releases/latest", timeout=2.5)
            latest_release_date = datetime.strptime(response.json()["created_at"], "%Y-%m-%dT%H:%M:%SZ")

            response_current = requests.get("https://api.github.com/repos/Steffenhir/GraXpert/releases/tags/" + version, timeout=2.5)
            current_release_date = datetime.strptime(response_current.json()["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            current_is_beta = response_current.json()["prerelease"]

            if current_is_beta:
                if current_release_date >= latest_release_date:
                    messagebox.showinfo(
                        title=_("This is a Beta release!"), message=_("Please note that this is a Beta release of GraXpert. You will be notified when a newer official version is available.")
                    )
                else:
                    messagebox.showinfo(
                        title=_("New official release available!"),
                        message=_("This Beta version is deprecated. A newer official release of GraXpert is available at") + " https://github.com/Steffenhir/GraXpert/releases/latest",
                    )

            elif latest_release_date > current_release_date:
                messagebox.showinfo(title=_("New version available!"), message=_("A newer version of GraXpert is available at") + " https://github.com/Steffenhir/GraXpert/releases/latest")
        except:
            logging.warning("Could not check for newest version")

    logging_thread = initialize_logging()

    style()
    root = CTk()

    try:
        if "Linux" == platform.system():
            root.attributes("-zoomed", True)
        else:
            root.state("zoomed")
    except Exception as e:
        root.state("normal")
        logging.warning(e, stack_info=True)

    root.title("GraXpert | Release: '{}' ({})".format(release, version))
    root.iconbitmap()
    root.iconphoto(True, tk.PhotoImage(file=resource_path("img/Icon.png")))
    # root.option_add("*TkFDialog*foreground", "black")
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, logging_thread))
    root.createcommand("::tk::mac::Quit", lambda: on_closing(root, logging_thread))
    root.minsize(width=800, height=600)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    app = ApplicationFrame(root)
    app.grid(column=0, row=0, sticky=tk.NSEW)
    root.update()
    check_for_new_version()

    if open_with_file and len(open_with_file) > 0:
        eventbus.emit(AppEvents.LOAD_IMAGE_REQUEST, {"filename": open_with_file})
    else:
        eventbus.emit(UiEvents.DISPLAY_START_BADGE_REQUEST)

    root.mainloop()


def main():
    if len(sys.argv) > 1:

        available_bge_versions = collect_available_versions(bge_ai_models_dir, bge_bucket_name)
        available_denoise_versions = collect_available_versions(denoise_ai_models_dir, denoise_bucket_name)

        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("-cli", "--cli", required=False, action="store_true", help="Has to be added when using the command line integration of GraXpert")
        parser.add_argument(
            "-cmd",
            "--command",
            required=False,
            default="background-extraction",
            choices=["background-extraction", "denoising"],
            type=str,
            help="Choose the image operation to execute: Background Extraction or Denoising",
        )
        parser.add_argument("filename", type=str, help="Path of the unprocessed image")
        parser.add_argument("-output", "--output", nargs="?", required=False, type=str, help="Filename of the processed image")
        parser.add_argument(
            "-preferences_file",
            "--preferences_file",
            nargs="?",
            required=False,
            default=None,
            type=str,
            help="Allows GraXpert commandline to run all extraction methods based on a preferences file that contains background grid points",
        )
        parser.add_argument("-v", "--version", action="version", version=f"GraXpert version: {graxpert_version} release: {graxpert_release}")

        bge_parser = argparse.ArgumentParser("GraXpert Background Extraction", parents=[parser], description="GraXpert, the astronomical background extraction tool")
        bge_parser.add_argument(
            "-ai_version",
            "--ai_version",
            nargs="?",
            required=False,
            default=None,
            type=bge_version_type,
            help='Version of the Background Extraction AI model, default: "latest"; available locally: [{}], available remotely: [{}]'.format(
                ", ".join(available_bge_versions[0]), ", ".join(available_bge_versions[1])
            ),
        )
        bge_parser.add_argument("-correction", "--correction", nargs="?", required=False, default=None, choices=["Subtraction", "Division"], type=str, help="Subtraction or Division")
        bge_parser.add_argument("-smoothing", "--smoothing", nargs="?", required=False, default=None, type=float, help="Strength of smoothing between 0 and 1")
        bge_parser.add_argument("-bg", "--bg", required=False, action="store_true", help="Also save the background model")

        denoise_parser = argparse.ArgumentParser("GraXpert Denoising", parents=[parser], description="GraXpert, the astronomical denoising tool")
        denoise_parser.add_argument(
            "-ai_version",
            "--ai_version",
            nargs="?",
            required=False,
            default=None,
            type=bge_version_type,
            help='Version of the Denoising AI model, default: "latest"; available locally: [{}], available remotely: [{}]'.format(
                ", ".join(available_denoise_versions[0]), ", ".join(available_denoise_versions[1])
            ),
        )
        denoise_parser.add_argument(
            "-strength",
            "--denoise_strength",
            nargs="?",
            required=False,
            default=None,
            type=float,
            help='Strength of the desired denoising effect, default: "1.0"',
        )
        denoise_parser.add_argument(
            "-batch_size",
            "--ai_batch_size",
            nargs="?",
            required=False,
            default=None,
            type=int,
            help='Number of image tiles which Graxpert will denoise in parallel. Be careful: increasing this value might result in out-of-memory errors. Valid Range: 1..50, default: "3"',
        )

        if "-h" in sys.argv or "--help" in sys.argv:
            if "denoising" in sys.argv:
                denoise_parser.print_help()
            else:
                bge_parser.print_help()
            sys.exit(0)

        args, extras = parser.parse_known_args()

        if args.command == "background-extraction":
            args = bge_parser.parse_args()
        else:
            args = denoise_parser.parse_args()

        if args.cli and args.command == "background-extraction":
            from graxpert.cmdline_tools import BGECmdlineTool

            logging.info(f"Starting GraXpert CLI, Background-Extraction, version: {graxpert_version} release: {graxpert_release}")
            clt = BGECmdlineTool(args)
            clt.execute()
            logging.shutdown()
        elif args.cli and args.command == "denoising":
            from graxpert.cmdline_tools import DenoiseCmdlineTool

            logging.info(f"Starting GraXpert CLI, Denoising, version: {graxpert_version} release: {graxpert_release}")
            clt = DenoiseCmdlineTool(args)
            clt.execute()
            logging.shutdown()
        else:
            logging.info(f"Starting GraXpert UI, version: {graxpert_version} release: {graxpert_release}")
            ui_main(args.filename)

    else:
        ui_main()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    configure_logging()
    main()
    logging.shutdown()
