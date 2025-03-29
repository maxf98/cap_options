from environments.environment import Environment
from tasks.task import EnvironmentConfiguration
import time
import pybullet as p

import numpy as np

from utils.core_types import *


code = """
def main():
    print("hello")
"""
if __name__ == "__main__":
    a = (0, 1, 0)
    b = (0.2, 0.03, 0.2)
    print(np.multiply(a, b))

import get_object_color, get_object_size, get_object_pose, put_first_on_second, say


def is_big_red_block(block: TaskObject) -> bool:
    """Function to verify whether a block is 'big red block'.
    A big red block has side lengths longer than 5cm"""
    return get_object_color(block) == "red" and min(get_object_size(block)) >= 0.05


def pick_and_place_big_red_block(block: TaskObject, place_pose: Pose):
    """..."""

    if not is_big_red_block(block):
        raise Exception("The block isn't a big red block.")

    place_pose


def build_structure_from_blocks(
    blocks: list[TaskObject],
    dimensions: tuple[int, int, int],
    pose: Pose,
):
    """..."""

    if len(blocks) < dimensions[0] * dimensions[1] * dimensions[2]:
        say("There's not enough blocks!")
        return

    pose


def stack_blocks(blocks, pose):
    """Stacks the blocks at the given pose, ensuring all blocks are rotated the same way.
    Blocks are placed in the order in which they are given, from first to last."""
    for block in blocks:
        cur_block_pose = get_object_pose(block)
        put_first_on_second(cur_block_pose, pose)


from utils.core_primitives import *

# Task: stack the blocks in the middle of the workspace
blocks = get_objects()
middle_of_workspace = Workspace.middle
stack_blocks(blocks, middle_of_workspace)
