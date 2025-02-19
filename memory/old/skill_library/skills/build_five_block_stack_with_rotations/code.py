def build_five_block_stack_with_rotations():
    """Builds a vertical stack of 5 blocks, each rotated 45 degrees relative to the previous one."""
    # Step 1: Retrieve all blocks in the environment
    blocks = get_objects()
    # Step 2: Ensure there are enough blocks to build the stack
    if len(blocks) < 5:
        say("Not enough blocks to build a stack of 5. Need exactly 5 blocks.")
        return
    # Step 3: Determine the base position for the stack
    center_position = calculate_workspace_center(Workspace())
    # Step 4: Get the standard rotation
    standard_rotation = get_end_effector_pose().rotation
    # Step 5: Create a 45-degree rotation around the z-axis
    forty_five_degree_rotation = Rotation.from_euler('z', np.pi / 4.0)
    # Step 6: Build the stack with rotating each block
    current_rotation = standard_rotation
    current_position = center_position
    block_height = blocks[0].size[2]
    for i in range(5):
        # Rotate each block 45 degrees from the previous block
        current_rotation = current_rotation * forty_five_degree_rotation if i > 0 else standard_rotation
        # Calculate the new position for the current block
        new_position = Point3D(
            current_position.x, 
            current_position.y, 
            current_position.z + (block_height * i))
        # Create a new pose for the current block
        new_pose = Pose(new_position, current_rotation)
        # Use the pick-and-place function to stack the current block
        put_first_on_second(get_object_pose(blocks[i]), new_pose)
        # Update the current position
        current_position = new_position
    say("Successfully built a stack of 5 blocks with 45 degree rotation between each.")