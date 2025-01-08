from dataclasses import dataclass
import numpy as np
from scipy.spatial.transform import Rotation
from environments.environment import Environment


__all__ = ["Point3D", "Pose", "TaskObject", "Rotation", "Environment"]

@dataclass
class Point3D:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    x: float
    y: float
    z: float

    @classmethod
    def from_xyz(cls, xyz):
        return cls(xyz[0], xyz[1], xyz[2])

    @property
    def np_vec(self) -> np.array:
        return np.array([self.x, self.y, self.z])

@dataclass
class Pose:
    position: Point3D
    rotation: Rotation

@dataclass
class TaskObject:
    objectType: str
    color: str
    id: int

    @property
    def description(self):
        return f"{self.color} {self.objectType} with object_id {self.id}"