def move_block_to_top_left_corner():
    """
    Main function to move the block to the top left corner of the workspace.
    """
    # Get all objects in the environment
    objects = get_objects()
    # Find the block object
    block = find_block(objects)
    # Get the current pose of the block
    block_pose = get_object_pose(block)
    # Calculate the top left corner position
    top_left_corner = find_top_left_corner(Workspace())
    # Create a new pose for placing the block at the top left corner
    place_pose = Pose(position=top_left_corner, rotation=block_pose.rotation)
    # Move the block to the top left corner
    put_first_on_second(block_pose, place_pose)
    # Announce completion
    say("Block has been moved to the top left corner of the workspace.")