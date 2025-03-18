from utils.cap_utils import get_skill_calls
from agents.model import Skill, TaskExample
from agents.memory import SkillManager, ExamplesManager


def add_task_examples():
    example_manager = ExamplesManager()
    examples = example_manager.all_examples

    for example in examples:
        skill_calls = get_skill_calls(example.code)
        for skill in skill_calls:
            skill.add_task_example(example)
            print(f"adding {example.task} to {skill.name}")
            skill.dump()

    skill_manager = SkillManager()
    skills = skill_manager.all_skills

    for skill in skills:
        print(f"{skill.name}: {len(skill.task_examples)}")


def remove_all_task_examples():
    """for some reason they're not working right now - i'm not sure why, but gonna delete them and hope it's because of something I added..."""
    skill_manager = SkillManager()
    skills = skill_manager.all_skills

    for skill in skills:
        skill._task_examples = []
        skill.dump()

    for skill in skills:
        print(f"{skill.name}: {len(skill.task_examples)}")


# example_id = "3eeba5b5-c52c-4227-b3ed-abc8a91b3c82"
# skill_name = "build_structure_from_blocks"

# skill_manager = SkillManager()

# example = TaskExample.retrieve_task_with_id(example_id)
# skill = Skill.retrieve_skill_with_name(skill_name)

# skill.add_task_example(example)

# print(skill.task_examples)
# skill.dump()

# skill = Skill.retrieve_skill_with_name(skill_name)
# print(skill.task_examples)
