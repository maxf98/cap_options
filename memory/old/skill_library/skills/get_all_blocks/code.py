def get_all_blocks():
    """Retrieve all block objects in the workspace."""
    return [obj for obj in get_objects() if is_block(obj)]