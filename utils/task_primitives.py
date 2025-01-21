from environments.task import Task
from utils.core_types import TaskObject, Pose
from environments.environment import Environment
from utils.core_primitives import _from_pybullet_pose, _to_pybullet_pose
import pybullet as p

import pickle
import time
import random

import utils.general_utils as utils


class EnvironmentConfiguration:
    def __init__(self, config: list[TaskObject, Pose] = []):
        self.config = config

    def dump(self, path):
        with open(path, "wb") as file:
            pickle.dump(self.config, file)

    @classmethod
    def from_path(cls, path) -> "EnvironmentConfiguration":
        with open(path, "rb") as file:
            loaded_config = pickle.load(file)
        return EnvironmentConfiguration(loaded_config)

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

    def __init__(self):
        super().__init__()
        self.taskObjects = list[TaskObject]()

    def reset(self, env):
        super().reset(env)

    def add_many_blocks(self, env: Environment, num_blocks: int = 20):
        for _ in range(num_blocks):
            self.add_block(env, color=random.choice(list(utils.COLORS.keys())))

        # wait for blocks to settle...
        for _ in range(500):
            p.stepSimulation()
            time.sleep(1 / 400)

    def add_block(
        self,
        env: Environment,
        color: str,
        size: tuple[float, float, float] = (0.04, 0.04, 0.04),
        pose: Pose = None,
    ):
        block_urdf = "box/box-template.urdf"

        block_pose = (
            self.get_random_pose(env, size) if pose is None else _to_pybullet_pose(pose)
        )

        sized_block_urdf = self.fill_template(block_urdf, {"DIM": size})
        block_id = env.add_object(sized_block_urdf, block_pose, color=color)
        # p.changeVisualShape(block_id, -1, rgbaColor=utils.COLORS[color] + [1])

        task_obj = TaskObject(
            objectType="block", color=color, id=block_id, category="rigid", size=size
        )

        self.taskObjects.append(task_obj)

    def getCurrentConfiguration(self, env: Environment) -> EnvironmentConfiguration:
        """gets all the objects and their properties, so we can reinitialise the scene..."""
        config = []
        for obj in self.taskObjects:
            pose = _from_pybullet_pose(env.get_object_pose(obj.id))
            config.append((obj, pose))

        storable = EnvironmentConfiguration(config)
        return storable

    def restoreFromConfig(self, env: Environment, config: EnvironmentConfiguration):
        for obj, pose in config.config:
            if obj.objectType == "block":
                self.add_block(env, obj.color, obj.size, pose)


class LoadedTask(Task):
    def __init__(self, config_path):
        super().__init__()
        self.config = EnvironmentConfiguration.from_path(config_path)

    def reset(self, env):
        super().reset(env)

        self.restoreFromConfig(env, self.config)
