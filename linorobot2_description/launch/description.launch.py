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

import os
import re
import subprocess
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def sanitized_urdf(path):
    """xacro 결과에서 XML 선언과 주석을 제거하고 한 줄로 만든다.

    gazebo_ros2_control은 robot_description을 controller_manager에
    `--param robot_description:=<xml>` 로 재전달하고 rcl이 이를 YAML로 파싱한다.
    XML 선언·주석(특히 비ASCII)이 있으면 파싱이 깨져 controller_manager가 뜨지 않는다.
    """
    urdf = subprocess.check_output(['xacro', path]).decode()
    urdf = re.sub(r'<\?xml[^>]*\?>', '', urdf)
    urdf = re.sub(r'<!--.*?-->', '', urdf, flags=re.DOTALL)
    return ' '.join(urdf.split())


def launch_setup(context, *args, **kwargs):
    urdf_path = LaunchConfiguration('urdf').perform(context)
    use_sim_time = LaunchConfiguration('use_sim_time')

    rviz_config_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_description'), 'rviz', 'description.rviz']
    )

    return [
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            condition=IfCondition(LaunchConfiguration('publish_joints')),
            parameters=[{'use_sim_time': use_sim_time}]
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'robot_description': sanitized_urdf(urdf_path),
            }]
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_path],
            condition=IfCondition(LaunchConfiguration('rviz')),
            parameters=[{'use_sim_time': use_sim_time}]
        ),
    ]


def generate_launch_description():
    robot_base = os.getenv('LINOROBOT2_BASE')
    if not robot_base:
        raise RuntimeError(
            "LINOROBOT2_BASE 환경변수가 설정되지 않았습니다. "
            "예: export LINOROBOT2_BASE=2wd (~/.bashrc에 영구 설정 권장)"
        )

    urdf_path = PathJoinSubstitution(
        [FindPackageShare("linorobot2_description"), "urdf/robots", f"{robot_base}.urdf.xacro"]
    )

    return LaunchDescription([
        DeclareLaunchArgument(name='urdf', default_value=urdf_path, description='URDF path'),
        DeclareLaunchArgument(name='publish_joints', default_value='true',
                              description='Launch joint_states_publisher'),
        DeclareLaunchArgument(name='rviz', default_value='false', description='Run rviz'),
        DeclareLaunchArgument(name='use_sim_time', default_value='false',
                              description='Use simulation time'),
        OpaqueFunction(function=launch_setup),
    ])
