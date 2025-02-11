from tasks.task import Task


class ClearAreaPallet(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "remove all blocks from the pallet"

    def reset(self, env):
        super().reset(env)
        self.add_pallet(env)
        self.add_blocks(env, 30, collision_free=False)


class ClearAreaZone(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "remove all blocks from the zone"

    def reset(self, env):
        super().reset(env)
        self.add_zone(env, "green")
        self.add_blocks(env, 30, collision_free=False)


class ClearAreaSemantic(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "clear an area of size (0.3, 0.3) in the middle of the workspace, i.e. remove all objects from it"

    def reset(self, env):
        super().reset(env)
        self.add_blocks(env, 30, collision_free=True)
