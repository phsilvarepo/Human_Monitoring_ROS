# Human Monitoring
This package contains the package to run human detection and identification wihtin the 3D space, in realtion to the camera frame. This 

## Setup

Edit env file to match specific setup. This node is equuiped with teh necessary SDK to run Intel Realsense cameras.

Parameters:

IMAGE_TOPIC - ROS2 Topic 

DEPTH_TOPIC
CAMERA_INFO_TOPIC
CONF_THRESHOLD
PUBLISH_RESULT 
ROS_DOMAIN_ID=0

IMAGE_TOPIC=/station/sensors/camera/people/rgb
DEPTH_TOPIC=/station/sensors/camera/people/depth
CAMERA_INFO_TOPIC=/station/sensors/camera/people/camera_info

CONF_THRESHOLD=0.75
SAVE_VIDEO=fa- Boldsfsd
SAVE_JSON=false
OUTPUT_BASE=test_run
PUBLISH_RESULT=true
