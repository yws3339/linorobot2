import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


MAP_NAME = 'depot_slam'  # change to the name of your own map here


def generate_launch_description():
    depth_sensor = os.getenv('LINOROBOT2_DEPTH_SENSOR', '')

    nav2_launch_path = PathJoinSubstitution(
        [FindPackageShare('nav2_bringup'), 'launch', 'bringup_launch.py']
    )

    rviz_config_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_navigation'), 'rviz', 'linorobot2_navigation.rviz']
    )

    default_map_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_navigation'), 'maps', f'{MAP_NAME}.yaml']
    )

    # sim=true → navigation_sim.yaml, sim=false → navigation.yaml
    sim_config_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_navigation'), 'config', 'navigation_sim.yaml']
    )
    real_config_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_navigation'), 'config', 'navigation.yaml']
    )

    nav2_sim_config_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_navigation'), 'config', 'navigation_sim.yaml']
    )


    return LaunchDescription([
        DeclareLaunchArgument(
            name='sim',
            default_value='true',
            description='true=시뮬레이션, false=실물 로봇'
        ),

        DeclareLaunchArgument(
            name='rviz',
            default_value='false',
            description='Run rviz'
        ),

        DeclareLaunchArgument(
            name='map',
            default_value=default_map_path,
            description='Navigation map path'
        ),

        DeclareLaunchArgument(
            name='initial_pose_x',
            default_value='0.0',
            description='Initial robot X position'
        ),

        DeclareLaunchArgument(
            name='initial_pose_y',
            default_value='0.0',
            description='Initial robot Y position'
        ),

        DeclareLaunchArgument(
            name='initial_pose_yaw',
            default_value='0.0',
            description='Initial robot yaw'
        ),

        # 시뮬용 (sim:=true)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch_path),
            condition=IfCondition(LaunchConfiguration('sim')),
            launch_arguments={
                'map': LaunchConfiguration('map'),
                'use_sim_time': 'true',
                'params_file': sim_config_path,
                'initial_pose_x': LaunchConfiguration('initial_pose_x'),
                'initial_pose_y': LaunchConfiguration('initial_pose_y'),
                'initial_pose_yaw': LaunchConfiguration('initial_pose_yaw'),
            }.items()
        ),

        # 실물용 (sim:=false)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch_path),
            condition=UnlessCondition(LaunchConfiguration('sim')),
            launch_arguments={
                'map': LaunchConfiguration('map'),
                'use_sim_time': 'false',
                'params_file': real_config_path,
                'initial_pose_x': LaunchConfiguration('initial_pose_x'),
                'initial_pose_y': LaunchConfiguration('initial_pose_y'),
                'initial_pose_yaw': LaunchConfiguration('initial_pose_yaw'),
            }.items()
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_path],
            condition=IfCondition(LaunchConfiguration('rviz')),
            parameters=[{'use_sim_time': LaunchConfiguration('sim')}]
        ),
    ])
