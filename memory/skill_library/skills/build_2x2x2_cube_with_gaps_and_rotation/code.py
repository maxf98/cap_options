def build_2x2x2_cube_with_gaps_and_rotation(start_position: Point3D, block_size: tuple[float, float, float], gap: float, rotation: Rotation):
    """
    Build a 2x2x2 cube using 8 blocks with specified gaps between them and a consistent rotation.
    :param start_position: The starting position for the cube.
    :param block_size: The size of each block.
    :param gap: The gap to leave between blocks.
    :param rotation: The consistent rotation to apply to all blocks.
    """
    # Step 1: Calculate target positions for the blocks
    target_positions = calculate_target_positions_with_gaps(start_position, block_size, gap)
    # Step 2: Clear the target area
    blocks = get_objects()
    clear_target_area(target_positions, blocks)
    # Step 3: Pick and place each block with the specified rotation
    for i, target_position in enumerate(target_positions):
        block = blocks[i]  # Assuming we have at least 8 blocks available
        pick_pose = get_object_pose(block)
        place_pose = Pose(position=target_position, rotation=rotation)
        put_first_on_second(pick_pose, place_pose)
        say(f"Placed block {block.description} at position {target_position} with consistent rotation")