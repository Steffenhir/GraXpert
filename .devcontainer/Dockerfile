# Run inside a recent debian based image with python3, pip3, git and sudo installed
# We are careful to use the python 3.12 version, because the rocm precompiled python native code for onxruntime is only available for a few versions
FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# We use 'user' as the name to match what the zhephyr-build image already created
ARG USERNAME=vscode

## Setup a user with sudo support
USER root

RUN apt update
RUN apt install -y libgl1-mesa-glx 

# extra packages needed for debugging native crashes in python
# RUN apt install -y python3-venv python3-dbg python3-tk-dbg

# Install and run AMD ROCm GPU support
# per https://rocm.docs.amd.com/projects/radeon/en/latest/docs/install/native_linux/install-onnx.html
RUN wget -P /tmp https://repo.radeon.com/amdgpu-install/6.4.1/ubuntu/jammy/amdgpu-install_6.4.60401-1_all.deb
RUN apt install -y /tmp/amdgpu-install_6.4.60401-1_all.deb
RUN apt update
RUN apt install -y python3-setuptools python3-wheel
# sudo usermod -a -G render,video $LOGNAME # Add the current user to the render and video groups
RUN apt -y install rocm


# Default user for devcontainer
USER vscode

