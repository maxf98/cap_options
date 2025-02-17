def find_blocks() -> list[TaskObject]:
    """
    Identify and return the two blocks in the environment.
    Assumes that the blocks are the only objects of a certain type or color.
    """
    objects = get_objects()
    blocks = [obj for obj in objects if obj.objectType == 'block']
    if len(blocks) != 2:
        raise ValueError("Expected exactly two blocks in the environment.")
    return blocks