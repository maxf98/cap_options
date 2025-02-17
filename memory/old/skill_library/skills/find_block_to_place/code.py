def find_block_to_place(objects: list[TaskObject]) -> TaskObject:
    """
    Select a block to place in the workspace.
    This function filters out non-block objects such as zones.
    :param objects: List of task objects in the environment.
    :return: The first available block to use for placement.
    """
    for obj in objects:
        if is_block(obj):
            return obj
    raise ValueError("No blocks available to place.")