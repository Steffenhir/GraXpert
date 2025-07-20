# Run inside a recent debian based image with python3, pip3, git and sudo installed
# We are careful to use the python 3.12 version, because the rocm precompiled python native code for onxruntime is only available for a few versions
FROM python:3.12-slim-bookworm

# We use 'user' as the name to match what the zhephyr-build image already created
ARG USERNAME=vscode

## Setup a user with sudo support
USER root

RUN apt update
RUN apt install -y libgl1-mesa-glx wget sudo

# Create a non-root user if one doesn't exist, and give it sudo rights
RUN if ! id -u ${USERNAME} > /dev/null 2>&1; then \
        groupadd --gid 1000 ${USERNAME} && \
        useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash ${USERNAME} && \
        echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME}-nopasswd; \
    fi

# extra packages needed for debugging native crashes in python
# RUN apt install -y python3-venv python3-dbg python3-tk-dbg

# Default user for devcontainer
USER ${USERNAME}

