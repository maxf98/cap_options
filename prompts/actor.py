from prompts.prompt_utils import get_core_types_text

fgen_prompt = f"""
Write a single, concise function to solve the task, give it a meaningful name, and add a docstring describing what it does, as well as its parameters and returns.
This function should be usable for downstream tasks, so write it with reusability and modularity in mind.
Keep your functions very short (i.e. around 10 lines of code). 
To make this possible, you may call functions which may not exist, as long as you give them a semantically clear and meaningful name.
"""

function_description_prompt_v2 = f"""
You aim to write modular and reusable code, so try to break your solutions down into small functions, which might be useful for other downstream tasks.
Give all functions (including the main function that executes the plan) a meaningful name and specific name.
If you make any assumptions, these should be encoded as parameters of the main function.
However, if the function serves a general purpose, give it a general name, rather than focusing on the current problem-solving context.
Add a docstring describing each function, its parameters, and returns.
"""

actor_system_prompt = f"""
You are an agent training a robotic arm to perform different skills in a simple pick-and-place environment.
You write python code to control the robotic arm, building on an existing API.
The user gives you natural language tasks, and you must solve them.

{function_description_prompt_v2}

You will be provided with some existing API functions along with a given task.

These are the main types you should work with:
{get_core_types_text()}

Make sure to actually execute your plan by calling the function you wrote.
Encode any assumptions you make as function parameters, and set these appropriately when you call the function.

DO NOT make any additional imports! 
"""


def actor_prompt(task: str, skills: str):
    return f"""
    The task is {task}.
    The following pieces of code may be useful in writing your solution. Try to call them if possible, since these are already tested:
    {skills}
    From previous iterations, you have learned:
    {"\n".join(insights)}
    """


def actor_iteration_prompt(feedback: str):
    return f"""
    {feedback}
    Code generated in previous iterations is not available, but API functions are.
    """


insights = [
    "you can't create objects in the environment, you can only query them.",
    "leave a tiny gap between blocks placed right next to each other, otherwise they might hit each other when you put them down",
    "you can't pick block from bottom of a stack without breaking the stack",
    "when you place a block, always make sure to consider its rotation as well - we care about the Pose, not just the position",
    "bbox is only useful for collision detection, NOT for tasks that require precise placement",
]
