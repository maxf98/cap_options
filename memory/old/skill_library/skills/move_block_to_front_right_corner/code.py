def move_block_to_front_right_corner(workspace: Workspace) -> None:
    """
    Move a block to the front right corner of the workspace (bottom-right from the robot's perspective).
    :param workspace: The workspace with bounds.
    """
    # 1. Get all blocks in the workspace
    blocks = get_objects()
    # 2. Find a block to move
    block_to_move = find_block_to_place(blocks)
    if block_to_move:
        # 3. Calculate the front right corner position
        front_right_position = get_front_right_corner_position(workspace)
        # 4. Get current pose of the block to move
        pick_pose = get_object_pose(block_to_move)
        # Create a place pose with the calculated position and the block's rotation
        place_pose = Pose(position=front_right_position, rotation=pick_pose.rotation)
        # 5. Use the pick-and-place primitive to move the block
        put_first_on_second(pick_pose, place_pose)
    else:
        say("No block available to move.")