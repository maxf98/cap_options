from utils.llm_utils import (
    query_llm,
    parse_code_response,
    query_llm_structured,
    print_code,
)
from utils.cap_utils import cap_code_exec

from agents.model.skill import Skill
from agents.model.example import TaskExample
from agents.memory import SkillManager, ExamplesManager



class Actor:
    """
    responsible for handling the main action loop
    i.e. integrating and potentially keeping track of new environment information
    actually not completely sure what this class should contain right now...
    """

    def __init__(self, skill_manager: SkillManager = None, examples_manager: ExamplesManager = None):
        self.skill_manager = skill_manager
        self.examples_manager = examples_manager
        self.messages = []

    def learn_skill(self, env, task, skill: Skill):
        """when we are solving a task with a given skill, we are learning the skill
        means we are both writing the skill code and the actual task-specific code"""

        from prompts.actor2 import actor_system_prompt, skill_learning_prompt

        self.env = env
        self.task = task

        # need function for retrieving other potentially task-relevant skills
        skills = self.retrieve_task_related_skills(task)
        few_shot_examples = self.retrieve_task_few_shot_examples(task)

        prompt = skill_learning_prompt(
                    task=task, few_shot_examples=few_shot_examples, skill=skill, other_useful_skills=skills
                )
        
        print(prompt)

        self.messages = [
            {"role": "system", "content": actor_system_prompt},
            {
                "role": "user",
                "content": prompt,
            },
        ]

        code = self.write_and_run_code(self.messages)
        
        return code
    
    def revise_code_with_feedback(self, feedback):
        """code revision should be different from initial task plan - there should be a different retrieval strategy for this
        for example also finding past examples of how feedback was incorporated into a solution
        """

        from prompts.actor2 import actor_iteration_prompt

        if feedback == "try-again":
            return self.try_again()

        self.messages.append(
            {
                "role": "user",
                "content": actor_iteration_prompt(feedback),
            }
        )

        code = self.write_and_run_code(self.messages)

        return code
    
    def solve_task(self, env, task):
        """solves a task without a skill to be learned"""
        return
    
    def write_and_run_code(self, messages):
        response = query_llm(messages)
        code = parse_code_response(response)
        self.last_code_str = code
        self.messages.append({"role": "assistant", "content": self.last_code_str})
        print_code(code)
        cap_code_exec(code, self.env)
        return code


    def try_again(self):
        """just run the last piece of code again"""
        cap_code_exec(self.last_code_str, self.env)
        return self.last_code_str
    
    def retrieve_task_related_skills(self, task) -> list[Skill]:
        # naive strategy for now...
        return self.skill_manager.retrieve_skills(task, num_results=10)
        

    def retrieve_task_few_shot_examples(self, task) -> list[TaskExample]:
        return self.examples_manager.retrieve_similar_examples(task)


