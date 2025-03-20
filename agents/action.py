from utils.llm_utils import (
    query_llm,
    parse_code_response,
    query_llm_structured,
    print_code,
)
from utils.cap_utils import cap_code_exec

from agents.model.skill import Skill
from agents.model.example import TaskExample
from agents.memory import MemoryManager
from agents.skill_parser import SkillParser

from collections import Counter

# TODO: until larger amount of skills, non-naive retrieval strategies aren't necessary (and actually interfere)


class Actor:
    """
    responsible for handling the main action loop
    i.e. integrating and potentially keeping track of new environment information
    actually not completely sure what this class should contain right now...
    """

    def __init__(self, memory_manager: MemoryManager, skill_parser: SkillParser = None):
        self.memory_manager = memory_manager
        self.skill_parser = skill_parser
        self.reset()

    def reset(self):
        self.messages = []
        self.env = None
        self.task = None
        self.lvars = {}

    def learn_skill(self, env, task, skill: Skill):
        """when we are solving a task with a given skill, we are learning the skill
        means we are both writing the skill code and the actual task-specific code
        """

        from prompts.skill import (
            actor_skill_learning_system_prompt,
            skill_learning_prompt,
        )

        self.env = env
        self.task = task

        # need function for retrieving other potentially task-relevant skills
        hint = input("what prior knowledge can I use to solve this task?")
        if hint == "none":
            examples = self.memory_manager.retrieve_examples(task, num_results=5)
        else:
            examples = self.skill_parser.apply_task_hint(hint)

        for example in examples:
            print(example.task)
        # skills = self.memory_manager.skill_manager.retrieve_skills(
        #     "query", only_core_primitives=True, num_results=20
        # )
        skills = self.memory_manager.skill_manager.all_skills
        # skills = self.retrieve_task_related_skills(task_examples=few_shot_examples)
        # skills = self.retrieve_task_related_skills_naive(task, num_results=50)
        # skills = []
        # skills = self.actively_request_examples()

        prompt = skill_learning_prompt(
            task=task,
            few_shot_examples=examples,
            skill=skill,
            other_useful_skills=skills,
        )

        self.messages = [
            {"role": "system", "content": actor_skill_learning_system_prompt},
            {
                "role": "user",
                "content": prompt,
            },
        ]

        code = self.write_and_run_code(self.messages)

        return code

    def attempt_task(self, env, task):
        """solves a task without a skill to be learned"""
        from prompts.actor import (
            actor_system_prompt,
            actor_prompt,
        )

        self.env = env
        self.task = task

        # need function for retrieving other potentially task-relevant skills
        few_shot_examples = self.memory_manager.retrieve_examples(task, num_results=20)
        skills = self.retrieve_task_related_skills_naive(task, num_results=50)

        prompt = actor_prompt(
            task=task, few_shot_examples=few_shot_examples, api=skills
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

        from prompts.actor import actor_iteration_prompt

        examples = []
        if feedback.startswith("hints:"):
            hints = feedback.split(":")[1].split(",")
            examples = self.skill_parser.apply_task_hint(hints)
        # elif feedback.startswith("skill-hints:"):
        #     hints = feedback.split(":")[1].split(",")
        #     skills = self.skill_parser.apply_skill_hint(feedback)

        self.messages.append(
            {
                "role": "user",
                "content": actor_iteration_prompt(feedback, examples),
            }
        )

        code = self.write_and_run_code(self.messages)

        return code

    def write_and_run_code(self, messages):
        response = query_llm(messages)
        code = parse_code_response(response)
        self.last_code_str = code
        self.messages.append({"role": "assistant", "content": self.last_code_str})
        print_code(code)
        new_lvars = cap_code_exec(
            code,
            self.env,
            self.memory_manager.skill_manager.resolve_dependencies(self.last_code_str),
            self.lvars,
        )
        return code

    def run_last_code_str(self):
        """just run the last piece of code again"""
        cap_code_exec(
            self.last_code_str,
            self.env,
            self.memory_manager.skill_manager.resolve_dependencies(self.last_code_str),
            self.lvars,
        )
        return self.last_code_str

    def generated_subtask_based_retrieval(self, task) -> list[Skill]:
        # generate a plan by decomposing the task into subtasks, and then retrieving a skill for each subtask
        pass

    def retrieve_task_related_skills_naive(self, task, num_results=20) -> list[Skill]:
        # naive strategy: retrieve skills by
        return self.memory_manager.retrieve_skills(task, num_results=num_results)

    def retrieve_task_related_skills(
        self, task=None, task_examples: list[TaskExample] = None, num_results=10
    ) -> list[Skill]:
        """can specify either a task, or a list of task examples - if specifying a task, it retrieves similar tasks first"""
        similar_tasks = (
            self.memory_manager.retrieve_examples(task)
            if task_examples is None
            else task_examples
        )
        skills = self.extract_skill_calls_from_code_strings(
            [task.code for task in similar_tasks], num_results
        )

        return skills

    def retrieve_skill_related_skills(
        self, skill: Skill, num_results=10
    ) -> list[Skill]:
        similar_skills = self.memory_manager.retrieve_skills(skill.description)
        return self.extract_skill_calls_from_code_strings(
            [skill.code for skill in similar_skills], num_results
        )

    def extract_skill_calls_from_code_strings(
        self, codes: list[str], max_skills=10
    ) -> list[Skill]:
        """can be used either to extract from task code or from skill codes"""
        per_code_skill_calls = [
            self.memory_manager.skill_manager.get_skill_calls(code) for code in codes
        ]
        counter = Counter(
            skill_call.name
            for task_calls in per_code_skill_calls
            for skill_call in task_calls
        )
        sorted_skill_names = [skill for (skill, _) in counter.most_common(max_skills)]
        sorted_skills = [
            self.memory_manager.skill_manager.retrieve_skill_with_name(name)
            for name in sorted_skill_names
        ]
        return sorted_skills

    def retrieve_skill_related_skills_naive(self, skill: Skill):
        return self.memory_manager.retrieve_skills(skill.description)


if __name__ == "__main__":

    memory_manager = MemoryManager()
    actor = Actor(memory_manager)

    # skill = Skill.parse_function_string(code)

    # task_skills = actor.retrieve_task_related_skills("put one block next to the other")
    # skills = actor.retrieve_skill_related_skills(skill)
    # Skill.print_skills(task_skills)
    # Skill.print_skills(skills)

    # naive_task_skills = actor.retrieve_task_related_skills_naive(
    #     "put one block next to the other"
    # )
    # naive_skills = actor.retrieve_skill_related_skills_naive(skill)

    # Skill.print_skills(naive_task_skills)
    # Skill.print_skills(naive_skills)
