"""자율주행 모드: map_server + AMCL + Nav2 (SLAM 없음).

저장된 맵 위에서 AMCL이 위치 추정, Nav2가 경로 계획·추종.
시연 당일 사용 — SLAM이 꺼져 있어 관객 영향으로 맵이 망가질 위험 없음.

사용 예:
  # 기본: aed_corridor 맵 (시뮬용)
  ros2 launch linorobot2_navigation navigation.launch.py use_sim_time:=true

  # 다른 맵 지정 (실 로봇)
  ros2 launch linorobot2_navigation navigation.launch.py \\
    use_sim_time:=false map:=/path/to/venue_map.yaml

RViz의 "2D Pose Estimate"로 초기 위치 보정 필수.
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from nav2_common.launch import RewrittenYaml


def _setup(context):
    nav_pkg = get_package_share_directory('linorobot2_navigation')
    bt_xml = os.path.join(nav_pkg, 'behavior_trees', 'navigate_w_obstacle_wait.xml')
    src_params = os.path.join(nav_pkg, 'config', 'navigation_sim.yaml')

    params_file = RewrittenYaml(
        source_file=src_params,
        param_rewrites={'default_nav_to_pose_bt_xml': bt_xml},
        convert_types=True,
    )

    localization_launch_path = PathJoinSubstitution(
        [FindPackageShare('nav2_bringup'), 'launch', 'localization_launch.py']
    )
    nav2_launch_path = PathJoinSubstitution(
        [FindPackageShare('nav2_bringup'), 'launch', 'navigation_launch.py']
    )

    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(localization_launch_path),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'map': LaunchConfiguration('map'),
                'params_file': params_file,
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch_path),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'params_file': params_file,
            }.items(),
        ),
    ]


def generate_launch_description():
    default_map = PathJoinSubstitution(
        [FindPackageShare('linorobot2_navigation'), 'maps', 'aed_corridor.yaml']
    )
    return LaunchDescription([
        DeclareLaunchArgument(
            name='use_sim_time',
            default_value='true',
            description='시뮬은 true, 실 로봇은 false',
        ),
        DeclareLaunchArgument(
            name='map',
            default_value=default_map,
            description='맵 yaml 파일 경로 (기본: aed_corridor.yaml)',
        ),
        OpaqueFunction(function=_setup),
    ])
