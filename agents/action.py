from utils.llm_utils import query_llm, parse_code_response
from utils.cap_utils import code_exec_with_bug_fix
from prompts.actor import actor_system_prompt, actor_prompt, actor_iteration_prompt

from agents.skill import Skill, SkillManager

import tiktoken


class Actor:
    """
    responsible for handling the main action loop
    i.e. integrating and potentially keeping track of new environment information
    actually not completely sure what this class should contain right now...
    """

    def __init__(self, skill_manager: SkillManager = None):
        self.skill_manager = skill_manager

    def set_env_and_task(self, env, task):
        self.task = task
        self.env = env
        self.messages = [{"role": "system", "content": actor_system_prompt}]
        skills = self.retrieve_skill_string(self.task)
        print(skills)
        encoding = tiktoken.get_encoding("o200k_base")
        num_tokensa = len(encoding.encode(actor_system_prompt))
        ap = actor_prompt(task, skills)
        num_tokensb = len(encoding.encode(ap))
        print(num_tokensa + num_tokensb)
        self.messages.append({"role": "user", "content": actor_prompt(task, skills)})

    def attempt_task(self, feedback=None):
        """where all the actual interaction logic should go...
        Possible augmentations: chain-of-thought prompting, structured outputs, generalise to learn skills...
        feedback: str
            if task was previously attempted (unsuccessfully), add feedback from last round
        """

        # TODO: update prompt to use chain of thought... i.e. use more output tokens for same task

        # if try again, just run the last piece of code again...
        if feedback != "try-again":
            if feedback:
                self.messages.append(
                    {"role": "user", "content": actor_iteration_prompt(feedback)}
                )
            response = query_llm(self.messages)
            self.last_code_str = parse_code_response(response)
            self.messages.append({"role": "assistant", "content": response})

        code_exec_with_bug_fix(self.last_code_str, self.env)

        return self.last_code_str

    def retrieve_skill_string(self, task) -> str:
        """format query for retrieval from vector database
        simplest approach is to use the task as a query and retrieve codes similar
        """

        if self.skill_manager is None:
            return ""

        skills = self.skill_manager.retrieve_skills(task)
        skill_string = ("\n\n").join([str(skill) for skill in skills])
        return skill_string
