import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    # robot localization configuration 
    loc_config_path = os.path.join(
        get_package_share_directory('firo_navigation'),
        'config',
        'localization_params.yaml'
    )

    # local robot localization node - no-lifecycle possibility
    local_localization_node = Node(
        package='robot_localization', 
        executable='ekf_node', 
        name='ekf_filter_node_odom',
        output='screen',
        parameters=[loc_config_path],
        remappings=[('odometry/filtered', 'ekf/local')],
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
        remappings=[('odometry/filtered', 'ekf/global')],
        respawn=True,
        arguments=['--ros-args', '--log-level', 'info'] 
    )

    # Define LaunchDescription variable
    ld = LaunchDescription()
    # Launch robot localization nodes
    ld.add_action(local_localization_node)
    ld.add_action(global_localization_node)
    return ld