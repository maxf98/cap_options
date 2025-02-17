def move_block_to_position(block: TaskObject, target_position: Point3D):
    """
    Move the specified block to the target position.
    :param block: The block to be moved.
    :param target_position: The target position in the workspace.
    """
    block_pose = get_object_pose(block)
    target_pose = Pose(position=target_position, rotation=block_pose.rotation)
    put_first_on_second(block_pose, target_pose)