#!/usr/bin/env python3
"""
占位：发布 /odom（模拟）
"""
import time
try:
    import rclpy
    from rclpy.node import Node
except Exception:
    # 允许无 ROS2 环境下导入此文件（不执行）
    rclpy = None
    Node = object


class EstimationNode(Node):
    def __init__(self):
        super().__init__('estimation_node')
        # 这里应初始化发布者：/odom
        # self.pub = self.create_publisher(Odometry, '/odom', 10)
        self.get_logger().info('Estimation node started (placeholder)')


def main():
    if rclpy is None:
        print('ROS2 环境未就绪，此脚本仅为占位。')
        return
    rclpy.init()
    node = EstimationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
