def build_jenga_layer_with_90_degree_rotation_and_gap(start_position: Point3D, gap: float):
    """
    Build a single layer of a Jenga tower with 3 blocks, ensuring they are rotated by 90 degrees and have a specified gap.
    :param start_position: The starting position for the first block in the layer.
    :param gap: The gap to leave between blocks.
    """
    # Step 1: Get the blocks and their size
    blocks = get_objects()
    if len(blocks) < 3:
        raise ValueError("Not enough blocks available to build a Jenga layer.")
    block_size = blocks[0].size  # Assuming all blocks are of the same size
    # Determine the correct rotation to align the longest side along the x-axis and add 90 degrees
    longest_side_index = block_size.index(max(block_size))
    if longest_side_index == 0:
        rotation_angle = 90  # Rotate 90 degrees from the x-axis
    elif longest_side_index == 1:
        rotation_angle = 180  # Rotate 90 degrees from the y-axis
    else:
        rotation_angle = 180  # Rotate 90 degrees from the z-axis (assuming 2D rotation)
    # Step 2: Clear the target area
    target_positions = calculate_jenga_layer_positions(start_position, block_size, gap)
    clear_target_area(target_positions, blocks)
    # Step 3: Place the blocks with the specified rotation
    rotation = Rotation.from_euler('z', rotation_angle, degrees=True)
    for i, target_position in enumerate(target_positions):
        block = blocks[i]
        place_block_with_rotation(block, target_position, rotation)