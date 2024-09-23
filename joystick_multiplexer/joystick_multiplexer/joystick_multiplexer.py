import rclpy
from rclpy.node import Node
from threading import Lock
from functools import partial
from joystick_control.msg import Topic, TopicArray, Gamepad  
from topic_tools_interfaces.srv import MuxSelect, MuxAdd, MuxDelete, MuxList 

from utils.translate_joystick import JoystickTranslator
from utils.debouncing import Debouncing


class JoystickMultiplexer(Node):

    def __init__(self) -> None:
        super().__init__('joy_multiplexer')

        self.declare_parameter('steering_modes', None)
        self.STEERING_MODES = self.get_parameter('steering_modes').value

        self.active_joystick = "__none"
        self.joystick_subscribers = {}
        self.active_output = "__none"

        self.output_publishers = {
            name: self.create_publisher(Gamepad, name, 10)
            for name in self.STEERING_MODES.keys() if name != "emergency"
        }

        self.joy_list_publisher = self.create_publisher(TopicArray, 'joy_list', 10)

        self.add_joy_service = self.create_service(MuxAdd, 'add_joy', self._add_joy)
        self.remove_joy_service = self.create_service(MuxDelete, 'remove_joy', self._remove_joy)
        self.select_joy_service = self.create_service(MuxSelect, 'select_joy', self._select_joy)
        self.select_output_service = self.create_service(MuxSelect, 'select_output', self._select_output)
        self.get_selected_joy_service = self.create_service(MuxSelect, 'get_selected_joy', self._get_selected_joy)
        self.get_selected_output_service = self.create_service(MuxSelect, 'get_selected_output', self._get_selected_output)

        self.selected_joy_publisher = self.create_publisher(Topic, 'selected_joy', 10)
        self.selected_output_publisher = self.create_publisher(Topic, 'selected_output', 10)

        self.prev_inputs = {}

        self.service_lock = Lock()

        self.translator = JoystickTranslator()

    def run(self):
        rclpy.spin(self)

    def _joy_subscriber_callback(self, data: Gamepad, topic_name=""):
        inputs = self.translator.translate(data)
        debounce = Debouncing(inputs, self.prev_inputs[topic_name])
        self.prev_inputs[topic_name] = inputs

        with self.service_lock:
            if debounce.is_leading_edge(self.STEERING_MODES["emergency"]["button"]):
                self.get_logger().warn("emergency stop")
                self.set_joystick("__none")
                self.set_output("__none")
                return

            for config in self.STEERING_MODES.values():
                if debounce.is_leading_edge(config["button"]):
                    self.get_logger().warn(f"enabling {config['topic']} with joystick {topic_name}")
                    self.set_joystick(topic_name)
                    self.set_output(config["topic"])

            if topic_name == self.active_joystick and self.active_output != "__none":
                self.output_publishers[self.active_output].publish(data)

    def set_joystick(self, topic_name):
        self.active_joystick = topic_name
        self.selected_joy_publisher.publish(Topic(topic_name))

    def set_output(self, topic_name):
        self.active_output = topic_name
        self.selected_output_publisher.publish(Topic(topic_name))

    def publish_joy_list_update(self):
        self.joy_list_publisher.publish(TopicArray(
            topics=[Topic(topic_name) for topic_name in self.joystick_subscribers.keys()]
        ))

    def _get_selected_joy(self, request, response):
        with self.service_lock:
            response.topic = self.active_joystick
        return response

    def _get_selected_output(self, request, response):
        with self.service_lock:
            response.topic = self.active_output
        return response

    def _select_output(self, request, response):
        topic_name = request.topic
        self.get_logger().info(f"Selecting output {topic_name}")
        with self.service_lock:
            if topic_name == "__none":
                self.set_joystick("__none")
                self.set_output("__none")
                response.success = True
                response.prev_topic = self.active_output
                return response

            if topic_name not in self.output_publishers:
                response.success = False
                return response

            response.prev_topic = self.active_output
            self.set_output(topic_name)
            response.success = True
        return response


    def _select_joy(self, request, response):
        topic_name = request.topic
        self.get_logger().info(f"Selecting joystick {topic_name}")
        with self.service_lock:
            if topic_name == "__none":
                self.set_joystick("__none")
                self.set_output("__none")
                response.success = True
                return response

            if topic_name not in self.joystick_subscribers:
                response.success = False
                return response

            self.set_joystick(topic_name)
            response.success = True
        return response

    def _add_joy(self, request, response):
        
        
        topic_name = request.topic
        self.get_logger().info(f"Adding {topic_name}")
        with self.service_lock:
            if topic_name in self.joystick_subscribers or topic_name == "__none":
                response.success = False
            else:
                self.prev_inputs[topic_name] = {key: 0 for key in self.translator.BUTTONS_ID.keys()}
                self.joystick_subscribers[topic_name] = self.create_subscription(
                    Gamepad, topic_name, partial(self._joy_subscriber_callback, topic_name=topic_name), 10
                )
                self.publish_joy_list_update()
                response.success = True
        return response

    def _remove_joy(self, request, response):
        topic_name = request.topic
        self.get_logger().info(f"Removing {topic_name}")
        with self.service_lock:
            if topic_name not in self.joystick_subscribers:
                response.success = False
            else:
                if topic_name == self.active_joystick:
                    self.set_joystick("__none")

                del self.prev_inputs[topic_name]
                self.destroy_subscription(self.joystick_subscribers[topic_name])
                del self.joystick_subscribers[topic_name]

                self.publish_joy_list_update()
                response.success = True
        return response

    def _get_joy_list(self, request, response):
        with self.service_lock:
            response.topics = list(self.joystick_subscribers.keys())
        return response


def main(args=None):
    rclpy.init(args=args)
    node = JoystickMultiplexer()
    node.run()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
