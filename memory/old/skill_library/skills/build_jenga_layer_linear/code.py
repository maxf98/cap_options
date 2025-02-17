def build_jenga_layer_linear(workspace: Workspace, gap: float = 0.008):
    """
    Constructs a single layer of a Jenga tower using three blocks in the workspace.
    The blocks are placed directly next to each other in a line to form a single layer.
    :param workspace: The workspace where the blocks should be arranged.
    :param gap: The gap to maintain between adjacent blocks.
    """
    # Step 1: Retrieve all blocks in the environment.
    blocks = get_objects()
    # Ensure we have enough blocks to complete the layer
    if len(blocks) < 3:
        say("Not enough blocks to build a Jenga layer.")
        return
    # Select three blocks to use
    selected_blocks = blocks[:3]
    # Step 2: Determine starting position for the Jenga layer
    starting_position = calculate_workspace_center(workspace)  # This gives a starting point in the middle
    # Assume the blocks have size dimensions where blocks[0].size[0] < blocks[0].size[1] resembles (width < length)
    block_length = selected_blocks[0].size[1]  # Longer side, typically the length
    # Use a standard rotation (e.g., identity rotation or current end-effector rotation)
    standard_rotation = get_end_effector_pose().rotation
    # Place first block
    first_block_pose = Pose(position=starting_position, rotation=standard_rotation)
    put_first_on_second(get_object_pose(selected_blocks[0]), first_block_pose)
    # Compute the position for the second block placed side by side with the first along its length
    second_block_position = get_point_at_distance_and_rotation_from_point(
        point=first_block_pose.position,
        rotation=standard_rotation,
        distance=(block_length + gap),  # Align next to first block along length
        direction=np.array([0, 1, 0])  # Assuming arrangement along the y-axis
    )
    second_block_pose = Pose(position=second_block_position, rotation=standard_rotation)
    put_first_on_second(get_object_pose(selected_blocks[1]), second_block_pose)
    # Compute position for the third block, continuing in the same direction to complete the row
    third_block_position = get_point_at_distance_and_rotation_from_point(
        point=second_block_pose.position,
        rotation=standard_rotation,
        distance=(block_length + gap),  # Continue alignment along length
        direction=np.array([0, 1, 0])  # Continue along the y-axis
    )
    third_block_pose = Pose(position=third_block_position, rotation=standard_rotation)
    put_first_on_second(get_object_pose(selected_blocks[2]), third_block_pose)
    say("Single Jenga layer constructed as a straight line.")