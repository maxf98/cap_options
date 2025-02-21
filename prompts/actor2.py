from prompts.prompt_utils import get_core_types_text
from agents.model.skill import Skill


actor_system_prompt = f"""
You write python code to control a robotic arm in a simulated environment, building on an existing API. 
We are trying to learn skills, and are using different tasks to test and effectively learn a specific skill. 

You will be given:
- a task for the robotic agent to solve
- the skill you are supposed to use to solve the task

You are supposed to complete the function, as well as flat, task-specific code, as follows:

def given_function(...) -> ...:
    \"\"\" ... \"\"\"
    <function code>

<task-specific code>

For example:
-------------------------------------------------
IN:
task: "put the red block on the green block"
skill:
def put_block_on_other_block(block: TaskObject, otherBlock: TaskObject):
    \"\"\" places the block on top of otherBlock \"\"\"
    pass

OUT:
def put_block_on_other_block(block: TaskObject, otherBlock: TaskObject):
    \"\"\" places the block on top of otherBlock \"\"\"
    put_first_on_second(get_object_pose(block), get_object_pose(otherBlock))

red_block = get_block(color="red")
green_block = get_block(color="green")
put_block_on_other_block(red_block, green_block)
-------------------------------------------------

DO NOT make any imports.
DO NOT write any functions other than the given one.

Adhere to the following basic types:
{get_core_types_text()}

"""


def actor_prompt(
    task, skill: Skill, few_shot_examples=[], other_useful_skills: list[Skill] = []
):
    return f"""
    The task is: {task}
    The function you are supposed to implement is: {str(skill)}.
    The following skills may be useful in your implementation:
    {"\n\n".join([skill.description for skill in other_useful_skills])}
    """
