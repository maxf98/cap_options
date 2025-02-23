def retrieve_blocks(color: str = None) -> list[TaskObject]:
    """ Retrieve all blocks in the environment, optionally filtering by a specified color. """
    all_objects = get_objects()
    blocks = [obj for obj in all_objects if obj.objectType == "block"]
    if color:
        blocks = [block for block in blocks if block.color == color]
    return blocks