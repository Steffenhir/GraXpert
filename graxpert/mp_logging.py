import logging
import logging.handlers
import multiprocessing
import os
import sys
import threading

from appdirs import user_log_dir


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ""
        self.line_complete = False

    def write(self, buf):
        self.linebuf += buf
        if self.linebuf.count("\n") > 0:
            self.line_complete = True
            self.flush()

    def flush(self):
        if self.line_complete:
            for s in self.linebuf.splitlines():
                self.logger.log(self.log_level, s.rstrip())
            self.linebuf = ""
            self.line_complete = False


# cf. https://docs.python.org/3/howto/logging-cookbook.html#using-concurrent-futures-processpoolexecutor

logging_queue = None
logfile_name = os.path.join(user_log_dir(appname="GraXpert"), "graxpert.log")


def get_logging_queue():
    global logging_queue
    if logging_queue is None:
        logging_queue = multiprocessing.Manager().Queue(-1)
    return logging_queue


def configure_logging():
    os.makedirs(os.path.dirname(logfile_name), exist_ok=True)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    h = logging.handlers.RotatingFileHandler(logfile_name, "a", maxBytes=1000000, backupCount=5, encoding="utf-8")
    f = logging.Formatter("%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s")
    h.setFormatter(f)
    root.handlers = []
    root.addHandler(h)

    h2 = logging.StreamHandler()
    h2.setFormatter(f)
    root.addHandler(h2)

    # stdout_logger = logging.getLogger("STDOUT")
    sl = StreamToLogger(root, logging.INFO)
    sys.stdout = sl

    # stderr_logger = logging.getLogger("STDERR")
    sl = StreamToLogger(root, logging.ERROR)
    sys.stderr = sl


def worker_configurer(queue):
    h = logging.handlers.QueueHandler(queue)  # Just the one handler needed
    root = logging.getLogger()
    root.addHandler(h)
    # send all messages, for demo; no other level or filter logic applied.
    root.setLevel(logging.INFO)


def logger_thread(queue):
    while True:
        record = queue.get()
        if record is None:
            break
        logger = logging.getLogger(record.name)
        logger.handle(record)


def initialize_logging():
    logging_thread = threading.Thread(target=logger_thread, args=(get_logging_queue(),), daemon=True)
    logging_thread.start()
    return logging_thread


def shutdown_logging(logging_thread):
    get_logging_queue().put(None)
    logging_thread.join()
