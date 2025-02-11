from tasks.task import Task


class BuildCube(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "build a 2*2*2 cube made of 8 blocks"

    def reset(self, env):
        super().reset(env)
        self.add_blocks(env, 8)


class BuildBig3Cube(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = (
            """build a 3*3*3 cube made of 27 blocks in the center of the workspace."""
        )
        # make sure the area where you build it is free of any blocks before you start. leave a small (0.005) gap between blocks placed next to each other.
        # make sure that you account for the rotation of the blocks.

    def reset(self, env):
        super().reset(env)
        self.add_blocks(env, 64)


class BuildBig4Cube(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = """build a 4*4*4 cube made of 64 blocks in the center of the workspace. 
        make sure the area where you build it is free of any blocks before you start. leave a small (0.005) gap between blocks placed next to each other. 
        make sure that you account for the rotation of the blocks."""

    def reset(self, env):
        super().reset(env)
        self.add_blocks(env, 64)


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
