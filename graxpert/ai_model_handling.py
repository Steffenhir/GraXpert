import logging
import os
import re
import shutil
import zipfile

import onnxruntime as ort
from appdirs import user_data_dir
from minio import Minio
from packaging import version

try:
    from graxpert.s3_secrets import endpoint, ro_access_key, ro_secret_key

    client = Minio(endpoint, ro_access_key, ro_secret_key)
except Exception as e:
    logging.exception(e)
    client = None

from graxpert.ui.loadingframe import DynamicProgressThread

ai_models_dir = os.path.join(user_data_dir(appname="GraXpert"), "ai-models")
bge_ai_models_dir = os.path.join(user_data_dir(appname="GraXpert"), "bge-ai-models")

# old ai-models folder exists, rename to 'bge-ai-models'
if os.path.exists(ai_models_dir):
    logging.warning(f"Older 'ai_models_dir' {ai_models_dir} exists. Renaming to {bge_ai_models_dir} due to introduction of new denoising models in GraXpert 3.")
    try:
        os.rename(ai_models_dir, bge_ai_models_dir)
    except Exception as e:
        logging.error(f"Renaming {ai_models_dir} to {bge_ai_models_dir} failed. {bge_ai_models_dir} will be newly created. Consider deleting obsolete {ai_models_dir} manually.")

os.makedirs(bge_ai_models_dir, exist_ok=True)

deconvolution_object_ai_models_dir = os.path.join(user_data_dir(appname="GraXpert"), "deconvolution-object-ai-models")
os.makedirs(deconvolution_object_ai_models_dir, exist_ok=True)
deconvolution_stars_ai_models_dir = os.path.join(user_data_dir(appname="GraXpert"), "deconvolution-stars-ai-models")
os.makedirs(deconvolution_stars_ai_models_dir, exist_ok=True)
denoise_ai_models_dir = os.path.join(user_data_dir(appname="GraXpert"), "denoise-ai-models")
os.makedirs(denoise_ai_models_dir, exist_ok=True)


# ui operations
def list_remote_versions(bucket_name):
    if client is None:
        return []
    try:
        objects = client.list_objects(bucket_name)
        versions = []

        for o in objects:
            tags = client.get_object_tags(o.bucket_name, o.object_name)
            if tags is not None and "ai-version" in tags:
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


def list_local_versions(ai_models_dir):
    try:
        model_dirs = [
            {"path": os.path.join(ai_models_dir, f), "version": f}
            for f in os.listdir(ai_models_dir)
            if re.search(r"\d\.\d\.\d", f) and len(os.listdir(os.path.join(ai_models_dir, f))) > 0  # match semantic version
        ]
        return model_dirs
    except Exception as e:
        logging.exception(e)
        return None


def latest_version(ai_models_dir, bucket_name):
    try:
        remote_versions = list_remote_versions(bucket_name)
    except Exception as e:
        remote_versions = []
        logging.exception(e)
    try:
        local_versions = list_local_versions(ai_models_dir)
    except Exception as e:
        local_versions = []
        logging.exception(e)
    ai_options = set([])
    ai_options.update([rv["version"] for rv in remote_versions])
    ai_options.update(set([lv["version"] for lv in local_versions]))
    ai_options = sorted(ai_options, key=lambda k: version.parse(k), reverse=True)
    return ai_options[0]


def ai_model_path_from_version(ai_models_dir, local_version):
    if local_version is None:
        return None

    return os.path.join(ai_models_dir, local_version, "model.onnx")


def compute_orphaned_local_versions(ai_models_dir):
    remote_versions = list_remote_versions(ai_models_dir)

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


def download_version(ai_models_dir, bucket_name, target_version, progress=None):
    try:
        remote_versions = list_remote_versions(bucket_name)
        for r in remote_versions:
            if target_version == r["version"]:
                remote_version = r
                break

        ai_model_dir = os.path.join(ai_models_dir, "{}".format(remote_version["version"]))
        os.makedirs(ai_model_dir, exist_ok=True)

        ai_model_file = os.path.join(ai_model_dir, "model.onnx")
        ai_model_zip = os.path.join(ai_model_dir, "model.zip")
        client.fget_object(
            remote_version["bucket"],
            remote_version["object"],
            ai_model_zip,
            progress=DynamicProgressThread(callback=progress),
        )

        with zipfile.ZipFile(ai_model_zip, "r") as zip_ref:
            zip_ref.extractall(ai_model_dir)

        if not os.path.isfile(ai_model_file):
            raise ValueError(f"Could not find ai 'model.onnx' file after extracting {ai_model_zip}")
        os.remove(ai_model_zip)

    except Exception as e:
        # try to delete (rollback) ai_model_dir in case of errors
        logging.exception(e)
        try:
            shutil.rmtree(ai_model_dir)
        except Exception as e2:
            logging.exception(e2)


def validate_local_version(ai_models_dir, local_version):
    return os.path.isfile(os.path.join(ai_models_dir, local_version, "model.onnx"))


def get_execution_providers_ordered(gpu_acceleration=True):

    if gpu_acceleration:
        supported_providers = [
            (
                "OpenVINOExecutionProvider",
                {
                    "device_type": "GPU",
                },
            ),
            "ROCMExecutionProvider",
            "DmlExecutionProvider",
            (
                "CoreMLExecutionProvider",
                {
                    "flags": "COREML_FLAG_CREATE_MLPROGRAM",
                },
            ),
            "CUDAExecutionProvider",
            "CPUExecutionProvider",
        ]
    else:
        supported_providers = ["CPUExecutionProvider"]

    result = []
    available = ort.get_available_providers()
    for provider in supported_providers:
        if isinstance(provider, tuple):
            if provider[0] in available:
                result.append(provider)  # Append the entire tuple
        else:
            if provider in available:
                result.append(provider)
    return result

def fallback_run(ai_path: str, ai_gpu_acceleration: bool, inputs: dict):
    """
    Fallback function to run inference with ONNX Runtime session.
    This is useful when if the session.run() method fails due to driver/install problems with GPU acceleration..

    If a failure happens, all GPU providers are blacklisted for the remainder of this run and a warning is logged.
    We fallback to the guaranteed safe CPUExecutionProvider.
    """
    if not hasattr(fallback_run, "blacklisted"):
        fallback_run.blacklisted = False

    if fallback_run.blacklisted:
        # If we fail once, we assume all other GPU invocations will also fail for the remainder of the session
        ai_gpu_acceleration = False

    providers = get_execution_providers_ordered(ai_gpu_acceleration)
    session = ort.InferenceSession(ai_path, providers=providers)

    logging.info(f"Available inference providers : {providers}")
    logging.info(f"Used inference providers : {session.get_providers()}")

    try:
        return session.run(None, inputs)
    except Exception as e:
        if not fallback_run.blacklisted:
            logging.warning(f"Critical error with AI provider, falling back to CPU implementation: {e}")
            fallback_run.blacklisted = True
            return fallback_run(ai_path, ai_gpu_acceleration, inputs)  # Retry with CPU provider
        else: 
            logging.error(f"Critical error with CPU AI provider: {e}")
            raise e