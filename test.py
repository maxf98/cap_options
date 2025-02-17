from environments.environment import Environment
from tasks.task import EnvironmentConfiguration
import time
import pybullet as p

from utils.core_types import *


if __name__ == "__main__":
    poseA = Pose(Point3D.from_xyz([1, 2, 3]), Rotation.from_quat([0, 0, 0, 1]))
    poseB = Pose(Point3D.from_xyz([1, 2, 3]), Rotation.from_quat([0, 0, 2, 1]))
    poseC = Pose(Point3D.from_xyz([1, 2, 3]), Rotation.from_quat([0, 0, 0, 1]))

    print(poseA == poseB)
    print(poseA == poseC)
