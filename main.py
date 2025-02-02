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
from agents.experience import AttemptTrace, InteractionTrace

from utils.task_primitives import LoadedTask


class CapOptioner:
    def __init__(self):
        self.max_num_task_attempts = 10  # not used for now... can use this when automating

        self.skill_manager = SkillManager()
        self.actor = Actor()
        self.critic = Critic()

    def run(self):
        env = self.setup_environment()

        while True:
            task_string = input(
                "\n\n\n"
                + "I'm ready to take instructions."
                + "\n"
                + "Input your instruction:"
            )

            self.attempt_task(env, task_string)

    def attempt_task(self, env: Environment, task_string: str):
        self.actor.set_env_and_task(env, task_string)

        trace = InteractionTrace(task_string)
        feedback = None
        while True:
            initial_config = env.task.get_current_configuration(env)
            print(initial_config)
            code_plan = self.actor.attempt_task(feedback)
            final_config = env.task.get_current_configuration(env)

            feedback = input(
                "How did I do? ('success', 'give-up', 'try-again', or give feedback)"
            )
            attempt_trace = AttemptTrace(initial_config, code_plan, final_config, feedback)

            trace.add_attempt(attempt_trace)

            # reset the environment to the exact same state
            env.set_task(LoadedTask(initial_config))
            env.reset()

            if feedback == "success" or feedback == "give-up":
                break

        env.set_task(ManyBlocksTask())
        env.reset()
        trace.dump()

            

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
