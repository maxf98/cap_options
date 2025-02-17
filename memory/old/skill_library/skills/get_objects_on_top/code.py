def get_objects_on_top(block: TaskObject, objects: list[TaskObject], gap: float = 0.008) -> list[TaskObject]:
    """
    Identifies and returns a list of blocks that are stacked directly on top of the specified block.
    :param block: The block you want to check for other blocks on top.
    :param objects: The list of all task objects in the environment.
    :param gap: The acceptable vertical gap to consider two blocks as stacked (default is 0.008).
    :return: A list of TaskObjects that are on top of the specified block.
    """
    block_pose = get_object_pose(block)
    block_top_z = block_pose.position.z + block.size[2] / 2
    blocks_on_top = []
    for obj in objects:
        if obj == block:
            continue
        obj_pose = get_object_pose(obj)
        # Check if the block is directly above within allowable gap
        if np.isclose(obj_pose.position.x, block_pose.position.x, atol=0.01) and \
           np.isclose(obj_pose.position.y, block_pose.position.y, atol=0.01) and \
           np.isclose(obj_pose.position.z, block_top_z, atol=block.size[2] + gap):
            blocks_on_top.append(obj)
    return blocks_on_top