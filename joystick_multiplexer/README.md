# Joystick Multiplexer

## Purpose
The `joystick_multiplexer` package is designed to manage multiple joystick inputs in a ROS2 environment. It selects which joystick is active and routes the appropriate messages to control topics. It supports switching between multiple steering modes and handles emergency stop functionality.

## Nodes

### `joy_multiplexer`

#### Subscribed Topics:
- **`/joystick_name`** (`sensor_msgs/Joy`): Receives joystick inputs.

#### Published Topics:
- **`/selected_joy`** (`joystick_control/Topic`): Publishes the name of the active joystick.
- **`/selected_output`** (`joystick_control/Topic`): Publishes the currently selected output topic.
- **`/joy_list`** (`joystick_control/TopicArray`): Publishes the list of available joysticks.

#### Services:
- **`/add_joy`** (`MuxAdd`): Adds a new joystick to the list of available joysticks.
- **`/remove_joy`** (`MuxDelete`): Removes a joystick from the list.
- **`/select_joy`** (`MuxSelect`): Selects the active joystick.
- **`/select_output`** (`MuxSelect`): Selects the active output topic.
- **`/get_selected_joy`** (`MuxSelect`): Returns the name of the currently selected joystick.
- **`/get_selected_output`** (`MuxSelect`): Returns the name of the currently selected output.

## Parameters
- **`steering_modes`** (`dict`): A dictionary defining available steering modes and their associated joystick buttons and topics.
