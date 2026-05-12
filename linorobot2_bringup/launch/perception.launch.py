from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        DeclareLaunchArgument(
            name='use_sim_time',
            default_value='false',
            description='Use simulation clock'
        ),
        # STVL(SpatioTemporalVoxelLayer)이 L515 PointCloud2를 직접 수신하므로
        # pointcloud_to_laserscan 변환 노드 불필요
    ])
