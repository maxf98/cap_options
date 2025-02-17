def line_up_blocks_along_x():
    """Line up all blocks along the x-axis in the workspace, considering rotation."""
    # First, ensure the tops of all blocks are clear
    clear_all_block_tops()
    # Get all blocks in the workspace
    blocks = get_all_blocks()
    # Sort blocks by color or ID just for consistency, though this is not necessary
    blocks.sort(key=lambda block: block.id)
    # Starting position from which to line up blocks
    workspace = Workspace()
    start_x = workspace.bounds[0, 0]  # Use the leftmost x position
    y_pos = 0.0  # Keep a consistent y to align them in a line
    # Place the first block manually since it won't have any other block to align next to it
    if blocks:
        current_block_pose = get_object_pose(blocks[0])
        initial_target_position = Point3D(x=start_x, y=y_pos, z=current_block_pose.position.z)
        initial_target_pose = Pose(position=initial_target_position, rotation=current_block_pose.rotation)
        put_first_on_second(pickPose=current_block_pose, placePose=initial_target_pose)
        say(f"Placed {blocks[0].description} at initial position ({start_x}, {y_pos}).")
    # Place subsequent blocks next to the previous block
    for i in range(1, len(blocks)):
        current_block = blocks[i]
        previous_block = blocks[i - 1]
        place_block_next_to(previous_block, current_block, np.array([1, 0, 0]), 0.008)