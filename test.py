from environments.environment import Environment
from tasks.task import EnvironmentConfiguration
import time
import pybullet as p

from utils.core_types import *


code = """
def main():
    print("hello")
"""
if __name__ == "__main__":
    new_code = code.replace("main", "hello")
    print(new_code)
    