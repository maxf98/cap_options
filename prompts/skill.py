skill_description_system_prompt = """
You will be given python code, and you are supposed to return a concise description of what this code accomplishes.
"""


def generate_skill_description_prompt(code, task):
    return f"""
            The code is {code}. It was written to solve the task {task}. 
            """
