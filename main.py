from environments.environment import Environment

from agents.memory import SkillManager, ExamplesManager
from agents.action import Actor
from agents.environment import EnvironmentAgent

from agents.model.interaction_trace import InteractionTrace
from agents.model.example import TaskExample
from agents.model.skill import Skill

from utils.llm_utils import (
    query_llm,
    query_llm_structured,
    parse_code_response,
    format_code_to_print,
    print_code,
)

from utils.cap_utils import cap_code_exec, get_non_function_code, get_defs

import textwrap
import pydantic
import re


class CapOptioner:
    states = ["parsing skill", "task setup", "attempting task", "testing skill"]

    def __init__(self, debugging=False):

        self.skill_manager = SkillManager()
        self.examples_manager = ExamplesManager()
        self.actor = Actor(skill_manager=self.skill_manager)
        self.env_agent = EnvironmentAgent()

        self.debugging = debugging

    def run(self):
        while True:
            # initial phase - determine skill to learn
            skill = self.parse_skill()
            
            self.learn_skill(skill)

    def learn_skill(self, skill: Skill):
        while True:
            task = input("provide a task that tests this skill: ")
            env_setup_prompt = input("how should the environment be setup?")

            self.env_agent.initialise_task(task, env_setup_prompt)

            self.attempt_task(skill)

            what_next = input("new-task or new-skill?")

            if what_next == "new-skill":
                return

    def attempt_task(self, skill=None):
        """
        if skill_header is given, we are trying to solve the task while also learning a specific skill
        otherwise we are just trying to solve the task - incorporate skill hints eventually
        the skill to be learned is a special skill which can be updated
        """
        inital_config = self.env_agent.reset()
        task = self.env_agent.current_task.lang_goal
        trace = InteractionTrace(task=task, initial_config=inital_config)
        code = self.actor.attempt_task(self.env_agent.env, task, skill)

        while True:
            feedback = input("how did I do? (success, give-up, try-again, or feedback)")

            match feedback:
                case "success":
                    example_code, skill_code = self.extract_task_and_skill_code(code)

                    final_config = self.env_agent.get_current_config()

                    task_example = TaskExample(
                        task=task,
                        code=example_code,
                        initial_config=inital_config,
                        final_config=final_config,
                    )
                    self.examples_manager.add_example_to_library(task_example)

                    trace.success(task_example)
                    trace.dump()

                    skill = Skill.parse_function_string(skill_code)
                    self.skill_manager.add_skill_to_library(skill)

                    return
                case "give-up":
                    trace.dump()
                    return    
                case "try-again":
                    self.env_agent.reset()
                    self.actor.try_again()
                case _:
                    trace.add_feedback_round(feedback)
                    self.env_agent.reset()
                    self.actor.revise_code_with_feedback(feedback)

    def extract_task_and_skill_code(self, code) -> tuple[str, str]:
        """given a code string with a function and some flat code, separate the two, and return both"""
        task_code = get_non_function_code(code)
        defs = get_defs(code, full_function_codes=True)
        print(task_code)
        print(defs)
        if len(defs) != 1:
            print(defs)
            return
        skill_code = defs[0]


        return task_code, skill_code

    def parse_intention(self):
        """there are multiple interactions that the user can make at every turn, depending on where the interaction is currently at...
        should definitely map this out in a state machine..."""

    def parse_skill(self) -> Skill:
        skill_prompt = input("what skill would you like to learn?")

        function_header, messages = self.generate_function_header(skill_prompt)
        skill = self.refine_function_header(function_header, messages)
        return skill

    def refine_function_header(self, function_header, messages=[]) -> Skill | str | None:
        from prompts.parse_skill import (
            refine_function_header_prompt,
        )

        while True:
            similar_skills = self.skill_manager.retrieve_skills(
                function_header, num_results=3
            )
            summary_str = f"""
                The proposed function header is: 
                {format_code_to_print(function_header)}
                Similar existing functions are:
                {"\n".join([format_code_to_print(skill.description) for skill in similar_skills])}
                """

            print(textwrap.dedent(summary_str))

            refinement_input = input("Accept the function? (<feedback>, abort, accept, use<function_name>)")

            match refinement_input:
                case "abort":
                    return None
                case "accept":
                    return Skill.parse_function_string(function_header)
                case str() if (m := re.fullmatch(r"use<(.*)>", refinement_input)):
                    name = m.group(1)
                    return Skill.retrieve_skill_with_name(name)

            messages.append(
                {
                    "role": "user",
                    "content": refine_function_header_prompt(
                        function_header, refinement_input
                    ),
                }
            )
            response = query_llm(messages)
            function_header = parse_code_response(response)
            messages.append({"role": "assistant", "content": function_header})

    def generate_function_header(self, skill_prompt):
        from prompts.parse_skill import (
            generate_function_header_system_prompt,
        )

        messages = [
            {"role": "system", "content": generate_function_header_system_prompt},
            {
                "role": "user",
                "content": skill_prompt,
            },
        ]

        response = query_llm(messages)
        code = parse_code_response(response)
        messages.append({"role": "assistant", "content": code})

        return code, messages

    def parse_user_response(self, feedback):
        """determine what action the user would like to take next:
        - iterate on the current task (refine task code and/or skill)
        - successfully solved current task -> store code example and Task configs...
            - sufficiently satisfied that the skill is successful?
            - finish
        - (technically - define a new skill, refine skills, ...)
        """




def reset_skill_library():
    """for some reason we need to do this in the root file, otherwise something doesn't work with pickling"""
    SkillManager.delete_skill_library()
    skill_manager = SkillManager()
    skill_manager.add_core_primitives_to_library()


def refresh_core_primitives():
    """update core primitives after a change to the file - this will remove trace_ids, but we can retrieve them later..."""
    skill_manager = SkillManager()
    skill_manager.add_core_primitives_to_library()


if __name__ == "__main__":
    agent = CapOptioner(debugging=False)
    agent.run()
    # refresh_core_primitives()
    # reset_skill_library()
    # skill_manager = SkillManager()
    # skill_manager.delete_skill("remove_blocks_from_pallet_and_align_left")
