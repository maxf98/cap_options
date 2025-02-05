from tasks.task import Task


class JengaLayer(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "build a single layer of a jenga tower with 3 blocks"

    def reset(self, env):
        super().reset(env)

        self.add_blocks(env, 3, "brown", size=(0.09, 0.03, 0.02))


class Jenga(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "build a jenga tower with 3 layers of 3 blocks each"

    def reset(self, env):
        super().reset(env)

        self.add_blocks(env, 9, "brown", size=(0.09, 0.03, 0.02))
