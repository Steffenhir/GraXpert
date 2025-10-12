#!/bin/bash

set -e

echo "Run this script on the HOST to create a vlan network that the windows/os-x VMs can live inside"
echo "NOTE: This is unlikely to be helpful if you are using rootless-podman because those net devices can reach the real host interfaces"

IFACE=wlp194s0

# Note: we reserve .198 for the host machine, and .193-.197 for containers
# 193 for windows
# 194 for macos
docker network create -d macvlan \
    --subnet=192.168.8.0/24 \
    --gateway=192.168.8.1 \
    --ip-range=192.168.8.192/29 \
    --aux-address 'host=192.168.8.198' \
    -o parent=$IFACE vlan

# Create a shim interface on the host so the host can also access the vlan network
sudo ip link add mynet-shim link $IFACE type macvlan mode bridge
sudo ip addr add 192.168.8.198/32 dev mynet-shim
sudo ip link set mynet-shim up

# tell host to to route all traffic for the vlan subnet via the shim interface
sudo ip route add 192.168.8.192/29 dev mynet-shim
