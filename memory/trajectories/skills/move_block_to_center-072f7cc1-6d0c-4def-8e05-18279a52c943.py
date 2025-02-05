def move_block_to_center():
    """
    Move the block to the center of the workspace.
    """
    # Find the block
    block = find_block()
    # Get the current pose of the block
    block_pose = get_object_pose(block)
    # Calculate the center of the workspace
    center_point = find_center_of_workspace()
    # Create a new pose for the center of the workspace
    center_pose = Pose(position=center_point, rotation=block_pose.rotation)
    # Move the block to the center of the workspace
    put_first_on_second(block_pose, center_pose)
    # Announce completion
    say("Block has been moved to the center of the workspace.")