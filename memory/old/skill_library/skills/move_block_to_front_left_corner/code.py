def move_block_to_front_left_corner(workspace: Workspace, blocks: list[TaskObject]) -> None:
    """
    Move a block to the front left corner of the workspace (top-right from the robot's perspective).
    :param workspace: The workspace with bounds.
    :param blocks: List of task objects in the environment.
    """
    # Select a block to move
    block_to_move = find_block_to_place(blocks)
    # Get the current pose of the block
    pick_pose = get_object_pose(block_to_move)
    # Calculate the position for the front left corner
    front_left_position = get_front_left_corner_position(workspace)
    # Create the new pose for placing the block
    place_pose = Pose(front_left_position, pick_pose.rotation)
    # Move the block
    put_first_on_second(pick_pose, place_pose)