# Human Monitoring
This package contains the package to run human detection and identification wihtin the 3D space, in relation to the camera frame. This package utilizes Yolov11 model to identify the humans in the scene and the depth infomariton to estiamte its 3D position. 

## Setup

Edit env file to match specific setup

Parameters:

IMAGE_TOPIC - ROS2 Topic ROS2 Topic Name for the Deph Image Messgae
DEPTH_TOPIC - ROS2 Topic Name for the Deph Image Messgae
CAMERA_INFO_TOPIC - ROS2 Topic Name for the Camera Info Messgae
CONF_THRESHOLD - Confidence Threshold for YOLO Model
PUBLISH_RESULT - Bollean on puiblishin annotated result Image

## Validation

This package is anbled to run detection and estimation of humna opeartors with teh input images being accesed from outside its scope via ROs2 Topic, from a Sim for example. Or directyl from a real hardware, in this case Intel reaslsense cameras. Therefore to test the pavkge:

docker compose build
With the data present in ROs2 topic:

'''
docker compose up yolo
'''

Directly from Intel Realsesne camera:

'''
docker compose up
'''

Specifics. This node was tested in a Linux x86 envrionemnt with acces to CUDA , running of a RTX 3090. Since the yolo architecture is not very computanionnly expensive it can be ran in weaker setup, but some changes to the Dockerfile Ubuntu+Cuda version may require changes,
