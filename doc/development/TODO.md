# TODO

Note: this document is currently a virtually unstructured pile of notes for @geeksville's work
on graxpert.  You can probably ignore it...

# Changelist

* Intel OpenVINO AI acceleration support added by @adaloveseal (this should allow **much** faster processing on AVX2/VNNI capable Intel CPUs - including the N100/N300 CPUs often used in telescope miniPCs).  On even a low-end N300 CPU (with a crummy iGPU) my benchmark test shows it as a 5x speedup.
* GPU acceleration for AMD GPUs (a 15x speedup vs CPU processing: 15 minute runs (on a 16 core CPU) become 1 minute (using less than 1 core))
* Failures in processing using GPU acceleration automatically failback to using the CPU instead and print a warning message to the logs.
* In addition to the old package options, graxpert is now available on pypi for easy install with "pip install graxpert" on Windows, Mac-OS, or Linux.
* An AppImage build is now available for Linux (as a prelude to eventual flatpak based distribution)
* Fix a number of resource leaks while the app was running.
* Previously most failures inside of graxpert would cause the app to appear to hang.  This is now fixed, the app will exit with an exception message instead.  Please report any failures you encounter by filing a github issue at FIXME.
* The -cli command line flag is no longer required (but will be ignored if you still use it).  Just pass in command line arguments as you wish (see README.md for documentation)
* If AI models crash in GPU code (even a native crash) the app will auto-fallback to a CPU based implementation.
* MacOS CoreML acceleration is now (again) used for most models.  For the time being denoise falls back to a CPU implementation on MacOS.


# Running github actions locally

➜  gh extension install https://github.com/nektos/gh-act
✓ Installed extension https://github.com/nektos/gh-act
gh act -l pull_request
gh act push -P ubuntu-24.04=catthehacker/ubuntu:act-latest
gh act push -j build-linux-zip -P ubuntu-24.04=catthehacker/ubuntu:act-latest


# Test commands

PYTHONPATH=. python graxpert/main.py -cmd background-extraction -output /tmp/testout tests/test_images/real_crummy.fits

FIXME - follow in instructions for vc 14 runtime install, after enabling ssh
py -m pip install //host.lan/Data/dist/graxpert-3.2.0a0.dev1-py3-none-any.whl[cuda]


graxpert -cmd background-extraction -output /tmp/testout tests/test_images/real_crummy.fits

>  Please consider submitting your AppImage to AppImageHub, the crowd-sourced
central directory of available AppImages, by opening a pull request
at https://github.com/AppImage/appimage.github.io

todo add https://onnxruntime.ai/docs/execution-providers/OpenVINO-ExecutionProvider.html#requirements windows instructions
I think just:
pip install openvino==2025.3.0
but also these very painful user steps
https://docs.openvino.ai/2025/get-started/install-openvino/install-openvino-archive-windows.html


# How to run Windows in a VM

* After starting windows devcontainer install github CLI: https://cli.github.com
* install "gh extension install nektos/gh-act"

# ONNX optimizations

Possibly tune block sizes?

2025-07-28 15:28:31,227 MainProcess root INFO     Progress: 36%
2025-07-28 15:28:31,420 MainProcess root INFO     Available inference providers : ['ROCMExecutionProvider', 'CPUExecutionProvider']
2025-07-28 15:28:31,420 MainProcess root INFO     Used inference providers : ['ROCMExecutionProvider', 'CPUExecutionProvider']
MIOpen(HIP): Warning [IsEnoughWorkspace] [GetSolutionsFallback AI] Solver <GemmBwdRest>, workspace required: 67108864, provided ptr: 0x7fc959400800 size: 33554432
MIOpen(HIP): Warning [IsEnoughWorkspace] [EvaluateInvokers] Solver <GemmBwdRest>, workspace required: 67108864, provided ptr: 0x7fc959400800 size: 33554432
MIOpen(HIP): Warning [IsEnoughWorkspace] [GetSolutionsFallback AI] Solver <GemmBwdRest>, workspace required: 134217728, provided ptr: 0x7fc953400400 size: 33554432
MIOpen(HIP): Warning [IsEnoughWorkspace] [EvaluateInvokers] Solver <GemmBwdRest>, workspace required: 134217728, provided ptr: 0x7fc953400400 size: 33554432
MIOpen(HIP): Warning [IsEnoughWorkspace] [GetSolutionsFallback AI] Solver <GemmBwdRest>, workspace required: 268435456, provided ptr: 0x7fc953400000 size: 33554

I thought the problem is related to batch_size.  Trid different values as an experiment but didn't seem to change much
https://github.com/ROCm/MIOpen/issues/2981

Do incrmental tuning on model partitioning
https://github.com/ROCm/MIOpen/blob/develop/docs/conceptual/tuningdb.rst

