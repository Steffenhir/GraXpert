#!/usr/bin/env bash
set -e

export USER=`whoami`

# the devcontainer mount of vscode/.local/share implicity makes the owner root (which is bad)
echo "Fixing permissions"
# Some containers might not have a .local directory at all, don't fail in that case
mkdir ~/.local | true
sudo chown -R $USER ~/.local

echo "Installing python requirements"
pip3 install --user -r requirements.txt
