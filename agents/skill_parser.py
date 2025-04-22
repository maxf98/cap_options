from agents.model import Skill, TaskExample
from agents.memory import MemoryManager

from utils.llm_utils import (
    query_llm,
    parse_code_response,
    format_code_to_print,
    query_llm_structured,
)
import textwrap


class SkillParser:
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
        self.messages = []

    def parse_skill(self) -> Skill:
        skill_prompt = input("what skill would you like to learn?")
        skill = self.check_for_existing_similar_skills(skill_prompt)
        if skill is None:
            skill = self.generate_skill(skill_prompt)

        skill = self.refine_skill(skill)
        return skill

    def apply_task_hint(self, hint) -> list[TaskExample]:
        # "this is similar to when..."
        # this represents skill **uses**

        # first split task hints within string, then perform retrieval for each
        from prompts.parse_skill import ParsedList, parse_hint_to_list_prompt

        messages = [{"role": "user", "content": parse_hint_to_list_prompt(hint)}]
        tasks = query_llm_structured(messages, ParsedList)
        task_descriptions = tasks.parsed_list

        retrieved_task_examples = []
        for task_desc in task_descriptions:
            ret_tasks = self.memory_manager.retrieve_examples(task_desc, num_results=5)
            retrieved_task_examples.extend(ret_tasks)
        return retrieved_task_examples

    def apply_skill_hint(self, hint) -> list[Skill]:
        # actually retrieves the skill objects, so that we can look inside for: this is "like" that
        # and so we can append them to the prompt, instead of appending all skills every time...

        # first split task hints within string, then perform retrieval for each
        from prompts.parse_skill import ParsedList, parse_hint_to_list_prompt

        messages = [{"role": "user", "content": parse_hint_to_list_prompt(hint)}]
        skills_object = query_llm_structured(messages, ParsedList)
        skill_descriptions = skills_object.parsed_list

        retrieved_skills = []
        for skill_desc in skill_descriptions:
            ret_skill = self.memory_manager.retrieve_skills(skill_desc, num_results=1)
            retrieved_skills.extend(ret_skill)

        return retrieved_skills

    def generate_skill(self, skill_prompt):
        from prompts.parse_skill import (
            generate_function_header_system_prompt,
            generate_skill_prompt,
        )

        similar_skills = self.memory_manager.retrieve_skills(
            skill_prompt, num_results=5
        )

        self.messages = [
            {"role": "system", "content": generate_function_header_system_prompt},
            {
                "role": "user",
                "content": generate_skill_prompt(skill_prompt, similar_skills),
            },
        ]

        response = query_llm(self.messages)
        code = parse_code_response(response)
        self.messages.append({"role": "assistant", "content": code})
        skill = Skill.parse_function_string(code)

        return skill

    def check_for_existing_similar_skills(self, skill_prompt) -> Skill | None:
        similar_skills = self.memory_manager.retrieve_skills(
            skill_prompt, num_results=5
        )
        summary_str = f"""
            Similar existing functions are:
            {"\n".join([format_code_to_print(skill.description) for skill in similar_skills])}
            """
        print(textwrap.dedent(summary_str))
        chosen_skill = input("choose a skill by typing its name, or none:\n")

        if chosen_skill != "none":
            return self.memory_manager.skill_manager.retrieve_skill_with_name(
                chosen_skill
            )

        return None

    def refine_skill(self, skill: Skill) -> Skill | None:
        from prompts.parse_skill import (
            refine_function_header_prompt,
            generate_function_header_system_prompt,
        )

        if len(self.messages) == 0:
            self.messages = [
                {"role": "system", "content": generate_function_header_system_prompt}
            ]

        function_code = skill.code

        while True:
            print(
                textwrap.dedent(
                    f"""
                The current function code is: 
                {format_code_to_print(function_code)}
                """
                )
            )

            refinement_input = input(
                "Accept the function? (abort, accept, or feedback and iterate)"
            )

            match refinement_input:
                case "abort":
                    self.messages = []
                    return None
                case "accept":
                    skill.code = function_code
                    self.messages = []
                    return skill
                case _:
                    self.messages.append(
                        {
                            "role": "user",
                            "content": refine_function_header_prompt(
                                function_code, refinement_input
                            ),
                        }
                    )
                    response = query_llm(self.messages)
                    function_code = parse_code_response(response)
                    self.messages.append(
                        {"role": "assistant", "content": function_code}
                    )


if __name__ == "__main__":
    skill_parser = SkillParser(MemoryManager())
    # skills = skill_parser.apply_skill_hint(
    #     "use the skills put_first_on_second and clear_blocks_from_area"
    # )
    # examples = skill_parser.apply_task_hint(
    #     "this is like when you had to build a block pyramid"
    # )
