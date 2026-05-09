import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        DeclareLaunchArgument(
            name='use_sim_time',
            default_value='false',
            description='Use simulation clock'
        ),

        Node(
            package='pointcloud_to_laserscan',
            executable='pointcloud_to_laserscan_node',
            name='pointcloud_to_laserscan_low',
            parameters=[{
                'use_sim_time': use_sim_time,
                'target_frame': 'base_link',
                'transform_tolerance': 0.05,
                'min_height': 0.05,
                'max_height': 0.50,
                'angle_min': -1.0472,
                'angle_max':  1.0472,
                'angle_increment': 0.0087,
                'scan_time': 0.1,
                'range_min': 0.25,
                'range_max': 8.0,
                'use_inf': True,
            }],
            remappings=[
                ('cloud_in', '/camera/depth/color/points'),
                ('scan', '/scan_low'),
            ],
        ),

        Node(
            package='pointcloud_to_laserscan',
            executable='pointcloud_to_laserscan_node',
            name='pointcloud_to_laserscan_high',
            parameters=[{
                'use_sim_time': use_sim_time,
                'target_frame': 'base_link',
                'transform_tolerance': 0.05,
                'min_height': 0.50,
                'max_height': 1.50,
                'angle_min': -1.0472,
                'angle_max':  1.0472,
                'angle_increment': 0.0087,
                'scan_time': 0.1,
                'range_min': 0.25,
                'range_max': 8.0,
                'use_inf': True,
            }],
            remappings=[
                ('cloud_in', '/camera/depth/color/points'),
                ('scan', '/scan_high'),
            ],
        ),
    ])
