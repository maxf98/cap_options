def build_cube_in_workspace():
    """Builds a 2x2x2 cube using 8 blocks in the center of the workspace."""
    # Step 1: Retrieve all blocks in the environment
    blocks = get_objects()
    # Step 2: Ensure there are enough blocks to build the cube
    if len(blocks) < 8:
        say("Not enough blocks to build the 2x2x2 cube. Need exactly 8 blocks.")
        return
    # Step 3: Determine the pose for the cube base
    center_position = calculate_workspace_center(Workspace())
    standard_rotation = get_end_effector_pose().rotation
    cube_pose = Pose(position=center_position, rotation=standard_rotation)
    # Step 4: Clear the area for the cube
    clear_area_for_cube(cube_pose, cube_size=0.08, gap=0.008)
    # Step 5: Ensure each block is cleared before building
    for block in blocks:
        clear_block_top(block)
    # Step 6: Build the cube using the available function
    gap = 0.008  # Defined gap between blocks
    build_2x2x2_cube(blocks, cube_pose, gap)