# FIRO Joy
## Nodes
### `joy_crossbar_switch`
The `joy_crossbar_switch` node manages multiple joystick inputs in a ROS2 environment. It routes joystick messages to selected output topics, allowing users to:

- Switch between different joystick input sources
- Direct joystick commands to different robot systems (e.g., mobile platform, robotic arm)
- Disable output entirely when needed

The node implements a flexible switching mechanism between joystick inputs and outputs. Users can change which joystick controls which part of the robot by:

1. Modifying the `output_topics/<nth_output_topic>/input_topic` parameter at runtime
2. Pressing the associated button defined in `output_topics/<nth_output_topic>/button` parameter on any active joystick

When switching control modes, the node automatically handles potential conflicts. If an output topic is activated that conflicts with other outputs (as defined in the `disable` parameter), those conflicting outputs will be automatically deactivated. This ensures different joysticks don't simultaneously control the same robot components.

The node also includes an emergency stop button feature that immediately disables all output topics.

#### Subscribed Topics:
- **`<nth_input_topic>`** (`sensor_msgs/Joy`): Multiple topics, one for each topic provided in `input_topics` parameter.  

#### Published Topics:
- **`<nth_output_topic>`** (`sensor_msgs/Joy`): Multiple topics, one for each topic defined in `output_topics` parameter.

#### Services:
- **`~/add`** (`topic_tools_interfaces/MuxAdd`): Add new input topic.
- **`~/delete`** (`topic_tools_interfaces/MuxDelete`): Remove input topic.
- **`~/emergency_stop`** (`std_srvs/srv/Trigger`): Disable all output topics.

#### Parameters
- **`input_topics`** (`unbounded dynamic array`): List of joystick topics to subscribe to. Can be updated in runtime with `add` and `delete` services.
  - **`"<nth_input_topic>"`** (`string`, dynamic): Replace `<nth_input_topic>` with the input topic name. Add as many input topics as you need.
- **`output_topics`** (`dict`): A dictionary mapping output topics to their associated parameters
  - **`"<nth_output_topic>"`** (`dict`, static): Replace `<nth_output_topic>` with the output topic name. Add as many output topics as you need.
    - **`input_topic`** (`string`, dynamic, default=`""`): Input topic to link with this output. If unset, output is disabled. This parameter can be changed at runtime to select different input topic.
    - **`button`** (`uint8`, static): Button index that, when pressed on any active joystick, assigns this joystick to this output. 
    - **`disable`** (`unbounded dynamic array`): Controls mutual exclusivity by listing output topics that should be deactivated when this output is selected. If unset, defaults to all defined output topics.
      - **`"<nth_output_topic>"`** (`string`, static): Conflicting output topic.
- **`emergency_stop`** (`uint8`, static): Button index that disables all output topics.
