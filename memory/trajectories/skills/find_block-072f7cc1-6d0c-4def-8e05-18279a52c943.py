def find_block() -> TaskObject:
    """
    Find the block object in the environment.
    Returns:
        TaskObject: The block object.
    """
    objects = get_objects()
    for obj in objects:
        if obj.objectType == 'block':
            return obj
    raise ValueError("No block found in the environment.")