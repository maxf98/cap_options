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
