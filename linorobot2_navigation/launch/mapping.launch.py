"""매핑 모드: slam_toolbox + Nav2.

slam_toolbox가 /map을 동적으로 발행, Nav2가 동시에 동작 (teleop 또는 Nav2 goal로 주행하며 매핑).
시연 전날 강당에서 맵을 만들 때 사용한 뒤 map_saver_cli로 저장.

사용 예:
  ros2 launch linorobot2_navigation mapping.launch.py use_sim_time:=true   # 시뮬
  ros2 launch linorobot2_navigation mapping.launch.py                       # 실 로봇

매핑 완료 후 저장:
  ros2 run nav2_map_server map_saver_cli -f ~/rp_ws/src/linorobot2/linorobot2_navigation/maps/venue_map
"""
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
            description='시뮬은 true, 실 로봇은 false',
        ),

        # slam_toolbox: /map 동적 발행
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(slam_launch_path),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
            }.items(),
        ),

        # Nav2: 동적 맵 위에서 경로 계획
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch_path),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'params_file': params_file,
            }.items(),
        ),
    ])
