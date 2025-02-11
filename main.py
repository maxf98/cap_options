from environments.environment import Environment

from utils import core_types
import numpy as np
import itertools

from agents.skill import SkillManager
from agents.action import Actor
from agents.critic import Critic
from agents.experience import AttemptTrace, InteractionTrace


from tasks.task import Task
from tasks.tasks.build_cube import (
    BuildBig3Cube,
    BuildBig4Cube,
    BuildCube,
    BuildCubeCluttered,
)
from tasks.tasks.place_blocks import Place2Blocks, Place4BlocksInLine, Place5Blocks
from tasks.tasks.checkerboard import BuildCheckerboard
from tasks.tasks.jenga import JengaLayer, PlaceTwoBlocksLengthwise
from tasks.tasks.gripper_placement import GripperPlacement, GripperCircle
from tasks.tasks.stack import Stack
from tasks.tasks.scene_understanding import UnderstandBasicCommands
from tasks.tasks.clear_area import ClearAreaPallet, ClearAreaZone, ClearAreaSemantic


class CapOptioner:
    def __init__(self, debugging=False):

        self.skill_manager = SkillManager()
        self.actor = Actor(skill_manager=self.skill_manager)

        self.debugging = debugging

    def run(self):
        env = self.setup_environment()

        task_string = env.task.lang_goal or input(
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
            try:
                code_plan = self.actor.attempt_task(feedback)
            except KeyboardInterrupt:
                print("interrupted")
            final_config = env.task.get_current_configuration(env)

            feedback = input(
                "How did I do? ('success', 'give-up', 'try-again', or give feedback)"
            )
            attempt_trace = AttemptTrace(
                initial_config, code_plan, final_config, feedback
            )

            trace.add_attempt(attempt_trace)

            match feedback:
                case "success":
                    if not self.debugging:
                        self.skill_manager.add_skills(attempt_trace)
                        trace.dump()
                    return True
                case "give-up":
                    if not self.debugging:
                        trace.dump()
                    return False

            env.reset()

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

        env.set_task(Place5Blocks())
        env.reset()

        return env


def reset_skill_library():
    """for some reason we need to do this in the root file, otherwise something doesn't work with pickling"""
    SkillManager.delete_skill_library()
    skill_manager = SkillManager()
    skill_manager.add_core_primitives_to_library()


if __name__ == "__main__":
    agent = CapOptioner(debugging=False)

    agent.run()

    # reset_skill_library()
