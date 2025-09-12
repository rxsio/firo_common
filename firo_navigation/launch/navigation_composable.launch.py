import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import ComposableNodeContainer
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.descriptions import ComposableNode
from launch_ros.actions import Node
"""
Soemthing still doesn't work as it should, for some reason local costmap gets initalized as global and global is empty. To de fixed.
"""


def generate_launch_description():

    # navigation configuration 
    nav_config_path = os.path.join(
        get_package_share_directory('firo_navigation'),
        'config',
        'navigation_params.yaml'
    )
   
    # composable nodes definitions
    bt_navigator = ComposableNode(
        package='nav2_bt_navigator',
        plugin='nav2_bt_navigator::BtNavigator',
        name='bt_navigator',
        parameters=[nav_config_path]
    )
    behavior_server = ComposableNode(
        package='nav2_behaviors',
        plugin='behavior_server::BehaviorServer',
        name='behavior_server',
        parameters=[nav_config_path],
        remappings=[('cmd_vel', 'cmd_vel_nav')]
    )
    planner_server = ComposableNode(
        package='nav2_planner',
        plugin='nav2_planner::PlannerServer',
        name='planner_server',
        parameters=[nav_config_path]
    )
    smoother_server = ComposableNode(
        package='nav2_smoother',
        plugin='nav2_smoother::SmootherServer',
        name='smoother_server',
        parameters=[nav_config_path]
    )
    controller_server = ComposableNode(
        package='nav2_controller',
        plugin='nav2_controller::ControllerServer',
        name='controller_server',
        parameters=[nav_config_path],
        remappings=[('cmd_vel', 'cmd_vel_nav')]
    )
    map_server = ComposableNode(
        package='nav2_map_server',
        plugin='nav2_map_server::MapServer',
        name='map_server',
        parameters=[nav_config_path]
    )
    waypoint_follower = ComposableNode(
        package='nav2_waypoint_follower',
        plugin='nav2_waypoint_follower::WaypointFollower',
        name='waypoint_follower',
        parameters=[nav_config_path]
    )
    velocity_smoother = ComposableNode(
        package='nav2_velocity_smoother',
        plugin='nav2_velocity_smoother::VelocitySmoother',
        name='velocity_smoother',
        parameters=[nav_config_path],
        remappings=[('cmd_vel', 'cmd_vel_nav'),
                    ('cmd_vel_smoothed', 'cmd_vel_nav_smoothed')]
    )
    collision_monitor = ComposableNode(
        package='nav2_collision_monitor',
        plugin='nav2_collision_monitor::CollisionMonitor',
        name='collision_monitor',
        parameters=[nav_config_path]
    )
    amcl = ComposableNode(
        package='nav2_amcl',
        plugin='nav2_amcl::AmclNode',
        name='amcl',
        parameters=[nav_config_path],
        remappings=[('/amcl_pose', '/pose_global')]
    )
    # composable nodes container
    nav_container = ComposableNodeContainer(
        name='navigation_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container_mt',
        composable_node_descriptions=[
            map_server,
            planner_server,
            controller_server,
            smoother_server,
            behavior_server,
            bt_navigator,
            waypoint_follower,
            velocity_smoother,
            collision_monitor,
            amcl,
        ],
        output='screen'
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

    # Include localization launch
    localization_launch = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource([
            get_package_share_directory('firo_navigation'),
            '/launch/localization.launch.py'
        ])
    )
    # twist stamper node -> humble doesn't support TS, which controllers require, also stops when goal is reached
    twist_stamper_node = Node(
        package='firo_navigation',
        executable='command_twist_stamper_node',
        name='twist_stamper_goal_stopper'
    )
    # temp
    base_to_footprint = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_footprint',
        output='screen',
        arguments=['0', '0', '-0.09', '0', '0', '0', 'base_link', 'base_footprint']
    )

    # Define LaunchDescription variable
    ld = LaunchDescription()

    # Launch nodes
    ld.add_action(nav_container)
    ld.add_action(lifecycle_manager)
    ld.add_action(localization_launch)
    ld.add_action(twist_stamper_node)
    #temp
    ld.add_action(base_to_footprint)

    return ld
