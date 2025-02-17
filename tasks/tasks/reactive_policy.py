from tasks.task import Task
import numpy as np
from utils.core_types import Pose, Point3D, Rotation, Workspace


class PlaceCubeInClutteredEnvironment(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "place the red cube in the middle of the workspace. after placing it, check if it worked, by checking if the pose is what you expected"

    def reset(self, env):
        super().reset(env)
        for _ in range(30):
            block_size = np.random.uniform(low=0.01, high=0.08)
            self.add_block(env, color="gray", size=(block_size, block_size, block_size))

        self.add_block(env, color="red", size=(0.08, 0.08, 0.08))


class PickBlockUnderOtherBlock(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = (
            "pick up the red block and put it in the center of the workspace"
        )

    def reset(self, env):
        super().reset(env)

        self.add_block(
            env,
            color="red",
            size=(0.08, 0.08, 0.08),
            pose=Pose(Point3D(0.5, 0.2, 0.04), Rotation.identity()),
        )
        self.add_block(
            env,
            color="blue",
            size=(0.08, 0.08, 0.08),
            pose=Pose(Point3D(0.5, 0.2, 0.12), Rotation.identity()),
        )


class NonPlanarBlock(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = (
            "pick up the red block and put it in the center of the workspace"
        )

    def reset(self, env):
        super().reset(env)

        self.add_block(
            env,
            color="blue",
            size=(0.08, 0.08, 0.08),
            pose=Pose(Point3D(0.5, 0.2, 0.04), Rotation.identity()),
        )
        self.add_block(
            env,
            color="blue",
            size=(0.06, 0.06, 0.06),
            pose=Pose(Point3D(0.5, 0.32, 0.025), Rotation.identity()),
        )
        self.add_block(
            env,
            color="red",
            size=(0.05, 0.05, 0.05),
            pose=Pose(Point3D(0.5, 0.25, 0.15), Rotation.identity()),
        )

        self.wait_for_objects_to_settle()
