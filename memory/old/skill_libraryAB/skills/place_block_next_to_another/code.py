def place_block_next_to_another(base_block: TaskObject, adjacent_block: TaskObject, gap: float = 0.005):
    """
    Place the adjacent block right next to the base block with a small gap, aligning their edges and considering rotation.
    :param base_block: The block next to which the adjacent block will be placed.
    :param adjacent_block: The block to be placed next to the base block.
    :param gap: The gap to leave between the blocks.
    """
    # Get the pose of the base block
    base_block_pose = get_object_pose(base_block)
    # Calculate the target position for the adjacent block
    target_position = calculate_adjacent_position_with_rotation(base_block, adjacent_block.size, gap)
    # Place the adjacent block at the calculated position
    place_block_with_rotation(adjacent_block, target_position, base_block_pose.rotation)