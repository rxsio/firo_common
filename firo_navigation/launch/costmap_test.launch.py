import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    # Define LaunchDescription variable
    ld = LaunchDescription()

    # Costmaps configuration file
    costmap_config_path = os.path.join(
        get_package_share_directory('firo_navigation'),
        'config',
        'costmap_params.yaml'
    )

        # GLOBAL costmap -> planner
    planner = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[costmap_config_path]
     )
    # LCOAL costmap -> controller
    controller = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[costmap_config_path]
     )


        # Lifecycle Manager (dla obu costmap)
    lc_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_costmaps',
        output='screen',
        parameters=[{
                'use_sim_time': False,
                'autostart': True,
                'node_names': ['planner_server', 'controller_server'] 
        }]
     )


    ld.add_action(planner)
    ld.add_action(controller)
    ld.add_action(lc_manager)

    return ld