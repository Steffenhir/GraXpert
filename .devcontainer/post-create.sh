#!/usr/bin/env bash
set -e

echo "Installing python requirements"
pip3 install --user -r requirements.txt

echo "Installing onnxruntime-rocm for AMD GPU support"
pip3 install --user onnxruntime-rocm -f https://repo.radeon.com/rocm/manylinux/rocm-rel-6.4.1/