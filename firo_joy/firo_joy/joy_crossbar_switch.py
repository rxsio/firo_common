import rclpy
from rclpy.node import Node
from threading import Lock
from functools import partial
from sensor_msgs.msg import Joy  
from topic_tools_interfaces.srv import MuxAdd, MuxDelete, MuxSelect
from topic_tools_interfaces.msg import Topic, TopicArray
from std_srvs.srv import Trigger

from utils.translate_joystick import JoystickTranslator
from utils.debouncing import Debouncing


class JoystickMultiplexer(Node):

    def __init__(self) -> None:
        super().__init__('joy_crossbar_switch')

        # Declare and get parameters
        self.declare_parameter('input_topics', [])
        self.declare_parameter('output_topics', {})
        self.declare_parameter('emergency_stop', 0)

        self.input_topics = self.get_parameter('input_topics').value
        self.output_topics_config = self.get_parameter('output_topics').value
        self.emergency_stop_button = self.get_parameter('emergency_stop').value

        # Initialize data structures
        self.joystick_subscribers = {}
        self.output_publishers = {}
        self.active_outputs = {}  # Maps output_topic -> input_topic
        self.prev_inputs = {}
        self.service_lock = Lock()

        # Create publishers for output topics
        for output_topic in self.output_topics_config:
            self.output_publishers[output_topic] = self.create_publisher(
                Joy, output_topic, 10
            )
            # Initialize all outputs as inactive
            self.active_outputs[output_topic] = ""

        # Create publishers for topic lists and selections
        self.joy_list_publisher = self.create_publisher(
            TopicArray, '~/joy_list', 10
        )
        self.output_status_publisher = self.create_publisher(
            TopicArray, '~/output_status', 10
        )

        # Create services
        self.add_joy_service = self.create_service(MuxAdd, '~/add', self._add_joy)
        self.remove_joy_service = self.create_service(MuxDelete, '~/delete', self._remove_joy)
        self.emergency_stop_service = self.create_service(Trigger, '~/emergency_stop', self._emergency_stop)

        # Initialize joystick translator for button mapping
        self.translator = JoystickTranslator()

        # Subscribe to initial input topics
        for topic in self.input_topics:
            self._add_joy_topic(topic)
            
        # Publish initial state
        self.publish_joy_list_update()
        self.publish_output_status_update()
        
        self.get_logger().info('Joy Crossbar Switch initialized')

    def run(self):
        rclpy.spin(self)

    def _joy_subscriber_callback(self, data: Joy, topic_name=""):
        inputs = self.translator.translate(data)
        
        # Initialize debouncing if this is the first message
        if topic_name not in self.prev_inputs:
            self.prev_inputs[topic_name] = {key: 0 for key in self.translator.BUTTONS_ID.keys()}
            
        debounce = Debouncing(inputs, self.prev_inputs[topic_name])
        self.prev_inputs[topic_name] = inputs

        with self.service_lock:
            # Check for emergency stop button
            if debounce.is_leading_edge(self.emergency_stop_button):
                self.get_logger().warn("Emergency stop activated")
                self._disable_all_outputs()
                return

            # Check for output activation buttons
            for output_topic, config in self.output_topics_config.items():
                button_index = config.get('button', 0)
                if debounce.is_leading_edge(button_index):
                    self.get_logger().info(f"Button pressed to assign {topic_name} to {output_topic}")
                    self._set_output(output_topic, topic_name)

            # Route joy messages to active outputs
            for output_topic, input_topic in self.active_outputs.items():
                if input_topic == topic_name and input_topic:
                    self.output_publishers[output_topic].publish(data)

    def _add_joy_topic(self, topic_name):
        """Helper method to add a joystick topic subscription"""
        if topic_name in self.joystick_subscribers:
            return False
            
        self.joystick_subscribers[topic_name] = self.create_subscription(
            Joy, topic_name, partial(self._joy_subscriber_callback, topic_name=topic_name), 10
        )
        return True

    def _set_output(self, output_topic, input_topic):
        """Set which input topic controls which output topic, handling conflicts"""
        if output_topic not in self.output_topics_config:
            return False
            
        # Handle conflicts - deactivate outputs listed in the 'disable' parameter
        if input_topic:  # Only if activating (not deactivating)
            disable_list = self.output_topics_config[output_topic].get('disable', list(self.output_topics_config.keys()))
            for other_output in disable_list:
                if other_output != output_topic and other_output in self.active_outputs:
                    self.active_outputs[other_output] = ""
        
        # Set the new mapping
        self.active_outputs[output_topic] = input_topic
        
        # Update parameter to reflect current state
        self.output_topics_config[output_topic]['input_topic'] = input_topic
        
        # Publish updated status
        self.publish_output_status_update()
        return True

    def _disable_all_outputs(self):
        """Disable all output topics"""
        for output_topic in self.active_outputs:
            self.active_outputs[output_topic] = ""
        self.publish_output_status_update()

    def publish_joy_list_update(self):
        """Publish the list of available joystick topics"""
        self.joy_list_publisher.publish(TopicArray(
            topics=[Topic(topic=topic_name) for topic_name in self.joystick_subscribers.keys()]
        ))

    def publish_output_status_update(self):
        """Publish the current status of output topics and their input assignments"""
        status_array = []
        for output_topic, input_topic in self.active_outputs.items():
            if input_topic:  # Only include active mappings
                status_array.append(Topic(topic=f"{output_topic}:{input_topic}"))
                
        self.output_status_publisher.publish(TopicArray(topics=status_array))

    def _add_joy(self, request, response):
        """Service handler to add a new joystick input topic"""
        topic_name = request.topic
        self.get_logger().info(f"Adding joystick input: {topic_name}")
        
        with self.service_lock:
            success = self._add_joy_topic(topic_name)
            response.success = success
            
            if success:
                # Add to parameters
                if topic_name not in self.input_topics:
                    self.input_topics.append(topic_name)
                    
                self.publish_joy_list_update()
                
        return response

    def _remove_joy(self, request, response):
        """Service handler to remove a joystick input topic"""
        topic_name = request.topic
        self.get_logger().info(f"Removing joystick input: {topic_name}")
        
        with self.service_lock:
            if topic_name not in self.joystick_subscribers:
                response.success = False
            else:
                # Remove from active outputs
                for output_topic in self.active_outputs:
                    if self.active_outputs[output_topic] == topic_name:
                        self.active_outputs[output_topic] = ""
                
                # Destroy subscription
                self.destroy_subscription(self.joystick_subscribers[topic_name])
                del self.joystick_subscribers[topic_name]
                
                # Remove from previous inputs cache
                if topic_name in self.prev_inputs:
                    del self.prev_inputs[topic_name]
                
                # Remove from parameters
                if topic_name in self.input_topics:
                    self.input_topics.remove(topic_name)
                
                self.publish_joy_list_update()
                self.publish_output_status_update()
                response.success = True
                
        return response

    def _emergency_stop(self, request, response):
        """Service handler for emergency stop"""
        self.get_logger().warn("Emergency stop service called")
        
        with self.service_lock:
            self._disable_all_outputs()
            response.success = True
            response.message = "All outputs disabled by emergency stop"
            
        return response


def main(args=None):
    rclpy.init(args=args)
    node = JoystickMultiplexer()
    node.run()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
