import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    
    # Lifecycle manager configuration file
    lc_mgr_config_path = os.path.join(
        get_package_share_directory('firo_navigation'),
        'config',
        'lidar_params.yaml'
    )

    # Lifecycle manager node
    lc_mgr_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager',
        output='screen',
        parameters=[
            # YAML files
            lc_mgr_config_path  # Parameters
        ]
    )

    # Include launch
    lidar_horizontal_launch = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource([
            get_package_share_directory('firo_navigation'),
            '/launch/lidar_bringup.launch.py'
        ]),
        launch_arguments={
            'node_name': 'lidar_horizontal'
        }.items()
    )
    lidar_vertical_left_launch = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource([
            get_package_share_directory('firo_navigation'),
            '/launch/lidar_bringup.launch.py'
        ]),
        launch_arguments={
            'node_name': 'lidar_vertical_left'
        }.items()
    )
    lidar_vertical_right_launch = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource([
            get_package_share_directory('firo_navigation'),
            '/launch/lidar_bringup.launch.py'
        ]),
        launch_arguments={
            'node_name': 'lidar_vertical_right'
        }.items()
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
    # Launch Nav2 Lifecycle Manager
    ld.add_action(lc_mgr_node)
    # Call LDLidar launch
    ld.add_action(lidar_horizontal_launch)
    #ld.add_action(lidar_vertical_left_launch)
    #ld.add_action(lidar_vertical_right_launch)
    # lidar tranform
    ld.add_action(base_to_lidar)
    ld.add_action(base_to_lidar_left)
    ld.add_action(base_to_lidar_right)
    return ld
