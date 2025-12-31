#!/usr/bin/env python3
"""
占位：将 /path 转换为 RC 命令并通过串口下发
"""
try:
    import rclpy
    from rclpy.node import Node
except Exception:
    rclpy = None
    Node = object


class ControlBridgeNode(Node):
    def __init__(self):
        super().__init__('control_bridge_node')
        self.get_logger().info('Control bridge node started (placeholder)')


def main():
    if rclpy is None:
        print('ROS2 环境未就绪，此脚本仅为占位。')
        return
    rclpy.init()
    node = ControlBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
