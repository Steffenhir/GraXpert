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

try:
    from graxpert.s3_secrets import bucket_name, endpoint, ro_access_key, ro_secret_key
    client = Minio(endpoint, ro_access_key, ro_secret_key)
except Exception as e:
    logging.exception(e)
    client = None

from graxpert.ui.loadingframe import DynamicProgressThread

ai_models_dir = os.path.join(user_data_dir(appname="GraXpert"), "ai-models")
os.makedirs(ai_models_dir, exist_ok=True)

# ui operations
def list_remote_versions():
    if client is None:
        return []
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
    finally:
        return versions


def list_local_versions():
    try:
        model_dirs = [{"path": os.path.join(ai_models_dir, f), "version": f} for f in os.listdir(ai_models_dir) if re.search(r"\d\.\d\.\d", f)]  # match semantic version
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
        logging.warning("Could not fetch remote versions. Thus, aborting cleaning of local versions in {}. Consider manual cleaning".format(ai_models_dir))
        return

    local_versions = list_local_versions()

    if local_versions is None:
        logging.warning("Could not read local versions in {}. Thus, aborting cleaning. Consider manual cleaning".format(ai_models_dir))
        return

    orphaned_local_versions = [{"path": lv["path"], "version": lv["version"]} for lv in local_versions if lv["version"] not in [rv["version"] for rv in remote_versions]]

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

        ai_model_dir = os.path.join(ai_models_dir, "{}".format(remote_version["version"]))
        os.makedirs(ai_model_dir, exist_ok=True)

        ai_model_file = os.path.join(ai_model_dir, "{}.zip".format(remote_version["version"]))
        client.fget_object(
            remote_version["bucket"],
            remote_version["object"],
            ai_model_file,
            progress=DynamicProgressThread(callback=progress),
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
