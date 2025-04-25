from agents.memory import MemoryManager
from agents.action import Actor
from agents.environment import EnvironmentAgent
from agents.revision import RevisionAgent
from agents.skill_parser import SkillParser

from agents.model import Skill, TaskExample, InteractionTrace

from utils.task_and_store import Task

from utils.cap_utils import (
    get_non_function_code,
    get_defs,
)


class CapOptioner:

    def __init__(self):
        MEMORY_DIR = "memory/memory"

        self.memory_manager = MemoryManager(MEMORY_DIR)
        self.env_agent = EnvironmentAgent(memory_manager=self.memory_manager)
        self.skill_parser = SkillParser(memory_manager=self.memory_manager)
        self.actor = Actor(
            memory_manager=self.memory_manager, skill_parser=self.skill_parser
        )
        self.revision_agent = RevisionAgent(
            memory_manager=self.memory_manager,
            env_agent=self.env_agent,
        )

    def run(self):
        while True:
            # initial phase - determine skill to learn
            learn_skill = input(
                "learn a new skill? (yes/no)  - no means just attempt task\n"
            )

            if learn_skill == "yes":
                skill = self.skill_parser.parse_skill()

                if skill is None:
                    continue

                while True:
                    # skill_tasks = self.memory_manager.skill_task_examples(skill)
                    # print(
                    #     f"tested tasks\n {'\n'.join([task.task for task in skill_tasks])}"
                    # )
                    self.env_agent.parse_task()

                    self.attempt_task(skill)

                    what_next = input("new-task or new-skill?")

                    if what_next == "new-skill":
                        break
            else:
                self.env_agent.parse_task()
                self.attempt_task()

    def attempt_task(self, skill: Skill = None):
        """
        if skill is given, we are trying to solve the task while also learning a specific skill
        otherwise we are just trying to solve the task - incorporate skill hints eventually
        the skill to be learned can be updated - all other skills can only be used
        """
        inital_config = self.env_agent.reset()
        task = self.env_agent.current_task.lang_goal
        trace = InteractionTrace(task=task, initial_config=inital_config)

        def get_initial_code():
            return (
                self.actor.learn_skill(self.env_agent.env, task, skill)
                if skill is not None
                else self.actor.attempt_task(self.env_agent.env, task)
            )

        # first attempt at solving the task prior to allowing user corrections
        code = get_initial_code()

        while True:
            # --------------------------------------------------------------------------------
            # use this when display set to false... supposed to be faster, but I'm not sure...
            # img = self.env_agent.env.render()
            # import matplotlib.pyplot as plt

            # plt.imshow(img)
            # plt.show()
            # --------------------------------------------------------------------------------

            feedback = input(
                "how did I do? (success, give-up, re-run, try-again, hints:..., or feedback & iterate)"
            )

            match feedback:
                case "success":
                    example_code, skill_code = self.extract_task_and_skill_code(code)

                    final_config = self.env_agent.get_current_config()

                    task_example = TaskExample(
                        task=task,
                        code=example_code,
                        initial_config=inital_config,
                        final_config=final_config,
                        skill_code=skill_code,
                    )

                    self.memory_manager.example_manager.add_example_to_library(
                        task_example
                    )

                    trace.success(task_example)
                    self.memory_manager.add_trace(trace)

                    if skill is not None:
                        # skip skill testing for now...
                        # failed_task = self.revision_agent.test_modified_skill_on_past_task_examples(
                        #     skill, skill_code
                        # )

                        # # only update the skill if the new skill is successful on all previous tasks
                        # if failed_task:
                        #     # TODO: handle this somehow...
                        #     print(
                        #         "failed to solve prior tasks - aborting commit! continue iterating!"
                        #     )
                        #     continue

                        skill.code = skill_code
                        skill.add_task_example(task_example)
                        self.memory_manager.skill_manager.add_skill_to_library(skill)

                    self.actor.reset()

                    return
                case "give-up":
                    self.actor.reset()
                    self.memory_manager.add_trace(trace)
                    return
                case "re-run":
                    self.env_agent.reset()
                    self.actor.run_last_code_str()
                case "try-again":
                    self.env_agent.reset()
                    code = get_initial_code()
                case _:
                    trace.add_feedback_round(feedback)
                    self.env_agent.reset()
                    code = self.actor.revise_code_with_feedback(feedback)

    def extract_task_and_skill_code(self, code) -> tuple[str, str]:
        """given a code string with a function and some flat code, separate the two, and return both"""
        task_code = get_non_function_code(code)
        defs = get_defs(code, full_function_codes=True)
        if len(defs) != 1:
            print(defs)
            return task_code, None
        skill_code = defs[0]

        return task_code, skill_code

    def run_past_example(self):
        example_string = input("give a task:")
        example = self.memory_manager.retrieve_examples(example_string, num_results=5)
        print(f"examples\n {'\n'.join([example.task for example in example])}")
        example_index = input("choose an example by typing its index")
        example = example[int(example_index)]
        self.env_agent.set_to_task_and_config(example.task, example.initial_config)
        self.actor.run_code_str(self.env_agent.env, example.code)


if __name__ == "__main__":
    agent = CapOptioner()
    agent.run()
    # agent.run_past_example()
