from tasks.task import Task


class BuildCheckerboard(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "build a 4*4 chessboard from the blocks"

    def reset(self, env):
        super().reset(env)
        self.add_blocks(env, 8, "white")
        self.add_blocks(env, 8, "black")
