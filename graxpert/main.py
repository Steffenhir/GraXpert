import os
import sys

# ensure sys.stdout and sys.stderr are not None in PyInstaller environments
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

from graxpert.mp_logging import configure_logging
configure_logging()

import argparse
import multiprocessing
import sys


def main():
    if (len(sys.argv) > 1):
        parser = argparse.ArgumentParser(description="GraXpert,the astronomical background extraction tool")
        parser.add_argument("filename", type = str, help = "Path of the unprocessed image")
        parser.add_argument("-ai_directory", "--ai_directory", nargs="?", required = False, default = None, type = str, help = "Path of the AI model")
        parser.add_argument('-correction', '--correction', nargs="?", required = False, default = "Subtraction", choices = ["Subtraction","Division"], type = str, help = "Subtraction or Division")
        parser.add_argument('-smoothing', '--smoothing', nargs="?", required = False, default = 0.0, type = float, help = "Strength of smoothing between 0 and 1")
        
        args = parser.parse_args()
        
        from graxpert.CommandLineTool import CommandLineTool
        clt = CommandLineTool(args)
        clt.execute()
    else:
        import graxpert.gui


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
