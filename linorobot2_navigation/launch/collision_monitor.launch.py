"""collision_monitor 상시 인라인 안전 필터.

velocity_smoother 출력(/cmd_vel)을 받아 충돌 임박 시 정지시키고 /cmd_vel_safe로 발행.
nav2 본체와 분리된 전용 lifecycle_manager로 관리.

사용 예:
  # 시뮬
  ros2 launch linorobot2_navigation collision_monitor.launch.py use_sim_time:=true
  # 실물
  ros2 launch linorobot2_navigation collision_monitor.launch.py use_sim_time:=false
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    nav_pkg = get_package_share_directory('linorobot2_navigation')
    params_file = os.path.join(nav_pkg, 'config', 'collision_monitor.yaml')

    configured_params = RewrittenYaml(
        source_file=params_file,
        param_rewrites={'use_sim_time': use_sim_time},
        convert_types=True,
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            name='use_sim_time',
            default_value='true',
            description='시뮬은 true, 실 로봇은 false',
        ),
        Node(
            package='nav2_collision_monitor',
            executable='collision_monitor',
            name='collision_monitor',
            output='screen',
            parameters=[configured_params],
        ),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_collision_monitor',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'autostart': True,
                'node_names': ['collision_monitor'],
            }],
        ),
    ])
