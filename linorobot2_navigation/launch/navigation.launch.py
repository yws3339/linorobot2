"""SLAM 모드 + Nav2 (map_server 없이 SLAM이 발행하는 /map 사용).

기본은 시뮬레이션 모드 (use_sim_time:=true).
실 로봇은 use_sim_time:=false 로 호출.
"""
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    nav2_launch_path = PathJoinSubstitution(
        [FindPackageShare('nav2_bringup'), 'launch', 'navigation_launch.py']
    )
    slam_launch_path = PathJoinSubstitution(
        [FindPackageShare('slam_toolbox'), 'launch', 'online_async_launch.py']
    )
    params_file = PathJoinSubstitution(
        [FindPackageShare('linorobot2_navigation'), 'config', 'navigation_sim.yaml']
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            name='use_sim_time',
            default_value='true',
            description='시뮬은 true, 실 로봇은 false'
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(slam_launch_path),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
            }.items()
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch_path),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'params_file': params_file,
            }.items()
        ),
    ])
