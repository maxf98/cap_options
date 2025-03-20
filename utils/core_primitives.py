import numpy as np
from utils.core_types import *
from utils.core_types import _from_pybullet_pose, _to_pybullet_pose
import utils.general_utils as utils

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

env = Environment(
    "/Users/maxfest/vscode/thesis/thesis/environments/assets",
    disp=True,
    shared_memory=False,
    hz=480,
    record_cfg={
        "save_video": False,
        "save_video_path": "${data_dir}/${task}-cap/videos/",
        "add_text": True,
        "add_task_text": True,
        "fps": 20,
        "video_height": 640,
        "video_width": 720,
    },
)
from tasks.tasks.place_blocks import Place5Blocks
from environments.grippers import Spatula

task = Place5Blocks()
# task.ee = Spatula

env.set_task(task)
env.reset()
"""-----------------------------------------------------------------------------"""

__all__ = [
    "get_objects",
    "get_object_size",
    "get_object_pose",
    "get_end_effector_pose",
    "put_first_on_second",
    "say",
    "move_end_effector_to",
    "get_bbox",
    "get_point_at_distance_and_rotation_from_point",
    "activate_end_effector",
    "release_end_effector",
    "check_grasp",
    "pick",
]


def get_object_pose(obj: TaskObject) -> Pose:
    """returns the pose (Point3d, Rotation) of a given object in the environment."""
    return _from_pybullet_pose(env.get_object_pose(obj.id))


def get_object_size(task_object: TaskObject) -> tuple[float, float, float]:
    """Returns the size of the given TaskObject as a tuple (width, depth, height)."""
    return task_object.size


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


def move_end_effector_to(pose: Pose, speed=0.001):
    """moves the end effector from its current Pose to a given new Pose"""
    suction_height = 0.05
    pose0 = _to_pybullet_pose(get_end_effector_pose())
    pose1 = _to_pybullet_pose(pose)
    pos0 = np.float32(pose0[0])
    pos1 = np.float32((pose1[0][0], pose1[0][1], pose1[0][2] + suction_height))
    vec = np.float32(pos1) - np.float32(pos0)
    length = np.linalg.norm(vec)
    vec = vec / length
    pos0 -= vec * 0.02
    pos1 -= vec * 0.05

    rot = (pose1[1] + np.pi) % (2 * np.pi) - np.pi
    timeout = env.movep((pos0, rot))

    n_push = np.int32(np.floor(np.linalg.norm(pos1 - pos0) / 0.01))
    for _ in range(n_push):
        target = pos0 + vec * n_push * 0.01
        timeout |= env.movep((target, rot), speed=speed)
    timeout |= env.movep((pos1, rot), speed=speed)


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


def get_point_at_distance_and_rotation_from_point(
    point: Point3D, rotation: Rotation, distance: float, direction=np.array([1, 0, 0])
) -> Point3D:
    """compute a point that is at a specific 'distance' from 'point', at a specified 'rotation'
    The direction specifies the base direction in which to apply the rotation.
    This is useful for placing objects relative to other objects.
    """

    rotated_direction = rotation.apply(direction)
    new_point = point.np_vec + distance * rotated_direction
    return Point3D.from_xyz(new_point)


def say(msg: str):
    """prints a message for the user to the terminal"""
    msg = f"robot says: {msg}"
    print(msg)
    return msg


def activate_end_effector():
    """activates the gripper - if there is an object in contact with the gripper, it will grasp this object
    if there is no object, it just won't work"""
    env.ee.activate()


def release_end_effector():
    """releases the end effector, and any object that was previously grasped"""
    import time

    env.ee.release()
    for _ in range(500):
        p.stepSimulation()
        time.sleep(1 / 400)


def check_grasp() -> bool:
    """checks whether the gripper is currently holding an object"""
    return env.ee.check_grasp()


def pick(object: TaskObject) -> bool:
    """moves end effector to the pick pose and activates"""
    object_pose = get_object_pose(object)
    size = get_object_size(object)
    pick_pose = Pose(
        object_pose.position.translate(Point3D(0, 0, size[2] / 2)), object_pose.rotation
    )
    pick_pose = _to_pybullet_pose(pick_pose)
    speed = 0.001
    # Execute picking primitive.
    prepick_to_pick = ((0, 0, 0.32), (0, 0, 0, 1))
    prepick_pose = utils.multiply(pick_pose, prepick_to_pick)
    timeout = env.movep(prepick_pose, speed)

    # Move towards pick pose until contact is detected.
    delta = (np.float32([0, 0, -0.001]), utils.eulerXYZ_to_quatXYZW((0, 0, 0)))
    targ_pose = prepick_pose
    while not env.ee.detect_contact():  # and target_pose[2] > 0:
        targ_pose = utils.multiply(targ_pose, delta)
        timeout |= env.movep(targ_pose)
        if timeout:
            return True

    # Activate end effector, move up, and check picking success.
    env.ee.activate()
    pick_success = env.ee.check_grasp()
    return pick_success


if __name__ == "__main__":

    import time

    move_end_effector_to(Pose(Point3D(0.5, 0.5, 0.05)), speed=0.001)
    move_end_effector_to(Pose(Point3D(0.5, -0.5, 0.05)), speed=0.001)
