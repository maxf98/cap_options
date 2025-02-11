from environments.task import Task
from utils.core_types import (
    TaskObject,
    Pose,
    Point3D,
    Rotation,
    Workspace,
    _from_pybullet_pose,
    _to_pybullet_pose,
)
from environments.environment import Environment
import pybullet as p

import pickle
import time
import random
import uuid

import utils.general_utils as utils

import numpy as np


class EnvironmentConfiguration:
    """stores a list of objects and their poses, s.t. we can reset to environment configurations
    also stores image, s.t. we can choose configs based on images
    """

    def __init__(self, objects_with_poses: list[TaskObject, Pose] = [], image=None):
        self.id = uuid.uuid4()
        self.objects_with_poses = objects_with_poses
        self.image = image

    @classmethod
    def from_path(cls, path) -> "EnvironmentConfiguration":
        with open(path, "rb") as file:
            loaded_config = pickle.load(file)
        return loaded_config

    def dump(self, path):
        with open(path, "wb") as file:
            pickle.dump(self, file)

    def __str__(self):
        ret = ""
        for obj, pose in self.config:
            ret += f"{obj.description}: {pose.position} {pose.rotation} \n"
        return ret


class Task(Task):
    """
    Provides a simple API for setting up the environment in a chat-based manner
    For example, adding different objects in different places
    This is more for myself... I could write each environment setup myself, but I think this would lead to more variety
    each environment setup is given as a function which returns a Task
    """

    def __init__(self, config_path=None):
        super().__init__()
        self.taskObjects: list[TaskObject] = []
        self.lang_goal = None
        self.config = (
            EnvironmentConfiguration.from_path(config_path)
            if config_path is not None
            else None
        )

    def reset(self, env):
        super().reset(env)

        if self.config is not None:
            self.restore_from_config(env, self.config)
            # wait for blocks to settle...
            for _ in range(500):
                p.stepSimulation()
                time.sleep(1 / 400)
        else:
            self.taskObjects = []

    def add_blocks(
        self,
        env: Environment,
        num_blocks: int = 20,
        color=None,
        size: tuple[float, float, float] = (0.04, 0.04, 0.04),
        collision_free: bool = True,
    ):
        for _ in range(num_blocks):
            self.add_block(
                env,
                color=color or random.choice(list(utils.COLORS.keys())),
                size=size,
                collision_free=collision_free,
            )

        # might cause some issues with blocks flying everywhere...
        if not collision_free:
            for _ in range(500):
                p.stepSimulation()
                time.sleep(1 / 400)

    def add_block(
        self,
        env: Environment,
        color: str,
        size: tuple[float, float, float] = (0.04, 0.04, 0.04),
        pose: Pose = None,
        collision_free: bool = True,
    ):
        block_urdf = "box/box-template.urdf"

        if collision_free:
            block_pose = (
                self.get_random_pose(env, size)
                if pose is None
                else _to_pybullet_pose(pose)
            )
        else:
            block_pose = _to_pybullet_pose(self.get_random_pose_not_collision_free())

        sized_block_urdf = self.fill_template(block_urdf, {"DIM": size})
        block_id = env.add_object(sized_block_urdf, block_pose, color=color)
        # p.changeVisualShape(block_id, -1, rgbaColor=utils.COLORS[color] + [1])

        task_obj = TaskObject(
            objectType="block", color=color, id=block_id, category="rigid", size=size
        )

        self.taskObjects.append(task_obj)

    def add_zone(
        self,
        env: Environment,
        color: str,
        size: tuple[float, float, float] = (0.1, 0.1, 0.01),
    ):
        zone_pose = self.get_random_pose(env, size)
        zone_id = env.add_object(
            "zone/zone.urdf", zone_pose, "fixed", scale=1, color=color
        )

        task_obj = TaskObject(
            objectType="zone", color=color, id=zone_id, category="fixed", size=size
        )
        self.taskObjects.append(task_obj)

    def add_pallet(self, env: Environment):
        pallet_size = (0.2, 0.2, 0.02)
        pallet_pose = self.get_random_pose(env, pallet_size)
        pallet_urdf = "pallet/pallet.urdf"
        pallet_id = env.add_object(pallet_urdf, pallet_pose, category="fixed")

        task_obj = TaskObject(
            objectType="pallet",
            color="brown",
            id=pallet_id,
            category="fixed",
            size=pallet_size,
        )
        self.taskObjects.append(task_obj)

    def get_random_pose_not_collision_free(self) -> Pose:
        def random_in_range(low, high):
            return np.random.uniform(low, high)

        pos = [
            random_in_range(Workspace.bounds[0][0], Workspace.bounds[0][1]),
            random_in_range(Workspace.bounds[1][0], Workspace.bounds[1][1]),
            random_in_range(Workspace.bounds[2][0], Workspace.bounds[2][1]),
        ]
        theta = np.random.rand() * 2 * np.pi
        rot = utils.eulerXYZ_to_quatXYZW((0, 0, theta))

        return Pose(Point3D.from_xyz(pos), Rotation.from_quat(rot))

    def get_current_configuration(self, env: Environment) -> EnvironmentConfiguration:
        """gets all the objects and their properties, so we can reinitialise the scene..."""
        config = []
        for obj in self.taskObjects:
            pose = _from_pybullet_pose(env.get_object_pose(obj.id))
            config.append((obj, pose))

        img = env.render()

        storable = EnvironmentConfiguration(config, img)
        return storable

    def restore_from_config(self, env: Environment, config: EnvironmentConfiguration):
        for obj, pose in config.config:
            if obj.objectType == "block":
                self.add_block(env, obj.color, obj.size, pose)
