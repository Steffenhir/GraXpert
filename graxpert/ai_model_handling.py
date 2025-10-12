import logging
import os
import sys
import re
import shutil
import zipfile
from multiprocessing import Process, Queue

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
                    # per https://onnxruntime.ai/docs/execution-providers/OpenVINO-ExecutionProvider.html#summary-of-options
                    # "device_type": "HETERO:GPU,CPU,NPU AUTO:GPU,CPU,NPU MULTI:GPU,CPU,NPU", # Will prefer dGPU, fallback to iGPU, NPU or CPU with extra Intel specific optimizations
                    "device_type": "AUTO:GPU,CPU", # Will prefer dGPU, fallback to iGPU, NPU or CPU with extra Intel specific optimizations
                }
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
    try:
        import onnxruntime as ort    
        available = ort.get_available_providers()
        for provider in supported_providers:
            if isinstance(provider, tuple):
                if provider[0] in available:
                    result.append(provider)  # Append the entire tuple
            else:
                if provider in available:
                    result.append(provider)
        return result
    except Exception as e:
        logging.error("Critical error!  The required ONNX Runtime (AI library) package is misconfigured.\n" \
        "Please read the README.md to confirm that you've selected the correct build for your hardware.\n" \
        "If you are using one of our prebuilt executables, please file a bug with the following information:\n"
        "{}".format(e))
        sys.exit(1)


def run_in_process(fn: callable):
    """Run a function in a separate process and return the result or raise an exception."""

    q = Queue()

    # Create a closure to call fn and put the result in the queue    
    def wrapped():
        try:
            r = fn()
        except Exception as e:
            r = e # return the exception to the main process
        q.put(r)

    p = Process(target=wrapped, name="ai-worker")
    p.start()
    p.join()

    if p.exitcode != 0:
        raise RuntimeError(f"worker process crashed with exit code {p.exitcode}.")

    result = q.get()
    if isinstance(result, Exception):
        raise result
    return result


# Provides a mutable session context that can swap out different sessions if needed
class SessionContext:
    model_name: str
    session: any # onnxruntime.InferenceSession

    def __init__(self, model_name: str,  gpu_acceleration: bool = True):
        """Initialize the ONNX model session with the specified execution provider."""

        providers = get_execution_providers_ordered(gpu_acceleration)
        logging.info(f"Available inference providers : {providers}")

        import onnxruntime as ort # Must be after get_execution_providers_ordered (so it can check for missing libs)
        self.session = ort.InferenceSession(model_name, providers=providers)
        self.model_name = model_name

        logging.info(f"Used inference providers for {model_name}: {self.session.get_providers()}")


    def __run_low(self, model_args: dict, gpu_acceleration: bool = True) -> any:
        """Run the ONNX model using the specified execution provider."""

        # if we are using a GPU the ONNX runtimes might crash due to native bugs (ROCm)
        # so run in a separate process just in case
        fn = lambda: self.session.run(None, model_args)
        if gpu_acceleration:
            return run_in_process(fn)
        else:
            return fn()

    def run(self, model_args: dict) -> any:
        """Run the ONNX model using the specified execution provider."""

        providers = self.session.get_providers()
        gpu_acceleration = len(providers) > 1 or providers[0] != "CPUExecutionProvider"
        try:
            result = self.__run_low(model_args, gpu_acceleration)
        except Exception as e:
            if not gpu_acceleration:
                raise  # Rethrow, the failure occurred with the regular CPU model also - show error dialog

            logging.warning(f"Error running model, falling back to CPU only: {e}")
            import onnxruntime as ort
            self.session = ort.InferenceSession(self.model_name, providers=get_execution_providers_ordered(False))
            result = self.__run_low(model_args, False)

        # all graxpert results are in the first array index
        return result[0]