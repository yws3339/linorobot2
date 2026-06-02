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
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution, PythonExpression, LaunchConfiguration, EqualsSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition, LaunchConfigurationEquals
from launch_ros.actions import Node


def generate_launch_description():
    zed_sensors = ['zed', 'zed2', 'zed2i', 'zedm']
    zed_common_config_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'config', 'zed_common.yaml']
    )

    oakd_sensors = ['oakd', 'oakdlite', 'oakdpro']
    to_oakd_vars = {
        "oakd": "OAK-D",
        "oakdlite": "OAK-D-LITE",
        "oakdpro": "OAK-D-PRO"
    }
    return LaunchDescription([
        DeclareLaunchArgument(
            name='sensor',
            default_value='realsense',
            description='Sensor to launch'
        ),
        DeclareLaunchArgument(
            name='pointcloud',
            default_value='false',
            description='pointcloud 생성 (SLAM 매핑 시에만 true — 자율주행은 라이다 전용이라 불필요)'
        ),
        DeclareLaunchArgument(
            name='enable_color',
            default_value='true',
            description='RGB 스트림 활성화 (도착 후 인지 게이팅 — aed_start는 false로 기동)'
        ),
        DeclareLaunchArgument(
            name='enable_depth',
            default_value='true',
            description='Depth 스트림 활성화 (도착 후 인지 게이팅 — aed_start는 false로 기동)'
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(PathJoinSubstitution(
                [FindPackageShare('realsense2_camera'), 'launch', 'rs_launch.py']
            )),
            condition=LaunchConfigurationEquals('sensor', 'realsense'),
            launch_arguments={
                'pointcloud.enable': LaunchConfiguration('pointcloud'),
                'ordered_pc': 'true',
                'initial_reset': 'false',
                'depth_module.profile': '320,240,15',
                'rgb_camera.profile': '640,480,15',
                'align_depth.enable': 'false',
                'depth_module.global_time_enabled': 'true',
                'rgb_camera.global_time_enabled': 'true',
                'enable_color': LaunchConfiguration('enable_color'),
                'enable_depth': LaunchConfiguration('enable_depth')
            }.items()
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(PathJoinSubstitution(
                [FindPackageShare('zed_wrapper'), 'launch/include', 'zed_camera.launch.py']
            )),
            condition=IfCondition(PythonExpression(['"', LaunchConfiguration('sensor'), '" in "', str(zed_sensors), '"'])),
            launch_arguments={
                'camera_model': LaunchConfiguration('sensor'),
                'config_common_path': zed_common_config_path,
                'camera_name': '',
                'node_name': 'zed',
                'publish_urdf': 'true',
                'base_frame': 'camera_link'
            }.items()   
        ),
        
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(PathJoinSubstitution(
                [FindPackageShare('depthai_examples'), 'launch', 'stereo.launch.py']
            )),
            condition=IfCondition(PythonExpression(['"', LaunchConfiguration('sensor'), '" in "', str(oakd_sensors), '"'])),
            launch_arguments={
                'camera_model': to_oakd_vars.get(LaunchConfiguration('sensor'), None),              
            }.items()   
        ),
    ])

