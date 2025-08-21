import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, LifecycleNode


def generate_launch_description():
    
    # lifecycle manager configuration file for ldlidar node
    lc_mgr_config_path = os.path.join(
        get_package_share_directory('ldlidar_node'),
        'params',
        'lifecycle_mgr_slam.yaml'
    )

    # slam toolbox configuration
    slam_config_path = os.path.join(
        get_package_share_directory('firo_navigation'),
        'config',
        'slam_params.yaml'
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

    # slam toolbox node in async mode
    slam_toolbox_node = LifecycleNode(
          package='slam_toolbox',
          executable='async_slam_toolbox_node',
          namespace='',
          name='slam_toolbox',
          output='screen',
          parameters=[
            # YAML files
            slam_config_path # Parameters
          ],
          remappings=[
                ('/pose', '/pose_slam')
          ]       
    )

    # include ldlidar node launch
    ldlidar_launch = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource([
            get_package_share_directory('firo_navigation'),
            '/launch/lidar_bringup.launch.py'
        ]),
        launch_arguments={
            'node_name': 'ldlidar_node'
        }.items(), 
    )

    # fake odom publisher
    fake_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='fake_odom_to_base_link',
        output='screen',
        arguments=['0', '0', '0', '0', '0', '0', 'odom', 'base_link']
    )
    # lidar base transform
    base_to_lidar = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_lidar',
        output='screen',
        arguments=['0.25', '0', '0.2', '0', '0', '0', 'base_link', 'lidar_link']
    )
    # base footprint transform
    base_to_footprint = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_footprint',
        output='screen',
        arguments=['0', '0', '-0.09', '0', '0', '0', 'base_link', 'base_footprint']
    )

    # RVIZ2 settings
    rviz2_config = os.path.join(
        get_package_share_directory('ldlidar_node'),
        'config',
        'ldlidar_slam.rviz'
    )

    # RVIZ2node
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=[["-d"], [rviz2_config]]
    )

    # Define LaunchDescription variable
    ld = LaunchDescription()

    # Launch Nav2 Lifecycle Manager
    ld.add_action(lc_mgr_node)

    # Launch SLAM Toolbox node
    ld.add_action(slam_toolbox_node)

    # Launch fake odom publisher node
    #ld.add_action(fake_odom)

    # Launch fake footprint publisher node
    ld.add_action(base_to_footprint)

    # Launch static transfrom publisher nodes
    ld.add_action(base_to_lidar)

    # Call LDLidar launch
    ld.add_action(ldlidar_launch)

    # Start RVIZ2
    ld.add_action(rviz2_node)

    return ld