export MIOPEN_FIND_MODE=3
export MIOPEN_FIND_ENFORCE=3
export MIOPEN_USER_DB_PATH="/workspaces/graxpert/mitune"


# version
We use PEP440 convention for versioning now



# building for pypi
python -m build

test pypi upload
python3 -m twine upload --repository testpypi dist/graxpert-3.2.0a0-py3-none-any.whl dist/graxpert-3.2.0a0.tar.gz 
python3 -m twine upload --repository testpypi dist/graxpert-3.2.0a0.dev4-py3-none-any.whl dist/graxpert-3.2.0a0.dev4.tar.gz 

test install locally
following works on fedora now if you manually install gcc.
pip install --user ~/development/telescope/graxpert/dist/graxpert-3.2.0a0.dev0-py3-none-any.whl

apt install python3-tkinter

# Installs the base application with CPU support
pip install graxpert

# Installs the base app PLUS the ROCm-specific package

sudo dnf install rocm
sudo apt install rocm-libs

pip install graxpert[openvino]
pip install graxpert[rocm]
pip install --user --break-system-packages ~/development/telescope/graxpert/dist/graxpert-3.2.0a0.dev1-py3-none-any.whl[rocm] -f https://repo.radeon.com/rocm/manylinux/rocm-rel-6.4.3/

pipx install ~/development/telescope/graxpert/dist/graxpert-3.1.0rc2.dev250919173048-py3-none-any.whl[rocm] --pip-args="-f https://repo.radeon.com/rocm/manylinux/rocm-rel-6.4.3/"

pipx install ~/development/telescope/graxpert/dist/graxpert-3.1.0rc2.dev250919182618-py3-none-any.whl[rocm] --pip-args="-f https://repo.radeon.com/rocm/manylinux/rocm-rel-7.0/"

strace -o run.strace python3 -c "import onnxruntime; print(onnxruntime.get_available_providers())"

# appimage

Size experiments

FIXME: make command line work - test with exe first
FIXME: shrink exe

size with rocm and gpu: 5496M	exe.linux-x86_64-3.12/
size with those removed: 532M	exe.linux-x86_64-3.12/

with just the gpu code added (no amd): 982M	exe.linux-x86_64-3.12/
allmost all of that extra 500MB is:
➜  ls -l exe.linux-x86_64-3.12/lib/onnxruntime/capi/
.rwxr-xr-x@ 408M kevinh  6 Sep 16:11 libonnxruntime_providers_cuda.so

and the extra rocm stuff also:
 ls -l exe.linux-x86_64-3.12/lib/onnxruntime/capi/
