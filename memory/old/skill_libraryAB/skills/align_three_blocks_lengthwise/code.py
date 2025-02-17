def align_three_blocks_lengthwise(gap: float = 0.008):
    """
    Align three blocks lengthwise in the environment.
    :param gap: The gap to leave between the blocks to avoid collision.
    """
    # Retrieve all objects in the environment
    objects = get_objects()
    # Filter out the blocks from the list of objects
    blocks = [obj for obj in objects if obj.objectType == 'block']
    # Ensure there are at least three blocks
    if len(blocks) < 3:
        raise ValueError("Not enough blocks in the environment to perform the task.")
    # Sort blocks by their id to ensure a consistent order
    blocks.sort(key=lambda block: block.id)
    # Align the blocks lengthwise
    for i in range(1, len(blocks)):
        base_block = blocks[i - 1]
        adjacent_block = blocks[i]
        # Calculate the new pose for the adjacent block
        new_pose = calculate_aligned_pose(base_block, adjacent_block, gap)
        # Move the adjacent block to the new pose
        current_pose_adjacent_block = get_object_pose(adjacent_block)
        put_first_on_second(current_pose_adjacent_block, new_pose)
    # Confirm the action
    say("Three blocks have been aligned lengthwise.")