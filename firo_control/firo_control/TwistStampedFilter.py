import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from rclpy.qos import QoSProfile, QoSHistoryPolicy, QoSReliabilityPolicy
from rclpy.qos_overriding_options import QoSOverridingOptions, QoSPolicyKind
import rclpy.time

class TwistStampedFilterNode(Node):
    def __init__(self):
        super().__init__('twist_stamped_filter')

        self.latest_timestamp = None

        publisher_qos_profile = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST, 
            depth=1,                             
            lifespan=Duration(seconds=0.1) 
        )
        publisher_qos_overrides = QoSOverridingOptions(policy_kinds=(QoSPolicyKind.LIFESPAN,QoSPolicyKind.RELIABILITY))

        self.publisher = self.create_publisher(
            TwistStamped,
            '/out',
            publisher_qos_profile,
            qos_overriding_options=publisher_qos_overrides
        )        
        subscriber_qos_profile = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST, 
            depth=1,                             
            lifespan=Duration(seconds=0.1), 
            reliability=QoSReliabilityPolicy.BEST_EFFORT
        )
        subscriber_qos_overrides = QoSOverridingOptions(policy_kinds=(QoSPolicyKind.LIFESPAN,QoSPolicyKind.RELIABILITY))

        self.subscriber = self.create_subscription(
            TwistStamped,
            '/in', 
            self.twist_stamped_callback,
            subscriber_qos_profile,
            qos_overriding_options=subscriber_qos_overrides
        )


    def twist_stamped_callback(self, msg: TwistStamped):
        timestamp = rclpy.time.Time.from_msg(msg.header.stamp)

        # Only process latest messages
        if self.latest_timestamp is None or timestamp > self.latest_timestamp:
            self.latest_timestamp = timestamp
            self.publisher.publish(msg)
            # rclpy.loginfo(f'Published message with timestamp {timestamp}')
        # else:
            # rclpy.loginfo(f'Skipped message with timestamp {timestamp}')


def main(args=None):
    rclpy.init()
    node = TwistStampedFilterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
