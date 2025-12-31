#!/usr/bin/env python3
"""
占位：订阅目标点并发布 /path
"""
try:
    import rclpy
    from rclpy.node import Node
except Exception:
    rclpy = None
    Node = object


class PlanningNode(Node):
    def __init__(self):
        super().__init__('planning_node')
        self.get_logger().info('Planning node started (placeholder)')


def main():
    if rclpy is None:
        print('ROS2 环境未就绪，此脚本仅为占位。')
        return
    rclpy.init()
    node = PlanningNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
