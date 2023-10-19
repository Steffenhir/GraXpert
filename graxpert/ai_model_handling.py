import logging
import os
import re
import shutil
import zipfile
from queue import Empty, Queue
from threading import Thread

from appdirs import user_data_dir
from minio import Minio
from packaging import version

from graxpert.s3_secrets import (bucket_name, endpoint, ro_access_key,
                                 ro_secret_key)

ai_models_dir = os.path.join(user_data_dir(appname="GraXpert"), "ai-models")
os.makedirs(ai_models_dir, exist_ok=True)

client = Minio(endpoint, ro_access_key, ro_secret_key)


# ui operations
def list_remote_versions():
    try:
        objects = client.list_objects(bucket_name)
        versions = []

        for o in objects:
            tags = client.get_object_tags(o.bucket_name, o.object_name)
            if "ai-version" in tags:
                versions.append(
                    {
                        "bucket": o.bucket_name,
                        "object": o.object_name,
                        "version": tags["ai-version"],
                    }
                )
        return versions

    except Exception as e:
        logging.exception(e)
        return None


def list_local_versions():
    try:
        model_dirs = [
            {"path": os.path.join(ai_models_dir, f), "version": f}
            for f in os.listdir(ai_models_dir)
            if re.search(r"\d\.\d\.\d", f)
        ]  # match semantic version
        return model_dirs
    except Exception as e:
        logging.exception(e)
        return None


def latest_version():
    try:
        remote_versions = list_remote_versions()
    except Exception as e:
        remote_versions = []
        logging.exception(e)
    try:
        local_versions = list_local_versions()
    except Exception as e:
        local_versions = []
        logging.exception(e)
    ai_options = set([])
    ai_options.update([rv["version"] for rv in remote_versions])
    ai_options.update(set([lv["version"] for lv in local_versions]))
    ai_options = sorted(ai_options, key=lambda k: version.parse(k), reverse=True)
    return ai_options[0]


def ai_model_path_from_version(local_version):
    return os.path.join(ai_models_dir, local_version, "bg_model")


def compute_orphaned_local_versions():
    remote_versions = list_remote_versions()

    if remote_versions is None:
        logging.warning(
            "Could not fetch remote versions. Thus, aborting cleaning of local versions in {}. Consider manual cleaning".format(
                ai_models_dir
            )
        )
        return

    local_versions = list_local_versions()

    if local_versions is None:
        logging.warning(
            "Could not read local versions in {}. Thus, aborting cleaning. Consider manual cleaning".format(
                ai_models_dir
            )
        )
        return

    orphaned_local_versions = [
        {"path": lv["path"], "version": lv["version"]}
        for lv in local_versions
        if lv["version"] not in [rv["version"] for rv in remote_versions]
    ]

    return orphaned_local_versions


def cleanup_orphaned_local_versions(orphaned_local_versions):
    for olv in orphaned_local_versions:
        try:
            shutil.rmtree(olv["path"])
        except Exception as e:
            logging.exception(e)


def download_version(remote_version, progress=None):
    try:
        remote_versions = list_remote_versions()
        for r in remote_versions:
            if remote_version == r["version"]:
                remote_version = r
                break

        ai_model_dir = os.path.join(
            ai_models_dir, "{}".format(remote_version["version"])
        )
        os.makedirs(ai_model_dir, exist_ok=True)

        ai_model_file = os.path.join(
            ai_model_dir, "{}.zip".format(remote_version["version"])
        )
        client.fget_object(
            remote_version["bucket"],
            remote_version["object"],
            ai_model_file,
            progress=Progress(callback=progress),
        )

        with zipfile.ZipFile(ai_model_file, "r") as zip_ref:
            zip_ref.extractall(ai_model_dir)

        os.remove(ai_model_file)
    except Exception as e:
        # try to delete (rollback) ai_model_dir in case of errors
        logging.exception(e)
        try:
            shutil.rmtree(ai_model_dir)
        except Exception as e2:
            logging.exception(e2)


def validate_local_version(local_version):
    return os.path.isdir(os.path.join(ai_models_dir, local_version, "bg_model"))


class Progress(Thread):
    def __init__(self, interval=1, callback=None):
        Thread.__init__(self)
        self.daemon = True
        self.interval = interval
        self.callback = callback
        self.total_length = 0
        self.current_size = 0
        self.update_queue = Queue()
        self.start()

    def set_meta(self, total_length, object_name):
        """
        Metadata settings for the object. This method is called before downloading the object
        :param total_length: Total length of object.
        """
        self.total_length = total_length

    def run(self):
        while True:
            try:
                # display every interval secs
                task = self.update_queue.get(timeout=self.interval)
            except Empty:
                continue

            current_size, total_length = task
            self.update_queue.task_done()
            if current_size == total_length:
                # once we have done uploading everything return
                self.done_progress()
                return

    def update(self, size):
        """
        Update object size to be shown. This method is called while downloading
        :param size: Object size.
        """
        if not isinstance(size, int):
            raise ValueError(
                "{} type can not be displayed. "
                "Please change it to Int.".format(type(size))
            )

        self.current_size += size
        self.update_queue.put((self.current_size, self.total_length))

        if self.callback is not None:
            self.callback(self.progress())

    def done_progress(self):
        self.total_length = 0
        self.current_size = 0

    def progress(self):
        if self.total_length == 0:
            return 0
        return float(self.current_size) / float(self.total_length)
