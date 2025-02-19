from tasks.task import Task
from utils.core_types import Pose, Point3D, Rotation


class GripperPlacement(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "flip over the block by pushing against it with the end effector on the top of the left side"

    def reset(self, env):
        super().reset(env)

        self.add_block(
            env,
            size=(0.09, 0.09, 0.09),
            color="red",
            pose=Pose(Point3D(0.5, 0, 0.045), Rotation.identity()),
        )


class GripperCircle(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = (
            "rotate the gripper in a circle, while maintaining its position"
        )

    def reset(self, env):
        super().reset(env)
