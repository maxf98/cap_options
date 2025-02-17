from tasks.task import Task


class Place5Blocks(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "place one blue block on each side of the red block, so that the edges align perfectly"

    def reset(self, env):
        super().reset(env)
        self.add_block(env, "red")
        self.add_blocks(env, 4, "blue")


class Place2Blocks(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "place one block right next to the other, such that the edges align and the corners touch"

    def reset(self, env):
        super().reset(env)
        self.add_block(env, "green")
        self.add_block(env, "yellow")


class Place4BlocksInLine(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = (
            "place the blocks in a line along the left side of the workspace"
        )

    def reset(self, env):
        super().reset(env)
        self.add_blocks(env, 4, "blue")


class PlaceBlockInZone(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "put the block in the zone"

    def reset(self, env):
        super().reset(env)
        self.add_zone(env, "green")
        self.add_blocks(env, 4, "blue")


class PlaceBlockMiddleLeft(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "put the block in the middle of the left side of the workspace"

    def reset(self, env):
        super().reset(env)
        self.add_block(env, "green")


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
