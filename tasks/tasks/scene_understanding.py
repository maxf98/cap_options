from tasks.task import Task
from utils.core_types import Pose, Point3D, Rotation


class UnderstandBasicCommands(Task):
    def __init__(self):
        super().__init__()

    def reset(self, env):
        super().reset(env)
        self.add_block(env, "red")
