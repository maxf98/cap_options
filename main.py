from environments.environment import Environment
from tasks.many_blocks import ManyBlocksTask
from tasks.precision_cylinder_tower import PrecisionCylinderTower
from tasks.assembling_kits import AssemblingKits

from utils import core_types
import numpy as np
import itertools

from agents.skill import SkillManager
from agents.action import Actor
from agents.critic import Critic
from agents.experience import ExperienceTrace


class CapOptioner:
    def __init__(self):
        self.max_num_task_attempts = 10

        self.skill_manager = SkillManager()
        self.actor = Actor()
        self.critic = Critic()

    def run(self):
        env = self.setup_environment()

        while True:
            task = input(
                "\n\n\n"
                + "I'm ready to take instructions."
                + "\n"
                + "Input your instruction:"
            )

            self.attempt_task(env, task)

    def attempt_task(self, env, task):
        self.actor.set_env_and_task(env, task)

        initial_config = env.task.getCurrentConfiguration()
        trace = ExperienceTrace(initial_config, task)

        feedback = None

        for attempt_round in range(self.max_num_task_attempts):
            code_plan = self.actor.attempt_task(feedback)

            feedback = input(
                "How did I do? (type success or give a reason for failure)"
            )

            trace.append(code_plan, feedback)
            if feedback == "success":
                trace.was_success(env.task.getCurrentConfiguration())
                break

        return False

    def setup_environment(self) -> Environment:
        """handles the basic environment setup, primarily adding objects to the scene"""
        env = Environment(
            "environments/assets",
            disp=True,
            shared_memory=False,
            hz=480,
            record_cfg={
                "save_video": False,
                "save_video_path": "${data_dir}/${task}-cap/videos/",
                "add_text": True,
                "add_task_text": True,
                "fps": 20,
                "video_height": 640,
                "video_width": 720,
            },
        )

        env.set_task(ManyBlocksTask())
        env.reset()

        return env


if __name__ == "__main__":
    agent = CapOptioner()

    agent.run()
    # code_env = agent.setup_code_environment()

    # obj, objj = agent.wrapped_env.get_objects()[1], agent.wrapped_env.get_objects()[2]
    # agent.wrapped_env.put_first_on_second(
    #     agent.wrapped_env.get_object_pose(obj), agent.wrapped_env.get_object_pose(objj)
    # )
