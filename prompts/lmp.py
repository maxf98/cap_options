from prompts.prompt_utils import get_core_types_text

insights = [
    "you can't create objects in the environment, you can only query them.",
    "leave a small gap (~0.008) between blocks placed right next to each other, otherwise they might hit each other when you put them down",
    "you can't pick block from bottom of a stack without breaking the stack",
    "when you place a block, always make sure to consider its rotation as well - we care about the Pose, not just the position",
    "don't assume the existence of objects, query them!",
    "avoid writing 'main' functions, choose semantically meaningful function names",
]


lmp_system_prompt = f"""
You write python code to control a robotic arm in a simulated environment. 
The user gives you natural language tasks, and you must solve them.

These are the main types you should work with:
{get_core_types_text()}

You aim to write modular and reusable code, so try to break your solutions down into small functions, which might be useful for other downstream tasks.
Give each function a clear and descriptive name, as well as a docstring that clearly and specifically explains the task that the function solves.

Make sure to actually execute your plan by calling the function you wrote.

DO NOT make any additional imports! 
"""


def lmp_prompt(task, inputs, outputs, examples):
    return f"""
    The following pieces of code may be useful in writing your solution.
    {examples}
    ---------------------------------------------------
    You may also introduce subtasks via the function: 
    lmp(task, inputs, outputs)
    Use this function if it is not clear how to solve a subtask from the examples.
    ---------------------------------------------------
    The task is {task}.
    Write a function to solve the task that accepts {inputs} as inputs, and returns {outputs}.
    """
