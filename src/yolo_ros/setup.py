from setuptools import find_packages, setup

package_name = 'yolo_ros'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='unparallel',
    maintainer_email='pedrosilva7320@gmail.com',
    description='YOLOv5 ROS2 node',
    license='MIT',
    entry_points={
        'console_scripts': [
            'yolo_node = yolo_ros.yolo_node:main',
        ],
    },
)

