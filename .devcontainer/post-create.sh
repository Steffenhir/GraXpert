#!/usr/bin/env bash
set -e

export USER=`whoami`

# the devcontainer mount of vscode/.local/share implicity makes the owner root (which is bad)
echo "Fixing permissions"
# Some containers might not have a .local directory at all, don't fail in that case
mkdir ~/.local | true
sudo chown -R $USER ~/.local

echo "Installing python requirements"
pip3 install --user --break-system-packages --no-warn-script-location -r requirements.txt

pip3 install --user --break-system-packages --no-warn-script-location cx_Freeze build twine

# if gh is available add the github actions extension
if command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) found, installing 'act' extension..."
    gh extension install https://github.com/nektos/gh-act
fi

# onnxruntime-gpu (moved to requirements.txt)
# Moved into requirements.txt to match historic user expectations (though it adds about about 500MB to exe size)
# without this added exe is already 500MB.
# echo "Installing onnxruntime-gpu for NVIDIA GPU support"
# pip install --user onnxruntime-gpu[cuda,cudnn]

# FIXME test onnxruntime-openvino to see how exe size is affected

# rocm moved to requirements-rocm.txt 
# would add 4.5GB! to exe size, make optional for AMD GPU users
# echo "Installing onnxruntime-rocm for AMD GPU support"
# pip install --user --force onnxruntime-rocm==1.21.0 onnxruntime==1.21.0 onnxruntime-gpu[cuda,cudnn]==1.21.0 -f https://repo.radeon.com/rocm/manylinux/rocm-rel-6.4.3/

# NOTE! If using rocm you must uninstall onnxruntime-gpu and THEN install from the rocm repo
# NOTE! rocm support only seems to be enabled currently in Ubuntu, not bare Debian!
pip3 uninstall -y --break-system-packages onnxruntime onnxruntime-gpu onnxruntime-rocm
# switching to the rocm runtime apparently requires **removing** the onnxruntime package (which came from a different repo?)
pip3 install --user --force --break-system-packages --no-warn-script-location numpy==2.2.6 onnxruntime-rocm==1.22.1 -f https://repo.radeon.com/rocm/manylinux/rocm-rel-7.0/
pip3 cache purge