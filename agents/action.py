from utils.llm_utils import (
    query_llm,
    parse_code_response,
    query_llm_structured,
    print_code,
)
from utils.cap_utils import cap_code_exec
from prompts.actor import (
    actor_system_prompt,
    actor_prompt,
    actor_iteration_prompt,
    identify_problematic_code,
    IdentifyFunctionToEdit,
)

from agents.skill import Skill, SkillManager

import tiktoken

from pydantic import BaseModel


class CodeEdit(BaseModel):
    code: str
    reasoning: str


class Actor:
    """
    responsible for handling the main action loop
    i.e. integrating and potentially keeping track of new environment information
    actually not completely sure what this class should contain right now...
    """

    def __init__(self, skill_manager: SkillManager = None):
        self.skill_manager = skill_manager
        self.messages = []

    def attempt_task(self, env, task, function_header):
        """when we are solving a task with a given skill, we are learning the skill
        means we are both writing the skill code and the actual task-specific code"""

        from prompts.actor2 import actor_system_prompt, actor_prompt

        skills = self.skill_manager.retrieve_skills(task, num_results=10)

        messages = [
            {"role": "system", "content": actor_system_prompt},
            {
                "role": "user",
                "content": actor_prompt(
                    task=task, skill=function_header, other_useful_skills=skills
                ),
            },
        ]

        code = parse_code_response(query_llm(messages))

        print_code(code)

        cap_code_exec(code, env)

        return code

    # def attempt_task(self, env, task):
    #     """where all the actual interaction logic should go...
    #     Possible augmentations: chain-of-thought prompting, structured outputs, generalise to learn skills...
    #     feedback: str
    #         if task was previously attempted (unsuccessfully), add feedback from last round
    #     """

    #     self.task = task
    #     self.env = env
    #     self.messages.append({"role": "system", "content": actor_system_prompt})
    #     # skills = self.retrieve_skill_string(self.task)
    #     # print(skills)
    #     skills = ""

    #     self.messages.append({"role": "user", "content": actor_prompt(task, skills)})

    #     response = query_llm(self.messages)
    #     self.last_code_str = parse_code_response(response)
    #     self.messages.append({"role": "assistant", "content": self.last_code_str})

    #     cap_code_exec(self.last_code_str, self.env)

    #     return self.last_code_str

    def revise_code_with_feedback(self, feedback):
        """code revision should be different from initial task plan - there should be a different retrieval strategy for this
        for example also finding past examples of how feedback was incorporated into a solution
        """

        if feedback == "try-again":
            return self.try_again()

        # TODO: somehow handle intermediate step with handling feedback

        # query_messages = self.messages.copy()
        # query_messages.append({"role": "assistant", "content": self.last_code_str})
        # skills = self.retrieve_skill_string(feedback)
        skills = ""
        # print(skills)
        self.messages.append(
            {
                "role": "user",
                "content": actor_iteration_prompt(feedback, skills),
            }
        )

        response = query_llm(self.messages)
        self.last_code_str = parse_code_response(response)
        self.messages.append({"role": "assistant", "content": self.last_code_str})

        cap_code_exec(self.last_code_str, self.env)

        return self.last_code_str

    def identify_problematic_code(self, code, feedback) -> Skill:
        messages = [
            {"role": "user", "content": identify_problematic_code(code, feedback)}
        ]
        response = query_llm_structured(messages, IdentifyFunctionToEdit)
        print(response.skill, response.reasoning)
        skill = Skill.retrieve_skill_with_name(response.function_name)
        return skill

    def try_again(self):
        """just run the last piece of code again"""
        cap_code_exec(self.last_code_str, self.env)
        return self.last_code_str

    def make_api_call(task):
        """check the api for previously solved tasks similar to this one - using the docstring should be fine? a description seems better though..."""
        # get few-shot examples
        # for each skill that is used

    def retrieve_skill_string(self, task, only_core_primitives=False) -> str:
        """format query for retrieval from vector database
        simplest approach is to use the task as a query and retrieve codes similar
        """

        if self.skill_manager is None:
            return ""

        skills = self.skill_manager.retrieve_skills(
            task, only_core_primitives=only_core_primitives
        )
        skill_string = ("\n\n").join([str(skill) for skill in skills])
        return skill_string
