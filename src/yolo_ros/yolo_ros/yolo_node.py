import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2
import os
import json
import time
import numpy as np
import time

# Use ultralytics package for YOLOv11
from ultralytics import YOLO

class YoloV11Node(Node):
    def __init__(self):
        super().__init__('yolov11_node')

        # ---------------------------
        # Parameters
        # ---------------------------
        self.declare_parameter('image_topic', '/camera/color/image_rect_raw')
        self.declare_parameter('depth_topic', '/camera/depth/image_rect_raw')
        self.declare_parameter('camera_info_topic', '/camera/color/camera_info')
        self.declare_parameter('confidence_threshold', 0.75)
        self.declare_parameter('output_base', '')
        self.declare_parameter('save_video', False)
        self.declare_parameter('save_json', False)
        self.declare_parameter('publish_annotated', True)  # new parameter

        self.image_topic = self.get_parameter('image_topic').value
        self.depth_topic = self.get_parameter('depth_topic').value
        self.camera_info_topic = self.get_parameter('camera_info_topic').value
        self.conf_threshold = self.get_parameter('confidence_threshold').value
        self.output_base = self.get_parameter('output_base').value
        self.save_video = self.get_parameter('save_video').value
        self.save_json = self.get_parameter('save_json').value
        self.publish_annotated = self.get_parameter('publish_annotated').value

        self.bridge = CvBridge()

        # ---------------------------
        # Camera intrinsics
        # ---------------------------
        self.fx = self.fy = self.cx = self.cy = None
        self.depth_image = None

        # ---------------------------
        # Output
        # ---------------------------
        self.output_dir = "./data/output"
        os.makedirs(self.output_dir, exist_ok=True)
        self.video_writer = None
        self.json_frames = []
        self.frame_idx = 0

        # ---------------------------
        # Load YOLOv11
        # ---------------------------
        self.get_logger().info("Loading YOLOv11 model...")
        self.model = YOLO("/workspace/src/yolo_ros/models/yolo11s.pt")
        self.model.fuse()  # optional: fuse conv+bn layers

        # Determine person class index
        self.person_class_id = next(
            (i for i, name in self.model.names.items() if name == "person"), None
        )
        if self.person_class_id is None:
            raise RuntimeError("Person class not found in YOLOv11 model.")

        # ---------------------------
        # ROS subscriptions & publishers
        # ---------------------------
        self.create_subscription(Image, self.image_topic, self.image_callback, 10)
        self.create_subscription(Image, self.depth_topic, self.depth_callback, 10)
        self.create_subscription(CameraInfo, self.camera_info_topic, self.camera_info_callback, 10)

        if self.publish_annotated:
            self.annotated_pub = self.create_publisher(Image, f"{self.image_topic}_annotated", 10)

        self.get_logger().info(
            f"Subscribed to RGB: {self.image_topic}, Depth: {self.depth_topic}, CameraInfo: {self.camera_info_topic}"
        )

    # ---------------------------
    # Callbacks
    # ---------------------------
    def camera_info_callback(self, msg):
        self.fx = msg.k[0]
        self.fy = msg.k[4]
        self.cx = msg.k[2]
        self.cy = msg.k[5]

    def depth_callback(self, msg):
        try:
            if msg.encoding == '16UC1':
                self.depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough') / 1000.0
            else:
                self.depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        except Exception as e:
            self.get_logger().warn(f"Depth callback error: {e}")

    # ---------------------------
    # Video writer setup
    # ---------------------------
    def setup_video_writer(self, frame):
        if not self.save_video or self.video_writer is not None:
            return

        h, w, _ = frame.shape
        output_path = os.path.join(self.output_dir, f"{self.output_base}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(output_path, fourcc, 30, (w, h), True)
        if not self.video_writer.isOpened():
            self.get_logger().error("Failed to open video writer")
            self.video_writer = None

    # ---------------------------
    # Main image callback
    # ---------------------------
    def image_callback(self, msg):
        if self.fx is None or self.depth_image is None:
            return  # wait until camera info and depth are available

        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().warn(f"Image conversion error: {e}")
            return

        self.setup_video_writer(frame)

        # Run YOLOv11 inference
        results = self.model(frame)[0]  # first frame results
        boxes = results.boxes.xyxy.cpu().numpy()
        confs = results.boxes.conf.cpu().numpy()
        classes = results.boxes.cls.cpu().numpy()

        persons = []

        for i in range(len(boxes)):
            xmin, ymin, xmax, ymax = map(int, boxes[i])
            conf = float(confs[i])
            cls = int(classes[i])

            if cls != self.person_class_id or conf < self.conf_threshold:
                continue

            cx, cy = (xmin + xmax) // 2, (ymin + ymax) // 2

            Z = float(self.depth_image[cy, cx]) if self.depth_image is not None else 0.0
            X = (cx - self.cx) * Z / self.fx
            Y = (cy - self.cy) * Z / self.fy
            distance = (X**2 + Y**2 + Z**2) ** 0.5

            person_data = {
                "bbox": [xmin, ymin, xmax, ymax],
                "confidence": round(conf, 2),
                "center": [cx, cy],
                "depth_m": round(Z, 2),
                "distance": round(distance, 2),
                "position_3d": [round(X, 2), round(Y, 2), round(Z, 2)]
            }
            persons.append(person_data)

            # Draw bounding box
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            cv2.putText(frame, f"{conf:.2f}", (xmin, ymin - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Publish annotated image if enabled
        if self.publish_annotated:
            annotated_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            self.annotated_pub.publish(annotated_msg)

        # Save JSON or video
        if persons:
            json_str = json.dumps({
                "frame_idx": self.frame_idx,
                "timestamp": time.time(),
                "persons": persons
            }, indent=2)
            print(json_str)

        if self.save_video and self.video_writer is not None:
            self.video_writer.write(frame)

        if self.save_json:
            self.json_frames.append({
                "frame_idx": self.frame_idx,
                "timestamp": time.time(),
                "persons": persons
            })

        self.frame_idx += 1

    # ---------------------------
    # Cleanup
    # ---------------------------
    def destroy_node(self):
        if self.video_writer is not None:
            self.video_writer.release()
            self.get_logger().info("Video writer released.")

        if self.save_json and self.output_base:
            output_path = os.path.join(self.output_dir, f"{self.output_base}.json")
            with open(output_path, "w") as f:
                json.dump(self.json_frames, f, indent=2)
            self.get_logger().info(f"JSON saved to {output_path}")

        super().destroy_node()


def main():
    rclpy.init()
    node = YoloV11Node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()