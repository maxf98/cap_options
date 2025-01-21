from environments.task import Task
from core_types import TaskObject
import pybullet as p

import general_utils as utils


class TaskBuilder(Task):
    """
    Provides a simple API for setting up the environment in a chat-based manner
    For example, adding different objects in different places
    This is more for myself... I could write each environment setup myself, but I think this would lead to more variety
    each environment setup is given as a function which returns a Task
    """

    def __init__(self):
        pass

    def addBlockAtRandomPosition(
        self, env, color, block_size=(0.04, 0.04, 0.04)
    ) -> TaskObject:
        block_urdf = "block/block.urdf"

        block_pose = self.get_random_pose(env, block_size)
        sized_block_urdf = self.fill_template(block_urdf, {"DIM": block_size})
        block_id = env.add_object(sized_block_urdf, block_pose)
        p.changeVisualShape(block_id, -1, rgbaColor=utils.COLORS["red"] + [1])

        task_obj = TaskObject(
            objectType="block",
            color=color,
            id=block_id,
            category="rigid",
            size=block_size,
        )

        return TaskObject
