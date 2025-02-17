def place_block_at_pose(block: TaskObject, target_pose: Pose) -> bool:
    """
    Place a block at the specified pose and check if the placement was successful.
    :param block: The block to be placed.
    :param target_pose: The desired pose where the block should be placed.
    :return: Boolean indicating if the placement was successful.
    """
    # Get the current pose of the block
    current_pose = get_object_pose(block)
    # Move the block to the specified target pose
    put_first_on_second(pickPose=current_pose, placePose=target_pose)
    # Verify if the block was successfully placed at the target location
    new_pose = get_object_pose(block)
    successful_placement = (
        np.isclose(new_pose.position.x, target_pose.position.x, atol=0.01) and
        np.isclose(new_pose.position.y, target_pose.position.y, atol=0.01) and
        np.isclose(new_pose.position.z, target_pose.position.z, atol=0.01) and
        new_pose.rotation.approx_equal(target_pose.rotation, atol=0.01)
    )
    return successful_placement