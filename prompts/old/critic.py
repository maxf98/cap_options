# critic_system_prompt = f"""
# You write python code to evaluate whether an agent successfully achieved a task. The agent controls a robotic arm in a simulated environment.
# {api_prompt}
# """


# def parse_completion_prompt(task, task_attempt):
#     return f"""
#     The task was: {task}.
#     The agent attempted to solve it using the following code: {task_attempt}.
#     I have attached an image of the workspace, you may use this to guide the generation of code.
#     For example, if you can see in the image that the task was not solved, identify the reason, and test for this in your code.
#     Write a function that returns the boolean completion truth value, and give the function an appropriate name.
#     Keep in mind: {code_style_prompt}

#     Return the boolean completion in the variable "task_success", as task_success = True | False
#     """


# explain_failure_prompt = f"""
#     According to your code, the task was not solved successfully. Explain why this might be the case. Use the image in the previous message to guide your response.
#     Answer concisely, give only your best theory as to why the solution was unsuccessful.
#     """


# def bug_fix_prompt(code_str, error_traceback):
#     return f"tried running the following code \n {code_str} and got the following error traceback \n {error_traceback}. Fix the error and return only the update code."
