from prompts.prompt_utils import get_core_primitives_text, get_core_types_text

code_style_prompt = """
DO NOT make any imports! Use only the described modules, and assume they are already imported in your code environment.
"""

api_prompt = f"""
Make sure to conform to the following utility types:
{get_core_types_text()}
You may use the following API:
{get_core_primitives_text()}
"""

environment_description = """
The Environment may contain objects of many different kinds. 
"""

actor_system_prompt = f"""
You are an agent training a robotic arm to perform different skills in a simple pick-and-place environment.
You write python code to control the robotic arm, building on a simple API.
{api_prompt}
The user gives you natural language tasks, and you must solve them.
Write flat solution codes, i.e. avoid writing functions.

DO NOT make any imports! Use only the described modules, and assume they are already imported in your code environment.

Make sure to actually execute your plan.
"""


def generate_action_plan_prompt(task):
    return f"""
        The task is {task}. Write python code to solve it. 
        """


critic_system_prompt = f"""
You write python code to evaluate whether an agent successfully achieved a task. The agent controls a robotic arm in a simulated environment.
{api_prompt}
"""


def parse_completion_prompt(task, task_attempt):
    return f"""
    The task was: {task}.
    The agent attempted to solve it using the following code: {task_attempt}.
    I have attached an image of the workspace, you may use this to guide the generation of code. 
    For example, if you can see in the image that the task was not solved, identify the reason, and test for this in your code.
    Write a function that returns the boolean completion truth value, and give the function an appropriate name.
    Keep in mind: {code_style_prompt}

    Return the boolean completion in the variable "task_success", as task_success = True | False
    """


explain_failure_prompt = f"""
    According to your code, the task was not solved successfully. Explain why this might be the case. Use the image in the previous message to guide your response.
    Answer concisely, give only your best theory as to why the solution was unsuccessful.
    """


def bug_fix_prompt(code_str, error_traceback):
    return f"tried running the following code \n {code_str} and got the following error traceback \n {error_traceback}. Fix the error and return only the update code."


# --------------------------------------------------------------------------
skill_description_system_prompt = """
You will be given python code, and you are supposed to return:
1) an appropriate name
2) a concise description of what this code accomplishes.
"""


def generate_skill_description_prompt(code, task):
    return f"""
            The code is {code}. It was written to solve the task {task}. 
            """
