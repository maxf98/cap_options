def move_block_to_center(block: TaskObject, center_position: Point3D):
    """
    Move the specified block to the center of the workspace.
    :param block: The block to be moved.
    :param center_position: The target center position in the workspace.
    """
    # Get the current pose of the block
    block_pose = get_object_pose(block)
    # Create a new pose for the center position
    center_pose = Pose(position=center_position, rotation=block_pose.rotation)
    # Move the block to the center
    put_first_on_second(block_pose, center_pose)