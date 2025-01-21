import numpy as np
from utils.core_types import *

import pybullet as p


class EnvWrapper:
    """just create a wrapper to store the environment - so that we don't have to pass it as an argument to every function call..."""

    def __init__(self, env: Environment):
        self.env = env

    def get_object_pose(self, obj: TaskObject) -> Pose:
        """returns the pose (Point3d, Rotation) of a given object in the environment."""
        return _from_pybullet_pose(self.env.get_object_pose(obj.id))

    def get_end_effector_pose(self) -> Pose:
        """gets the current pose of the end effector"""
        return _from_pybullet_pose(self.env.get_ee_pose())

    def get_bbox(self, obj: TaskObject) -> AABBBoundingBox:
        """gets the bounding box of an object"""
        aabb_min, aabb_max = self.env.getBoundingBox(obj.id)

        return AABBBoundingBox(Point3D.from_xyz(aabb_min), Point3D.from_xyz(aabb_max))

    def get_objects(self) -> list[TaskObject]:
        """gets all objects in the environment"""
        return self.env.task.objs

    def move_end_effector_to(self, pose: Pose) -> bool:
        """moves the end effector from its current position to a given new position"""
        ee_pose = self.get_end_effector_pose()

        max_steps = 100
        step = 0
        while (
            np.linalg.norm(pose.position.np_vec - ee_pose.position.np_vec) > 0.01
            and step < max_steps
        ):
            self.env.movep(_to_pybullet_pose(pose))
            self.env.step_simulation()
            ee_pose = self.get_end_effector_pose()
            step += 1

    def put_first_on_second(self, pickPose: Pose, placePose: Pose):
        """
        This is the main pick-and-place primitive.
        It allows you to pick up the TaskObject at 'pickPose', and place it at the Pose specified by 'placePose'.
        If 'placePose' is occupied, it places the object on top of 'placePose.
        """
        return self.env.step(
            action={
                "pose0": _to_pybullet_pose(pickPose),
                "pose1": _to_pybullet_pose(placePose),
            }
        )

    def say(self, msg: str):
        """prints a message for the user to the terminal"""
        msg = f"robot says: {msg}"
        print(msg)
        return msg


def _from_pybullet_pose(pose) -> Pose:
    return Pose(
        position=Point3D.from_xyz(pose[0]), rotation=Rotation.from_quat(pose[1])
    )


def _to_pybullet_pose(pose: Pose):
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
            "video_width": 720,
        },
    )
    from tasks.many_blocks import ManyBlocksTask

    env.set_task(ManyBlocksTask())
    env.reset()

    wrapped_env = EnvWrapper(env)

    zone = wrapped_env.get_objects()[0]
    bbox = wrapped_env.get_bbox(zone)

    import time

    time.sleep(10)
