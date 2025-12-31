#!/usr/bin/env python3
"""
占位：从视频流检测障碍并发布 /obstacles
"""
try:
    import rclpy
    from rclpy.node import Node
except Exception:
    rclpy = None
    Node = object


class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')
        self.get_logger().info('Perception node started (placeholder)')


def main():
    if rclpy is None:
        print('ROS2 环境未就绪，此脚本仅为占位。')
        return
    rclpy.init()
    node = PerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
