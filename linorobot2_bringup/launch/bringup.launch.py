# Copyright (c) 2021 Juan Miguel Jimeno
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition


def generate_launch_description():
    ekf_config_path = PathJoinSubstitution(
        [FindPackageShare("linorobot2_base"), "config", "ekf.yaml"]
    )

    description_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_description'), 'launch', 'description.launch.py']
    )

    perception_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'perception.launch.py']
    )

    extra_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'extra.launch.py']
    )

    joy_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'joy_teleop.launch.py']
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            name='odom_topic',
            default_value='/odom',
            description='EKF out odometry topic'
        ),

        DeclareLaunchArgument(
            name='madgwick',
            default_value='false',
            description='Use madgwick to fuse imu and magnetometer'
        ),

        DeclareLaunchArgument(
            name='orientation_stddev',
            default_value='0.003162278',
            description='Madgwick orientation stddev'
        ),

        DeclareLaunchArgument(
            name='extra',
            default_value='false',
            description='Launch extra launch file (e.g. laser filter)'
        ),

        DeclareLaunchArgument(
            name='joy',
            default_value='false',
            description='Use Joystick'
        ),

        # EKF
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[ekf_config_path],
            remappings=[("odometry/filtered", LaunchConfiguration("odom_topic"))]
        ),

        # Madgwick (선택)
        Node(
            condition=IfCondition(LaunchConfiguration("madgwick")),
            package='imu_filter_madgwick',
            executable='imu_filter_madgwick_node',
            name='madgwick_filter_node',
            output='screen',
            parameters=[{
                'orientation_stddev': LaunchConfiguration('orientation_stddev'),
                'publish_tf': False
            }]
        ),

        # URDF + robot_state_publisher + joint_state_publisher
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(description_launch_path),
        ),

        # ODrive (주행 모터)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [FindPackageShare('odrive_bridge'), 'launch', 'odrive_bridge.launch.py']
                )
            ),
        ),

        # IMU
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [FindPackageShare('imu_publisher'), 'launch', 'imu.launch.py']
                )
            ),
        ),

        # Optical Flow
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [FindPackageShare('optical_flow_publisher'), 'launch', 'optical_flow.launch.py']
                )
            ),
        ),

        # 인지 (카메라 등)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(perception_launch_path),
        ),

        # 추가 (선택)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(extra_launch_path),
            condition=IfCondition(LaunchConfiguration("extra")),
        ),

        # 조이스틱 (선택)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(joy_launch_path),
            condition=IfCondition(LaunchConfiguration("joy")),
        ),

        # 경광봉(beacon_node)은 별도 실행:
        # ros2 launch vesc_bridge beacon.launch.py
    ])
