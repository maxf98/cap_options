import numpy as np
from utils.core_types import *
import time


__all__ = ["get_object_pose", "move_end_effector_to", "get_end_effector_pose", "put_first_on_second", "get_bbox", "get_objects", "say"] 


def get_object_pose(env: Environment, obj: TaskObject) -> Pose:
    """
    returns the pose (Point3d, Rotation) of a given object in the environment.
    """
    return from_pybullet_pose(env.get_object_pose(obj.id))
    

def move_end_effector_to(env, pose: Pose) -> bool:
    """
    moves the end effector from its current position to a given new position
    """
    ee_pose = get_end_effector_pose(env)

    while np.linalg.norm(pose.position.np_vec - ee_pose.position.np_vec) > 0.01:
        env.movep(to_pybullet_pose(pose))
        env.step_simulation()
        ee_pose = get_end_effector_pose(env)

def get_end_effector_pose(env: Environment) -> Pose:
    """
    gets the current pose of the end effector
    """
    return from_pybullet_pose(env.get_ee_pose())

def put_first_on_second(env: Environment, pickPose: Pose, placePose: Pose):
    """
    attempts to pick up an object at {pickPose}, and to place it at {placePose}
    """
    return env.step(action={"pose0": to_pybullet_pose(pickPose), "pose1": to_pybullet_pose(placePose)})

def get_bbox(env, obj: TaskObject):
    """
    gets the bounding box of an object as a 6-tuple (minX, maxX, minY, maxY, minZ, maxZ)
    """
    return env.get_bounding_box(obj.id)

def get_objects(env: Environment) -> list[TaskObject]:
    """
    gets all objects in the environment
    """
    return env.task.objs

def say(msg):
    """
    prints a message for the user to the terminal
    """
    msg = f'robot says: {msg}'
    print(msg)
    return msg

def np_vec(point: Point3D) -> np.ndarray:
    return np.ndarray([point.x, point.y, point.z])


def from_pybullet_pose(pose) -> Pose:
    return Pose(position=Point3D.from_xyz(pose[0]), rotation=Rotation.from_quat(pose[1]))

def to_pybullet_pose(pose: Pose):
    xyz = (pose.position.x, pose.position.y, pose.position.z)
    return (xyz, pose.rotation.as_quat())


if __name__ == "__main__":
    env = Environment(
        "/Users/maxfest/vscode/thesis/ravens/environments/assets",
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
            "video_width": 720
        }
    )
    from tasks.many_blocks import ManyBlocksTask
    env.set_task(ManyBlocksTask())
    env.reset()

    objects = get_objects(env)
    print(get_bbox(env, objects[0]))
    pose = get_object_pose(env, objects[0])
    pose1 = get_object_pose(env, objects[1])
    print(pose.position.x)

    print(to_pybullet_pose(pose))

    put_first_on_second(env, pose, pose1)

    time.sleep(3)

    move_end_effector_to(env, get_object_pose(env, objects[3]))

    time.sleep(3)

    move_end_effector_to(env, get_object_pose(env, objects[8]))
