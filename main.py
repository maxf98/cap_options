from environments.environment import Environment

from agents.skill import SkillManager, Skill
from agents.action import Actor
from agents.experience import AttemptTrace, InteractionTrace
from agents.environment import EnvironmentAgent

from utils.llm_utils import (
    query_llm,
    query_llm_structured,
    parse_code_response,
    format_code_to_print,
    print_code,
)

import textwrap
import pydantic


class CapOptioner:
    states = ["parsing skill", "task setup", "attempting task", "testing skill"]

    def __init__(self, debugging=False):

        self.skill_manager = SkillManager()
        self.actor = Actor(skill_manager=self.skill_manager)
        self.env_agent = EnvironmentAgent()

        self.debugging = debugging

    def run(self):
        while True:
            # initial phase - determine skill to learn
            skill_header = self.parse_skill()

            task = input("provide a task that tests this skill: ")
            env_setup_prompt = input("how should the environment be setup?")
            self.env_agent.initialise_task(task, env_setup_prompt)
            inital_config = self.env_agent.reset()
            self.actor.attempt_task(
                self.env_agent.env, self.env_agent.current_task.lang_goal, skill_header
            )
            final_config = self.env_agent.get_current_config()
            # feedback = input("how did I do?")
            # self.parse_user_response(feedback)

    def parse_intention(self):
        """there are multiple interactions that the user can make at every turn, depending on where the interaction is currently at...
        should definitely map this out in a state machine..."""

    def parse_skill(self) -> str:
        while True:
            skill_prompt = input("what skill would you like to learn?")
            function_header, messages = self.generate_function_header(skill_prompt)
            function_header = self.refine_function_header(function_header, messages)
            if function_header is not None:
                return function_header
            else:
                print("abandoning current generation")

    def refine_function_header(self, function_header, messages=[]) -> str | None:
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

            refinement_input = input("Accept the function? (<feedback>, abort, accept)")

            match refinement_input:
                case "abort":
                    return None
                case "accept":
                    return function_header

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

    #     task_string = env.task.lang_goal or input(
    #         "\n\n\n"
    #         + "I'm ready to take instructions."
    #         + "\n"
    #         + "Input your instruction:"
    #     )

    #     self.attempt_task(env, task_string)

    # def attempt_task(self, env: Environment, task_string: str):
    #     trace = InteractionTrace(task_string)
    #     feedback = None
    #     while True:
    #         initial_config = env.task.get_current_configuration(env)
    #         code_plan = (
    #             self.actor.attempt_task(task=task_string, env=env)
    #             if feedback is None
    #             else self.actor.revise_code_with_feedback(feedback)
    #         )
    #         final_config = env.task.get_current_configuration(env)

    #         feedback = input(
    #             "How did I do? ('success', 'give-up', 'try-again', 'abort', or give feedback)"
    #         )
    #         attempt_trace = AttemptTrace(
    #             initial_config, code_plan, final_config, feedback
    #         )

    #         trace.add_attempt(attempt_trace)

    #         match feedback:
    #             case "success":
    #                 if not self.debugging:
    #                     self.skill_manager.add_skills_from_trace(trace)
    #                     trace.dump()
    #                 return True
    #             case "give-up":
    #                 if not self.debugging:
    #                     trace.dump()
    #                 return False
    #             case "abort":
    #                 return False
    #             case _:
    #                 env.reset()


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
