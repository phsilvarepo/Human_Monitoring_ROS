# -------------------------------
# Base image with CUDA for GPU acceleration
# -------------------------------
FROM nvidia/cuda:12.2.2-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV ROS_DISTRO=humble

# -------------------------------
# Install basic tools
# -------------------------------
RUN apt-get update && apt-get install -y \
    curl gnupg2 lsb-release git wget build-essential python3-pip \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Add ROS 2 apt repository
# -------------------------------
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
    http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" \
    > /etc/apt/sources.list.d/ros2.list

# -------------------------------
# Install ROS 2 + Python ROS tools
# -------------------------------
RUN apt-get update && apt-get install -y \
    ros-humble-desktop \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-argcomplete \
    ros-humble-cv-bridge \
    ros-humble-image-transport \
    libopencv-dev libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Initialize rosdep
RUN rosdep init || true
RUN rosdep update

# -------------------------------
# Install Python ML stack
# -------------------------------
RUN pip3 install --upgrade pip

# Install PyTorch (CUDA 12.1 wheels)
RUN pip3 install --ignore-installed torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install compatible NumPy + ML tools
RUN pip3 install "numpy<2" pandas opencv-python ultralytics seaborn tqdm

# -------------------------------
# Copy ROS 2 workspace into container
# -------------------------------
WORKDIR /workspace
COPY ./src ./src

# Build ROS 2 workspace
RUN /bin/bash -c "source /opt/ros/$ROS_DISTRO/setup.bash && colcon build --symlink-install"

# -------------------------------
# Entrypoint
# -------------------------------
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