.rw-r--r--@  174 kevinh  6 Sep 16:22 __init__.pyc
.rw-r--r--@  177 kevinh  6 Sep 16:22 _ld_preload.pyc
.rw-r--r--@ 1.2k kevinh  6 Sep 16:22 _pybind_state.pyc
.rw-r--r--@  284 kevinh  6 Sep 16:22 build_and_package_info.pyc
.rw-r--r--@ 160M kevinh  5 Aug 16:31 libamd_comgr.so.3.0.60403
.rw-r--r--@  28M kevinh  6 Sep 16:20 libamdhip64.so.6.4.60403
.rw-r--r--@ 101k kevinh 25 Jul 13:37 libdrm.so.2.124.0
.rw-r--r--@  73k kevinh  6 Sep 16:20 libdrm_amdgpu.so.1.124.0
.rw-r--r--@ 1.4M kevinh  6 Sep 16:21 libhipblas.so.2.4.60403
.rw-r--r--@ 7.7M kevinh  6 Sep 16:20 libhipblaslt.so.0.12.60403
.rw-r--r--@  78k kevinh  6 Sep 16:21 libhipfft.so.0.1.60403
.rw-r--r--@ 916k kevinh  5 Aug 16:37 libhiprtc.so.6.4.60403
.rw-r--r--@ 3.5M kevinh  6 Sep 16:20 libhsa-runtime64.so.1.15.60403
.rw-r--r--@  75M kevinh  5 Aug 23:40 libmigraphx.so.2012000.0.60403
.rw-r--r--@ 586k kevinh  6 Sep 16:20 libmigraphx_c.so.3.0.60403
.rw-r--r--@ 5.3M kevinh  6 Sep 16:20 libmigraphx_onnx.so.2012000.0.60403
.rw-r--r--@ 3.5M kevinh  6 Sep 16:20 libmigraphx_tf.so.2012000.0.60403
.rw-r--r--@ 707M kevinh  6 Sep 16:21 libMIOpen.so.1.0.60403
.rwxr-xr-x@  25M kevinh  6 Sep 16:18 libonnxruntime.so.1.21.0
.rwxr-xr-x@  20M kevinh  6 Sep 16:11 libonnxruntime.so.1.22.0
.rwxr-xr-x@  21M kevinh  6 Sep 11:08 libonnxruntime.so.1.22.1
.rwxr-xr-x@ 408M kevinh  6 Sep 16:11 libonnxruntime_providers_cuda.so
.rwxr-xr-x@ 585k kevinh  6 Sep 16:20 libonnxruntime_providers_migraphx.so
.rwxr-xr-x@ 1.2G kevinh  6 Sep 16:22 libonnxruntime_providers_rocm.so
.rwxr-xr-x@  16k kevinh  6 Sep 16:18 libonnxruntime_providers_shared.so
.rwxr-xr-x@ 736k kevinh  6 Sep 16:11 libonnxruntime_providers_tensorrt.so
.rw-r--r--@ 1.7G kevinh  6 Sep 16:21 librccl.so.1.0.60403
.rw-r--r--@  60M kevinh  6 Sep 16:20 librocblas.so.4.4.60403
.rw-r--r--@  11M kevinh  6 Sep 16:21 librocfft.so.0.1.60403
.rw-r--r--@  15k kevinh  5 Aug 16:19 librocm-core.so.1.0.60403
.rwxr-xr-x@ 1.5M kevinh  6 Sep 16:18 librocm_smi64-f954cc49.so.7.7.60403
.rw-r--r--@ 1.4M kevinh  5 Aug 16:20 librocm_smi64.so.7.7.60403
.rw-r--r--@ 559k kevinh  5 Aug 16:20 librocprofiler-register.so.0.4.0
.rw-r--r--@ 732M kevinh  6 Sep 16:21 librocsolver.so.0.4.60403
.rw-r--r--@ 339k kevinh  6 Sep 16:21 libroctracer64.so.4.1.60403
.rw-r--r--@  15k kevinh  5 Aug 16:40 libroctx64.so.4.1.60403
drwxr-xr-x@    - kevinh  6 Sep 16:20 migraphx
.rw-r--r--@ 1.8k kevinh  6 Sep 16:22 onnxruntime_collect_build_info.pyc
.rw-r--r--@  55k kevinh  6 Sep 16:22 onnxruntime_inference_collection.pyc
.rw-r--r--@  27M kevinh  6 Sep 16:18 onnxruntime_pybind11_state.cpython-312-x86_64-linux-gnu.so
.rw-r--r--@ 5.2k kevinh  6 Sep 16:22 onnxruntime_validation.pyc

CURRENT TASK FIXME make app image build not so huge 1.2G!
FIXME rpm build has all sorts of crap in it - like .git, tests etc...
FIXME add this to " build_exe --optimize=1" similar to what RPM build does

Please consider submitting your AppImage to AppImageHub, the crowd-sourced
central directory of available AppImages, by opening a pull request
at https://github.com/AppImage/appimage.github.io

https://github.com/niess/python-appimage 
https://python-appimage.readthedocs.io/en/latest/apps/ 
https://docs.appimage.org/packaging-guide/from-source/linuxdeploy-user-guide.html

NOTE: windows build will fail if version starts with a v.

git tag -a 3.2.0.dev0 -m "WIP by @geeksville, testing/using release binaries"
git push origin --tags

sudo apt-get update && sudo apt-get install -y fuse

# Misc docker experiments (WIP)

podman build --network=slirp4netns --security-opt=label=disable --tag graxpertcmd .
podman run -it --rm graxpertcmd bash

docker run --rm \
  -v ~/Pictures/telescope:/data \
  your-image-name \
  --input /data/image.fits

must use abs path
  docker run -v /local/path/to/file1.txt:/container/path/to/file1.txt
-mount type=bind,src=.,dst=/project,ro,Z

sudo docker cp goofy_roentgen:/out_read.jpg .

docker run -v /local/path/to/file1.txt:/container/path/to/file1.txt
crashes with glibc malloc mem corruption
python -m graxpert.main /images/testdata/Stacked_492_M\ 13_20.0s_IRCUT_20250712-010002.fit --cli --ai_version 1.0.1 --correction Division --smoothing 0.1 --bg

--gpu false hides the problem
/usr/local/bin/python -m graxpert.main /images/testdata/Stacked_492_M\ 13_20.0s_IRCUT_20250712-010002.fit -cli -ai_version 1.0.1 -correction Division -smoothing 0.1
 -bg -gpu false -out /tmp/out.tiff

special options with files
--output x
--preferences_file x 
inputfilename

run_graxpert.sh srcfile --preferences_file --output outfile --otheroptions

to force a hang: select various different stretch options then do AI background extraction.

# Todo 

* build python binary package and use that in the container version
* distribute AI model files via ghcr
* make a top level github team 

## debugging native crashes in python
  
python3-dbg -m venv graxpert-env
source graxpert-env/bin/activate
python3-dbg -m pip install -r requirements.txt
python3-dbg -m graxpert.main
gdb --args graxpert-env/bin/python3 -m graxpert.main
