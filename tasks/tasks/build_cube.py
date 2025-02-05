from tasks.task import Task


class BuildCube(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "build a 2*2*2 cube made of 8 blocks"

    def reset(self, env):
        super().reset(env)
        self.add_blocks(env, 8)


class BuildCubeInZone(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "build a 2*2*2 cube made of 8 blocks"

    def reset(self, env):
        super().reset(env)
        self.add_blocks(env, 8)


class BuildCubeCluttered(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "build a 2*2*2 cube made of 8 blocks"

    def reset(self, env):
        super().reset(env)
        self.add_blocks(env, 30)
