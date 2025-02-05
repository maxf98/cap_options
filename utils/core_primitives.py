import numpy as np
from utils.core_types import *
from utils.core_types import _from_pybullet_pose, _to_pybullet_pose

import pybullet as p

"""
-----------------------------------------------------------------------------
the following functions require an initialised environment - 
the agent doesn't need to know anything about the environment, only what methods are available to it
we are responsible for properly initialising the environment, and ensuring that the agent has access to it
"""

"""
IMPORTANT
- pybullet can only handle one server at a time, if this is not commented out, this is the environment being used
"""

# env = Environment(
#     "/Users/maxfest/vscode/thesis/ravens/environments/assets",
#     disp=True,
#     shared_memory=False,
#     hz=480,
#     record_cfg={
#         "save_video": False,
#         "save_video_path": "${data_dir}/${task}-cap/videos/",
#         "add_text": True,
#         "add_task_text": True,
#         "fps": 20,
#         "video_height": 640,
#         "video_width": 720,
#     },
# )
# from tasks.task import Task

# env.set_task(Task())
# env.reset()
"""-----------------------------------------------------------------------------"""


__all__ = [
    "get_objects",
    "get_object_pose",
    "get_end_effector_pose",
    "put_first_on_second",
    "say",
    "move_end_effector_to",
    "get_bbox",
]


def get_object_pose(obj: TaskObject) -> Pose:
    """returns the pose (Point3d, Rotation) of a given object in the environment."""
    return _from_pybullet_pose(env.get_object_pose(obj.id))


def get_end_effector_pose() -> Pose:
    """gets the current pose of the end effector"""
    return _from_pybullet_pose(env.get_ee_pose())


def get_bbox(obj: TaskObject) -> AABBBoundingBox:
    """gets the axis-aligned bounding box of an object - this is useful primarily for collision detection"""
    aabb_min, aabb_max = env.get_bounding_box(obj.id)

    return AABBBoundingBox(Point3D.from_xyz(aabb_min), Point3D.from_xyz(aabb_max))


def get_objects() -> list[TaskObject]:
    """gets all objects in the environment"""
    return env.task.taskObjects


def move_end_effector_to(pose: Pose):
    """moves the end effector from its current position to a given new position"""
    ee_pose = get_end_effector_pose()

    max_steps = 100
    step = 0
    while (
        not np.allclose(pose.position.np_vec, ee_pose.position.np_vec, atol=1e-3)
        or not np.allclose(
            pose.rotation.as_matrix(), ee_pose.rotation.as_matrix(), atol=1e-3
        )
    ) and step < max_steps:
        env.movep(_to_pybullet_pose(pose), speed=0.0005)
        env.step_simulation()
        ee_pose = get_end_effector_pose()
        step += 1


def put_first_on_second(pickPose: Pose, placePose: Pose):
    """
    This is the main pick-and-place primitive.
    It allows you to pick up the TaskObject at 'pickPose', and place it at the Pose specified by 'placePose'.
    If 'placePose' is occupied, it places the object on top of 'placePose.
    """
    return env.step(
        action={
            "pose0": _to_pybullet_pose(pickPose),
            "pose1": _to_pybullet_pose(placePose),
        }
    )


def say(msg: str):
    """prints a message for the user to the terminal"""
    msg = f"robot says: {msg}"
    print(msg)
    return msg


if __name__ == "__main__":

    import time

    move_end_effector_to(
        Pose(
            position=Point3D(0.3, 0.3, 0.3),
            rotation=Rotation.from_euler("xyz", [0, 0, 0]),
        )
    )

    time.sleep(2)

    move_end_effector_to(
        Pose(
            position=Point3D(0.5, 0.1, 0.1),
            rotation=Rotation.from_euler("xyz", [0, 45, 0]),
        )
    )

    time.sleep(2)

    move_end_effector_to(
        Pose(
            position=Point3D(0.5, 0.1, 0.3),
            rotation=Rotation.from_euler("xyz", [0, -45, 0]),
        )
    )

    time.sleep(2)
