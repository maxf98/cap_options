def place_block_in_back_right_corner(workspace: Workspace, blocks: list[TaskObject]) -> None:
    """
    Place a selected block in the back right corner of the workspace, from the robot's perspective.
    :param workspace: The workspace with bounds.
    :param blocks: List of task objects in the environment.
    """
    # Find block to use
    block_to_place = find_block_to_place(blocks)
    # Get the pose of the block
    block_pose = get_object_pose(block_to_place)
    # Calculate the target position in the back right corner
    back_right_corner_position = get_back_right_corner_position(workspace)
    # Create a new Pose for the back right corner with the same rotation as the block
    target_pose = Pose(position=back_right_corner_position, rotation=block_pose.rotation)
    # Move the block to the back right corner
    put_first_on_second(block_pose, target_pose)