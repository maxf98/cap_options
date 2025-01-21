from environments.environment import Environment
from tasks.many_blocks import ManyBlocksTask
from tasks.precision_cylinder_tower import PrecisionCylinderTower
from tasks.assembling_kits import AssemblingKits

from utils.core_primitives import EnvWrapper
from utils import core_types
import numpy as np
import itertools

from agents.skill import SkillManager
from agents.action import Actor
from agents.critic import Critic


class CapOptioner:
    def __init__(self):
        self.max_num_task_attempts = 10

        self.skill_manager = SkillManager()
        self.actor = Actor()
        self.critic = Critic()

    def run(self):
        code_env = self.setup_code_environment()

        while True:
            task = input(
                "\n\n\n"
                + "I'm ready to take instructions."
                + "\n"
                + "Input your instruction:"
            )

            self.attempt_task(code_env, task)

    def attempt_task(self, code_env, task):
        self.actor.set_env_and_task(code_env, task)
        self.critic.set_env_and_task(code_env, task)

        feedback = None

        for attempt_round in range(self.max_num_task_attempts):
            code_plan = self.actor.attempt_task(feedback)

            # completion_image = self.wrapped_env.env.render()
            # # evaluate whether plan was successful
            # task_success, feedback, eval_code = self.critic.ai_check_task_success(
            #     code_plan, completion_image
            # )

            feedback = input("How did I do?")

            # this can only happen if it was actually successful at generating a skill... how can we guarantee this?
            # if task_success:
            #     self.skill_manager.add_skill_to_library(
            #         task, code_plan, eval_code, completion_image
            #     )
            #     return True

        return False

    def setup_code_environment(self) -> Environment:
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

        self.wrapped_env = EnvWrapper(env)

        code_env = {"bot": self.wrapped_env}
        code_env.update(
            {name: getattr(core_types, name) for name in core_types.__all__}
        )
        code_env.update({"np": np, "itertools": itertools})

        return code_env


if __name__ == "__main__":
    agent = CapOptioner()

    agent.run()
    # code_env = agent.setup_code_environment()

    # obj, objj = agent.wrapped_env.get_objects()[1], agent.wrapped_env.get_objects()[2]
    # agent.wrapped_env.put_first_on_second(
    #     agent.wrapped_env.get_object_pose(obj), agent.wrapped_env.get_object_pose(objj)
    # )
