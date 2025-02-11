def place_blue_block_next_to_red_block(gap: float = 0.005):
    """
    Place the blue block right next to the red block with a small gap, aligning their edges and considering rotation.
    :param gap: The gap to leave between the blocks.
    """
    # Retrieve all objects in the environment
    objects = get_objects()
    # Get the red and blue blocks
    red_block = get_block_by_color("red", objects)
    blue_block = get_block_by_color("blue", objects)
    # Calculate the target position for the blue block
    target_position = calculate_adjacent_position_with_rotation(red_block, blue_block.size, gap)
    # Get the rotation of the red block
    red_block_rotation = get_object_pose(red_block).rotation
    # Place the blue block at the target position with the same rotation as the red block
    place_block_with_rotation(blue_block, target_position, red_block_rotation)