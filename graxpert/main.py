import os
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

from graxpert.ai_model_handling import list_local_versions, list_remote_versions
from graxpert.mp_logging import configure_logging

available_local_versions = []
available_remote_versions = []


def collect_available_version():
    global available_local_versions
    global available_remote_versions

    try:
        available_local_versions = sorted(
            [v["version"] for v in list_local_versions()],
            key=lambda k: version.parse(k),
            reverse=True,
        )
    except Exception as e:
        available_local_versions = ""
        logging.exception(e)
    try:
        available_remote_versions = sorted(
            [v["version"] for v in list_remote_versions()],
            key=lambda k: version.parse(k),
            reverse=True,
        )
    except Exception as e:
        available_remote_versions = ""
        logging.exception(e)


def version_type(arg_value, pat=re.compile(r"^\d+\.\d+\.\d+$")):
    global available_local_versions
    global available_remote_versions

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


def ui_main():
    import tkinter as tk

    from appdirs import user_config_dir
    from customtkinter import CTk

    from graxpert.application.app import graxpert
    from graxpert.application.eventbus import eventbus
    from graxpert.mp_logging import initialize_logging, shutdown_logging
    from graxpert.parallel_processing import executor
    from graxpert.preferences import app_state_2_prefs, save_preferences
    from graxpert.resource_utils import resource_path
    from graxpert.ui.application_frame import ApplicationFrame
    from graxpert.ui.styling import style
    from graxpert.ui.ui_events import UiEvents
    from graxpert.version import check_for_new_version, release, version

    def on_closing(root, logging_thread):
        graxpert.prefs = app_state_2_prefs(graxpert.prefs, graxpert.cmd.app_state, graxpert)

        prefs_filename = os.path.join(user_config_dir(appname="GraXpert"), "preferences.json")
        save_preferences(prefs_filename, graxpert.prefs)
        try:
            executor.shutdown(cancel_futures=True)
        except Exception as e:
            logging.exception("error shutting down ProcessPoolExecutor")
        shutdown_logging(logging_thread)
        root.destroy()
        logging.shutdown()
        sys.exit(0)

    logging_thread = initialize_logging()
    check_for_new_version()

    root = CTk()
    try:
        root.state("zoomed")
    except:
        root.state("normal")
    style(root)
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
    eventbus.emit(UiEvents.DISPLAY_START_BADGE_REQUEST)
    root.mainloop()


def main():
    if len(sys.argv) > 1:
        global available_local_versions
        global available_remote_versions

        collect_available_version()

        parser = argparse.ArgumentParser(description="GraXpert,the astronomical background extraction tool")
        parser.add_argument("filename", type=str, help="Path of the unprocessed image")
        parser.add_argument(
            "-ai_version",
            "--ai_version",
            nargs="?",
            required=False,
            default=None,
            type=version_type,
            help='Version of the AI model, default: "latest"; available locally: [{}], available remotely: [{}]'.format(", ".join(available_local_versions), ", ".join(available_remote_versions)),
        )
        parser.add_argument("-correction", "--correction", nargs="?", required=False, default="Subtraction", choices=["Subtraction", "Division"], type=str, help="Subtraction or Division")
        parser.add_argument("-smoothing", "--smoothing", nargs="?", required=False, default=0.0, type=float, help="Strength of smoothing between 0 and 1")

        args = parser.parse_args()

        from graxpert.CommandLineTool import CommandLineTool

        clt = CommandLineTool(args)
        clt.execute()
        logging.shutdown()
    else:
        ui_main()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    configure_logging()
    main()
    logging.shutdown()
