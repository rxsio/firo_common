import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration

def generate_launch_description():

    # Lidar odometry configuration file
    odom_config_path = os.path.join(
        get_package_share_directory('firo_navigation'),
        'config',
        'lidar_odom_params.yaml'
    )

    lidar_odom_node = Node(
        package='rf2o_laser_odometry',
        executable='rf2o_laser_odometry_node',
        name='rf2o_laser_odometry',
        output='screen',
        parameters=[
            odom_config_path
        ]
    )

    lidar_odom_fixer_node = Node(
        package='firo_navigation',
        executable='lidar_odom_cov_fixer_node',
        name='rf2o_laser_odometry_fixer',
        output='screen',
        parameters=[
            odom_config_path
        ]
    )

    # Define LaunchDescription variable
    ld = LaunchDescription()

    # Launch lidar odom node
    ld.add_action(lidar_odom_node)

    # Launch lidar odom covariance fixer node
    ld.add_action(lidar_odom_fixer_node)


    return ld
