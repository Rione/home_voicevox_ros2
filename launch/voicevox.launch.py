from launch_ros.actions import Node

from launch import LaunchDescription


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="voicevox_ros2",
                executable="voicevox_node",
                output="screen",
            ),
        ]
    )
