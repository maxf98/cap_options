from dataclasses import dataclass
import numpy as np
from scipy.spatial.transform import Rotation
from environments.environment import Environment


__all__ = [
    "Point3D",
    "Pose",
    "AABBBoundingBox",
    "TaskObject",
    "Rotation",
    "Environment",
    "Workspace",
]


@dataclass
class Point3D:
    """
    Basic class for 3D points in cartesian space.
    """

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    x: float
    y: float
    z: float

    @classmethod
    def from_xyz(cls, xyz):
        """Create a Point3D object from a tuple of (x, y, z)"""
        return cls(xyz[0], xyz[1], xyz[2])

    @property
    def np_vec(self) -> np.array:
        """return the point as a numpy array"""
        return np.array([self.x, self.y, self.z])


@dataclass
class Pose:
    """Objects in 3D space have a position and a rotation, i.e. a Pose
    The position is given as the center of the object,
    Rotation type is taken from scipy.spatial.transform
    """

    position: Point3D
    rotation: Rotation


def _from_pybullet_pose(pose) -> Pose:
    return Pose(
        position=Point3D.from_xyz(pose[0]), rotation=Rotation.from_quat(pose[1])
    )


def _to_pybullet_pose(pose: Pose):
    xyz = (pose.position.x, pose.position.y, pose.position.z)
    return (xyz, pose.rotation.as_quat())


@dataclass
class AABBBoundingBox:
    """Axis-aligned bounding box, represented by two points
    If the contained object is rotated on the x-y plane, the bounding box is larger than the object
    Particularly, the corners of the bounding box do not correspond to the corners of the object...
    (could take this out to be fair...)
    """

    minPoint: Point3D
    maxPoint: Point3D

    @property
    def size(self) -> tuple[float, float, float]:
        """return size of bounding box as tuple of (width, depth, height)"""
        return (
            abs(self.minPoint.x - self.maxPoint.x),
            abs(self.minPoint.y - self.maxPoint.y),
            abs(self.minPoint.z - self.maxPoint.z),
        )


@dataclass
class TaskObject:
    """Any 'thing' in the workspace.
    E.g. blocks, ropes, zones, etc..."""

    objectType: str
    color: str
    id: int
    category: str = "rigid"
    size: tuple[float, float, float] = (0.04, 0.04, 0.04)

    @property
    def description(self):
        return f"{self.color} {self.objectType} with object_id {self.id}"


@dataclass
class Workspace:
    """Tasks are defined in a workspace, fully reachable by the robotic arm.
    The robotic arm is positioned at the origin (0,0)"""

    bounds = np.array([[0.25, 0.75], [-0.5, 0.5], [0, 0.3]])
