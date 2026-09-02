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
                # ⚠️ 두 조건을 동시에 만족해야 한다. 어기면 조용히 실패한다.
                #  1) L515 depth 는 **30Hz 만** 지원한다(1024x768/640x480/320x240
                #     전부 @30). 15 를 주면 "Given value ... is invalid" 를 찍고
                #     640x480x30 으로 되돌아간다. 즉 여기 적은 값은 무시된다.
                #  2) 해상도가 rgb_camera.profile 과 **같아야** 한다.
                #     approach_fallen._read_depth 는 컬러 이미지 좌표(u,v)를 깊이
                #     이미지에 스케일 없이 그대로 인덱싱한다. 320x240 으로 두면
                #     좌표가 범위를 벗어나 depth 를 못 읽고 검출을 통째로 버린다.
                'depth_module.profile': '640,480,30',
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

