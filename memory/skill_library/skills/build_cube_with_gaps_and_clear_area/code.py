def build_cube_with_gaps_and_clear_area():
    """
    Build a 2x2x2 cube using 8 blocks by picking and placing them in the correct positions
    with a consistent rotation for all blocks, a small gap between them, and ensuring the area is clear.
    """
    # Get all objects in the environment
    blocks = get_objects()
    # Define the size of each block (assuming all blocks are the same size)
    block_size = blocks[0].size
    # Define the starting position for the cube
    start_position = Point3D(0.4, 0.0, block_size[2] / 2)
    # Define a small gap to leave between blocks
    gap = 0.005  # 5mm gap
    # Calculate the target positions for the 8 blocks to form a 2x2x2 cube with gaps
    target_positions = calculate_target_positions_with_gaps(start_position, block_size, gap)
    # Define a consistent rotation for all blocks (e.g., no rotation)
    consistent_rotation = Rotation.from_euler('xyz', [0, 0, 0])
    # Clear the target area if necessary
    clear_target_area(target_positions, blocks)
    # Iterate over each block and place it at the corresponding target position
    for i, block in enumerate(blocks):
        pick_pose = get_object_pose(block)
        place_pose = Pose(position=target_positions[i], rotation=consistent_rotation)
        put_first_on_second(pick_pose, place_pose)
        say(f"Placed block {block.description} at position {target_positions[i]} with consistent rotation and gap")