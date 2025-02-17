from prompts.prompt_utils import get_core_types_text
from pydantic import BaseModel

fgen_prompt = f"""
Write a single, concise function to solve the task, give it a meaningful name, and add a docstring describing what it does, as well as its parameters and returns.
This function should be usable for downstream tasks, so write it with reusability and modularity in mind.
Keep your functions very short (i.e. around 10 lines of code). 
To make this possible, you may call functions which may not exist, as long as you give them a semantically clear and meaningful name.
"""

function_description_prompt_v2 = f"""
You aim to write modular and reusable code, so try to break your solutions down into small functions, which might be useful for other downstream tasks.
If you make any assumptions, these should be encoded as parameters of the main function.
Add a clear and descriptive docstring describing each function, its parameters, and returns.
"""

insights = [
    "you can't create objects in the environment, you can only query them.",
    "leave a small gap (~0.008) between blocks placed right next to each other, otherwise they might hit each other when you put them down",
    "you can't pick block from bottom of a stack without breaking the stack",
    "when you place a block, always make sure to consider its rotation as well - we care about the Pose, not just the position",
    "don't assume the existence of objects, query them!",
    "avoid writing 'main' functions, choose semantically meaningful function names",
]


actor_system_prompt = f"""
You are an agent training a robotic arm to perform different skills in a simple pick-and-place environment.
You write python code to control the robotic arm, building on an existing API.
The user gives you natural language tasks, and you must solve them.
You will be provided with some existing API functions along with a given task.

These are the main types you should work with:
{get_core_types_text()}

You aim to write modular and reusable code, so try to break your solutions down into small functions, which might be useful for other downstream tasks.
Give each function a clear and descriptive name, as well as a docstring that clearly and specifically explains the task that the function solves.

Only write new functions if this is necessary. Otherwise just produce a flat solution code without defining any functions.

Make sure to actually execute your plan by calling the function you wrote.

DO NOT make any additional imports! 

From previous iterations, you have learned:
{"\n".join(insights)}
"""


def actor_prompt(task: str, skills: str):
    return f"""
    The following pieces of code may be useful in writing your solution. Try to call them if possible, since these are already tested:
    {skills}
    ---------------------------------------------------
    The task is {task}.
    """


def actor_iteration_prompt(feedback: str, skills: str):
    return f"""
    The feedback for the last iteration of code was:
    {feedback}
    Revise your code appropriately.
    The following skills may be useful in doing so:
    {skills}
    Make sure to actually execute your code!
    """


def bug_fix_prompt(code_str, error_traceback):
    return f"tried running the following code \n {code_str} and got the following error traceback \n {error_traceback}. Fix the error and return only the update code."


def identify_problematic_code(code, feedback):
    return f"""
    I am controlling a robotic arm in a simulated environment with python code. 
    Your role is to figure out which function needs to be edited in order to accommodate the user's feedback. 
    You will be given a list of functions, and you are only to return the name of the function to edit.
    The code is: 
    {code}
    The user's feedback was:
    {feedback}
    Which function needs to be edited?
    """


class IdentifyFunctionToEdit:
    function_name: str
    reasoning: str
