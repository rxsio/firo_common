#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

'''
Parameter Description:
---
- Set laser scan directon: 
  1. Set counterclockwise, example: {'laser_scan_dir': True} - ROS standard
  2. Set clockwise,        example: {'laser_scan_dir': False}
- Angle crop setting, Mask data within the set angle range:
  1. Enable angle crop fuction:
    1.1. enable angle crop,  example: {'enable_angle_crop_func': True}
    1.2. disable angle crop, example: {'enable_angle_crop_func': False}
  2. Angle cropping interval setting:
  - The distance and intensity data within the set angle range will be set to 0.
  - angle >= 'angle_crop_min' and angle <= 'angle_crop_max' which is [angle_crop_min, angle_crop_max], unit is degress.
    example:
      {'angle_crop_min': 135.0}
      {'angle_crop_max': 225.0}
      which is [135.0, 225.0], angle unit is degress.
'''

def generate_launch_description():

    # Lifecycle manager configuration file
    lidar_params = os.path.join(
        get_package_share_directory('firo_navigation'),
        'config',
        'lidar_params.yaml'
    )

    # LDROBOT LiDAR publisher node
    lidar_horizontal_node = Node(
        package='ldlidar_sl_ros2',
        executable='ldlidar_sl_ros2_node',
        name='lidar_horizontal',
        output='screen',
        parameters=[lidar_params]
    )
    lidar_vertical_left_node = Node(
        package='ldlidar_sl_ros2',
        executable='ldlidar_sl_ros2_node',
        name='lidar_vertical_left',
        output='screen',
        parameters=[lidar_params]
    )
    lidar_vertical_right_node = Node(
        package='ldlidar_sl_ros2',
        executable='ldlidar_sl_ros2_node',
        name='lidar_vertical_right',
        output='screen',
        parameters=[lidar_params]
    )

    # temp
    base_to_lidar = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_lidar',
        output='screen',
        arguments=['0.265', '0', '0.055', '0', '0', '0', 'torso', 'lidar_horizontal_link']
    )
    base_to_lidar_left = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_imu',
        output='screen',
        arguments=['-0.135', '0.2', '0.05','0', '0', '-1.5708', 'torso', 'lidar_vertical_left_link']
    )
    base_to_lidar_right = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_imu',
        output='screen',
        arguments=['-0.135', '-0.2', '0.05','0', '0', '1.5708', 'torso', 'lidar_vertical_right_link']
    )

    # Define LaunchDescription variable
    ld = LaunchDescription()
    ld.add_action(lidar_horizontal_node)
    ld.add_action(lidar_vertical_left_node)
    ld.add_action(lidar_vertical_right_node)
    ld.add_action(base_to_lidar)
    ld.add_action(base_to_lidar_left)
    ld.add_action(base_to_lidar_right)
    return ld