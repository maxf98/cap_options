def align_blocks_lengthwise():
    """
    Align two blocks lengthwise in the environment.
    """
    # Find the blocks
    block1, block2 = find_blocks()
    # Calculate the new pose for block2
    new_pose = calculate_aligned_pose(block1, block2)
    # Move block2 to the new pose
    current_pose_block2 = get_object_pose(block2)
    put_first_on_second(current_pose_block2, new_pose)
    # Confirm the action
    say("Blocks have been aligned lengthwise.")