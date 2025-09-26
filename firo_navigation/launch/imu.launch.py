import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
def generate_launch_description():
    ld = LaunchDescription()
    config = os.path.join(
        get_package_share_directory('firo_navigation'),
        'config',
        'imu_params.yaml'
        )

    # imu node   
    node=Node(
        package = 'bno055',
        executable = 'bno055',
        name= "bno055",
        parameters = [config]
    )

    # temp transform
    base_to_imu = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_imu',
        output='screen',
        arguments=['0.025', '0', '0.023','3.14159', '0', '0', 'torso', 'imu_link']
    )

    ld.add_action(node)
    ld.add_action(base_to_imu)
    return ld