from tasks.task import Task


class PlaceBlocks(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "place one blue block on each side of the red block, so that the edges align perfectly"

    def reset(self, env):
        super().reset(env)
        self.add_block(env, "red")
        self.add_blocks(env, 4, "blue")
