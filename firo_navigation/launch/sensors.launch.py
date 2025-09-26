import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    # Include lidar launch
    lidar_launch = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource([
            get_package_share_directory('firo_navigation'),
            '/launch/lidar.launch.py'
        ])
    )

    # Include lidar odometry launch
    lidar_odom_launch = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource([
            get_package_share_directory('firo_navigation'),
            '/launch/lidar_odometry.launch.py'
        ])
    )

    # Include imu launch
    imu_launch = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource([
            get_package_share_directory('firo_navigation'),
            '/launch/imu.launch.py'
        ])
    )
    

    # Define LaunchDescription variable
    ld = LaunchDescription()
    # Call launches
    ld.add_action(lidar_launch)
    ld.add_action(lidar_odom_launch)
    ld.add_action(imu_launch)
    return ld