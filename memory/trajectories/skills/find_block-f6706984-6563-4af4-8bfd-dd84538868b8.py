def find_block(objects: list[TaskObject]) -> TaskObject:
    """
    Find the first block object in the list of objects.
    Parameters:
    - objects: List of TaskObject in the environment.
    Returns:
    - TaskObject: The first block object found.
    """
    for obj in objects:
        if obj.objectType == 'block':
            return obj
    raise ValueError("No block found in the objects list.")