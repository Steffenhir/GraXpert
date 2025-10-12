# Run inside a recent debian based image with python3, pip3, git and sudo installed
# We are careful to use the python 3.12 version, because the rocm precompiled python native code for onxruntime is only available for a few versions
FROM python:3.12.11-slim-bookworm

# We use 'user' as the name to match what the zhephyr-build image already created
ARG USERNAME=vscode

## Setup a user with sudo support
USER root

RUN apt update
RUN apt install -y --no-install-recommends python3-setuptools python3-wheel python3-tk rpm alien libgl1-mesa-glx wget sudo git patchelf 

# Create a non-root user if one doesn't exist, and give it sudo rights
RUN if ! id -u ${USERNAME} > /dev/null 2>&1; then \
        groupadd --gid 1000 ${USERNAME} && \
        useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash ${USERNAME} && \
        echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME}-nopasswd; \
    fi

# extra packages needed for debugging native crashes in python
# RUN apt install -y python3-venv python3-dbg python3-tk-dbg

# Install and run AMD ROCm GPU support.  Tested and confirmed that 7.0.1 is better than the old 6.x releases
# per https://rocm.docs.amd.com/projects/radeon/en/latest/docs/install/native_linux/install-onnx.html
# and https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html
RUN wget -P /tmp https://repo.radeon.com/amdgpu-install/7.0.1/ubuntu/noble/amdgpu-install_7.0.1.70001-1_all.deb
RUN apt install -y --allow-downgrades --no-install-recommends /tmp/amdgpu-install_7.0.1.70001-1_all.deb
RUN apt update
# Note: the github docker container is limited to 14GB max size, so we leave out the (enormous) rocm tools on that build
# RUN apt -y install rocm

# try to clean up space so our devcontainer can fit in the 14GB github action limit
RUN apt-get clean 
RUN rm -rf /var/lib/apt/lists/*

# Default user for devcontainer
USER ${USERNAME}

