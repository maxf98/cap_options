from tasks.task_primitives import Task


class TaskAgent:
    """
    responsible for aiding in environment setup
    like the actor, should get better and better at setting the environment to a specific configuration
    tailored to the creator - it learns a specific language, i.e. a mapping from NL to env-config
    (through API + retrieval - including past configs)

    for now just a two-pass attempt
    first: retrieve previous configs
    if none chosen, generate new from string
    """

    def __init__(self):
        self.task = Task()

    def generate_task(self, task_prompt: str):
        pass
