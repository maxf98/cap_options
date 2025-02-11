def get_block_by_color(color: str, objects: list[TaskObject]) -> TaskObject:
    """
    Retrieve a block by its color from a list of TaskObjects.
    :param color: The color of the block to retrieve.
    :param objects: The list of TaskObjects in the environment.
    :return: The TaskObject representing the block with the specified color.
    """
    for obj in objects:
        if obj.color == color:
            return obj
    raise ValueError(f"No block with color {color} found.")