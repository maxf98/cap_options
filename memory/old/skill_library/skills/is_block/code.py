def is_block(obj: TaskObject) -> bool:
    """
    Determine if a task object is a block.
    :param obj: A task object.
    :return: True if the object is a block, otherwise False.
    """
    return obj.objectType == "block"