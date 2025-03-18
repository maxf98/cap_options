def generate_config_description(task):
    return f"""
    An agent has successfully solved the task: {task}.
    Generate a minimal description of the state the environment finds itself in after the task has been solved.
    Do not add any unnecessary information, focus on extracting the important details from the task description.

    i.e. "assuming the task was solved successfully, the environment is in this state"

    For example, if the task was to 'build a jenga tower in the middle of the workspace', the description could be: 'jenga tower in the middle of the workspace'
    """
