def place_block_with_rotation(block: TaskObject, target_position: Point3D, rotation: Rotation):
    """
    Place a block at the target position with the specified rotation.
    :param block: The block to be placed.
    :param target_position: The target position in the workspace.
    :param rotation: The rotation to apply to the block.
    """
    pick_pose = get_object_pose(block)
    place_pose = Pose(position=target_position, rotation=rotation)
    put_first_on_second(pick_pose, place_pose)