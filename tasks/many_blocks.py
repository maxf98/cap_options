# basic environment with lots of different objects...

import numpy as np
import time

from environments import primitives
from environments.grippers import Grip

# from environments.task import Task
from utils.task_primitives import Task

from utils.core_types import TaskObject
from utils import general_utils

import pybullet as p


class ManyBlocksTask(Task):
    """Push piles of small objects into a target goal zone marked on the tabletop."""

    def __init__(self):
        super().__init__()
        # self.primitive = primitives.push
        # self.ee = Grip

    def reset(self, env):
        super().reset(env)

        # Add goal zone.
        # zone_size = (0.12, 0.12, 0)
        # zone_pose = self.get_random_pose(env, zone_size)
        # zone_id = env.add_object("pallet/pallet.urdf", zone_pose, "fixed")
        # self.objs.append(TaskObject(objectType="pallet", color="green", id=zone_id))

        # Add pile of small blocks with `make_piles` function
        self.add_many_blocks(env)
