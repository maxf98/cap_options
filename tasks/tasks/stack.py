from tasks.task import Task


class Stack(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "build a stack of 5 blocks"

    def reset(self, env):
        super().reset(env)
        self.add_blocks(env, 5)
