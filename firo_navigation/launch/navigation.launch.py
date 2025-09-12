import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    
    # navigation configuration 
    nav_config_path = os.path.join(
        get_package_share_directory('firo_navigation'),
        'config',
        'navigation_params.yaml'
    )
    # slam configuration 
    slam_config_path = os.path.join(
        get_package_share_directory('firo_navigation'),
        'config',
        'slam_params.yaml'
    )

    # Include localization launch
    localization_launch = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource([
            get_package_share_directory('firo_navigation'),
            '/launch/localization.launch.py'
        ])
    )

    # twist stamper node -> humble doesn't support TS, which controllers require, also stops when goal is reached
    twist_stamper = Node(
        package='firo_navigation',
        executable='command_twist_stamper_node',
        name='twist_stamper_goal_stopper'
    )

    # nav2 nodes for lifecycle manager
    bt_navigator_node = Node(
        package='nav2_bt_navigator', 
        executable='bt_navigator', 
        name='bt_navigator',
        output='screen',
        parameters=[nav_config_path],
        respawn=True,
        arguments=['--ros-args', '--log-level', 'info']
    )
    behavior_server_node = Node(
        package='nav2_behaviors', 
        executable='behavior_server', 
        name='behavior_server',
	    output='screen',
        parameters=[nav_config_path],
        respawn=True,
        remappings=[('cmd_vel', 'cmd_vel_nav')],
        arguments=['--ros-args', '--log-level', 'info']
    )
    planner_server_node = Node(
        package='nav2_planner', 
        executable='planner_server', 
        name='planner_server',
        output='screen',
        parameters=[nav_config_path],
        respawn=True,
        arguments=['--ros-args', '--log-level', 'info']
    )
    smoother_server_node = Node(
        package='nav2_smoother', 
        executable='smoother_server', 
        name='smoother_server',
        output='screen',
        parameters=[nav_config_path],
        respawn=True,
        arguments=['--ros-args', '--log-level', 'info']
    )
    controller_server_node = Node(
        package='nav2_controller', 
        executable='controller_server', 
        name='controller_server',
        output='screen',
        parameters=[nav_config_path],
        respawn=True,
        arguments=['--ros-args', '--log-level', 'info'],
        remappings=[('cmd_vel', 'cmd_vel_nav')]
    )
    map_server_node = Node(
        package='nav2_map_server', 
        executable='map_server', 
        name='map_server',
        output='screen',
        parameters=[nav_config_path],
        respawn=True,
        arguments=['--ros-args', '--log-level', 'info']
    )
    map_saver_node = Node(
        package='nav2_map_server', 
        executable='map_saver_server',  
        name='map_saver',
        output='screen',
        parameters=[nav_config_path],
        respawn=True,
        arguments=['--ros-args', '--log-level', 'info']
    )
    waypoint_follower_node = Node(
        package='nav2_waypoint_follower', 
        executable='waypoint_follower', 
        name='waypoint_follower',
        output='screen',
        parameters=[nav_config_path],
        respawn=True,
        arguments=['--ros-args', '--log-level', 'info']
    )
    velocity_smoother_node = Node(
        package='nav2_velocity_smoother', 
        executable='velocity_smoother', 
        name='velocity_smoother',
        output='screen',
        parameters=[nav_config_path],
        remappings=[('cmd_vel', 'cmd_vel_nav'), ('cmd_vel_smoothed', 'cmd_vel_nav_smoothed')],
        respawn=True,
        arguments=['--ros-args', '--log-level', 'info']
    )
    collision_monitor_node = Node(
        package='nav2_collision_monitor', 
        executable='collision_monitor', 
        name='collision_monitor',
        output='screen',
        parameters=[nav_config_path],
        respawn=True,
        arguments=['--ros-args', '--log-level', 'info']
    )
    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[nav_config_path],
        respawn=True,
        arguments=['--ros-args', '--log-level', 'info'],
        remappings=[('/amcl_pose', '/pose_global')]
    )

    # lifecycle manager node 
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager',
        output='screen',
        parameters=[nav_config_path],
        respawn=True,
        arguments=['--ros-args', '--log-level', 'info']
    )

    # temp 
    # base footprint transform
    base_to_footprint = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_footprint',
        output='screen',
        arguments=['0', '0', '-0.09', '0', '0', '0', 'base_link', 'base_footprint']
    )

    # Define LaunchDescription variable
    ld = LaunchDescription()
    #temp
    ld.add_action(base_to_footprint)
    # launch nodes
    ld.add_action(localization_launch)
    ld.add_action(twist_stamper)
    # launch nav2 nodes
    ld.add_action(bt_navigator_node)
    ld.add_action(behavior_server_node)
    ld.add_action(planner_server_node)
    ld.add_action(smoother_server_node)
    ld.add_action(controller_server_node)
    ld.add_action(map_server_node)
    ld.add_action(map_saver_node)
    ld.add_action(waypoint_follower_node)
    ld.add_action(velocity_smoother_node)
    ld.add_action(collision_monitor_node)
    ld.add_action(amcl_node)
    # launch lifecycle manager
    ld.add_action(lifecycle_manager)
    return ld
