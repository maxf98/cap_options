from utils.task_and_store import Task


# for manually loading tasks

class Place2Blocks(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "place the green block next to the yellow block"

    def reset(self, env):
        super().reset(env)
        self.add_block(env, "green")
        self.add_block(env, "yellow")