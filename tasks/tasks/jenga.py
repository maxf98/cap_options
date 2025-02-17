from tasks.task import Task


class PlaceTwoBlocksLengthwise(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "place one block next to the other, such that their longer sides are touching."

    def reset(self, env):
        super().reset(env)

        self.add_blocks(env, 2, "brown", size=(0.09, 0.03, 0.02))


class PlaceThreeBlocksLengthwise(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "align the three blocks lengthwise, i.e. place them next to each other such that the longer sides of the blocks are touching each other"

    def reset(self, env):
        super().reset(env)

        self.add_blocks(env, 3, "brown", size=(0.09, 0.03, 0.02))


class PlaceTwoBlocksShortwise(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "align the two blocks such that the shorter sides of the blocks are touching each other"

    def reset(self, env):
        super().reset(env)

        self.add_blocks(env, 2, "brown", size=(0.09, 0.03, 0.02))


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
