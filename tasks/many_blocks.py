# basic environment with lots of different objects...

import numpy as np
import time

from environments import primitives
from environments.grippers import Spatula
from environments.task import Task

from utils.core_types import TaskObject
from utils import general_utils

import pybullet as p


class ManyBlocksTask(Task):
    """Push piles of small objects into a target goal zone marked on the tabletop."""

    def __init__(self):
        super().__init__()
        self.max_steps = 20
        self.lang_template = "push the pile of blocks into the green square"
        self.task_completed_desc = "done sweeping."
        # self.primitive = primitives.push
        # self.ee = Spatula
        self.objs = []
        self.additional_reset()

    def reset(self, env):
        super().reset(env)

        # Add goal zone.
        zone_size = (0.12, 0.12, 0)
        zone_pose = self.get_random_pose(env, zone_size)
        env.add_object('zone/zone.urdf', zone_pose, 'fixed')

        # Add pile of small blocks with `make_piles` function
        self.objs = self.add_blocks(env)
        for _ in range(500):
            p.stepSimulation()
            time.sleep(1/400)

        # Add goal
        self.add_goal(objs=self.objs, matches=np.ones((50, 1)), targ_poses=[zone_pose], replace=True,
                      rotations=False, metric='zone', params=[(zone_pose, zone_size)],
                      step_max_reward=1, language_goal=self.lang_template)

    def make_pile(self, env, block_color="red", num_blocks=50, *args, **kwargs):
        """
        add the piles objects for tasks involving piles
        """

        objs = []

        for _ in range(num_blocks):
            rx = self.bounds[0, 0] + 0.3 + np.random.rand() * 0.15
            ry = self.bounds[1, 0] + 0.3 + np.random.rand() * 0.15
            xyz = (rx, ry, 0.01)
            theta = np.random.rand() * 2 * np.pi
            xyzw = general_utils.eulerXYZ_to_quatXYZW((0, 0, theta))
            obj_id = env.add_object('block/small.urdf', (xyz, xyzw))
            color = general_utils.COLORS[block_color]
            p.changeVisualShape(obj_id, -1, rgbaColor=color + [1])
            objs.append(TaskObject(objectType="block", color=block_color, id=obj_id))

        return objs
    
    def add_blocks(self, env):
        objs = []

        for _ in range(20):
            rx = (self.bounds[0,0] + self.bounds[0,1])  / 2 + (np.random.rand() * 0.5 - 0.25)
            ry = (self.bounds[1,0] + self.bounds[1,1])  / 2 + (np.random.rand() * 0.5 - 0.25)
            xyz = (rx, ry, self.bounds[2, 1])
            theta = np.random.rand() * 2 * np.pi
            xyzw = general_utils.eulerXYZ_to_quatXYZW((0, 0, theta))
            obj_id = env.add_object('block/block.urdf', (xyz, xyzw))
            color = np.random.choice(list(general_utils.COLORS.keys()))
            p.changeVisualShape(obj_id, -1, rgbaColor=general_utils.COLORS[color] + [1])
            objs.append(TaskObject(objectType="block", color=color, id=obj_id))

        return objs