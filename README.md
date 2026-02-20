# Human Monitoring

This package enables human detection and 3D position estimation relative to the camera frame. It leverages the **YOLOv11** model to identify human operators and uses depth information to compute their positions in 3D space. Communication between containers is handled via **host network mode**, allowing ROS2 nodes in different containers to interact seamlessly over the host network.

## Setup

Edit the `.env` file to match your specific setup.  

### Parameters

- **IMAGE_TOPIC** – ROS2 topic for the RGB image message  
- **DEPTH_TOPIC** – ROS2 topic for the depth image message  
- **CAMERA_INFO_TOPIC** – ROS2 topic for the camera info message  
- **CONF_THRESHOLD** – Confidence threshold for the YOLO model  
- **PUBLISH_RESULT** – Boolean to publish annotated detection result  

## Validation

This package can run detection and 3D position estimation of human operators with input images accessed from external sources via ROS2 topics (e.g., from a simulator) or directly from hardware such as **Intel RealSense** cameras.  

### Testing

**From ROS2 topic with existing data:**

```
docker compose build
docker compose up yolo
```

**Directly from the Intel Realsense camera:**

```
docker compose build
docker compose up
```

### Notes

- This package was tested in a Linux x86 environment (Ubuntu 24.04) with CUDA-capable GPU support, running on an **RTX 3090**. 
- Since the YOLO architecture is not very computationally expensive, it can run on weaker setups, but some changes to the Dockerfile (Ubuntu + CUDA version) may be required.
- Still need to test Realsense 
