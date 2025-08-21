import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, LifecycleNode


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
    # robot localization configuration 
    loc_config_path = os.path.join(
        get_package_share_directory('firo_navigation'),
        'config',
        'robot_localization_params.yaml'
    )

    # local robot localization node - no-lifecycle possibility
    local_localization_node = Node(
            package='robot_localization', 
            executable='ekf_node', 
            name='ekf_filter_node_odom',
	    output='screen',
            parameters=[loc_config_path],
            remappings=[('odometry/filtered', 'odometry/local')],
            respawn=True,
            arguments=['--ros-args', '--log-level', 'info']           
        )

    # global robot localization node - no-lifecycle possibility
    global_localization_node = Node(
            package='robot_localization', 
            executable='ekf_node', 
            name='ekf_filter_node_map',
	    output='screen',
            parameters=[loc_config_path],
            remappings=[('odometry/filtered', 'odometry/global')],
            respawn=True,
            arguments=['--ros-args', '--log-level', 'info'] 
        )

    # slam toolbox node in async mode
    slam_toolbox_node = LifecycleNode(
          package='slam_toolbox',
          executable='async_slam_toolbox_node',
          name='slam_toolbox',
          namespace='',
          output='screen',
          parameters=[slam_config_path],
          remappings=[('/pose', '/pose_slam')],
          respawn=True,
          arguments=['--ros-args', '--log-level', 'info']         
    )
    # twist stamper node -> humble doesnt support TS which controllers require
    twist_stamper = Node(
        package='twist_stamper',
        executable='twist_stamper',
        name='twist_stamper',
        remappings=[('/cmd_vel_in','/cmd_vel_nav_smoothed'),
                    ('/cmd_vel_out','/cmd_vel')]
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


    # Define LaunchDescription variable
    ld = LaunchDescription()

    # launch nodes
    ld.add_action(local_localization_node)
    ld.add_action(global_localization_node)
    ld.add_action(slam_toolbox_node)
    # nav2 nodes
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
    # lifecycle manager
    ld.add_action(lifecycle_manager)


    return ld
