import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node, LifecycleNode


def generate_launch_description():
    
    # slam toolbox configuration 
    slam_config_path = os.path.join(
        get_package_share_directory('firo_navigation'),
        'config',
        'slam_params.yaml'
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
                 ('/pose', '/pose_global')
           ]        
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
    # Launch SLAM Toolbox node
    ld.add_action(slam_toolbox_node)
    # Launch static transfrom publisher nodes
    ld.add_action(base_to_footprint)
    return ld
