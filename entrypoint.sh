#!/bin/bash
set -e

export FASTDDS_BUILTIN_TRANSPORTS=UDPv4
export ROS_DOMAIN_ID=0
# Source ROS 2 and workspace
source /opt/ros/humble/setup.bash
source /workspace/install/setup.bash

exec "$@"
