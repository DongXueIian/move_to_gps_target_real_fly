import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription,GroupAction, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node,PushRosNamespace
from launch_ros.descriptions import ParameterFile
from nav2_common.launch import ReplaceString, RewrittenYaml
from pathlib import Path


def generate_launch_description():
    move_to_gps_target_real_fly_dir = get_package_share_directory('move_to_gps_target_real_fly')
    ld = LaunchDescription()
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=[
            "-d",
            f'{Path(move_to_gps_target_real_fly_dir) / "rviz2" / "240508_real_fly_settting.rviz"}',
        ],
        parameters=[{'use_sim_time': False}],
    )


    not_height_tf_transform_cmd=Node(
            package='move_to_gps_target_real_fly',
            executable='gztf_filter_not_height',
            name='not_height_tf_transform',
            output='screen',
            respawn=False,
    )

    script_path = os.path.join(move_to_gps_target_real_fly_dir, 'launch', 'ros2_recorder.sh')
    # 确保脚本有执行权限
    os.chmod(script_path, 0o775)
    ros2_recorder_setup_cmd = TimerAction(
        period=10.0,  # 延迟时间（单位：秒）
        actions=[
            ExecuteProcess(
                cmd=['bash', script_path],
                output='screen',
                shell=True
            )
        ]
    )

    # 构建 Python 脚本的完整路径
    apm_controller_script = Path(move_to_gps_target_real_fly_dir) / "launch" / "apm_keyborad_controller.py"

    # 启动新的命令行窗口并执行 Python 脚本
    apm_controller_process = ExecuteProcess(
        cmd=['gnome-terminal', '--', 'bash', '-c', f'python3 {apm_controller_script}; exec bash'],
        output='screen'
    )


    ld.add_action(rviz)
    # ld.add_action(not_height_tf_transform_cmd)
    ld.add_action(apm_controller_process)
    # ld.add_action(ros2_recorder_setup_cmd)


    return ld