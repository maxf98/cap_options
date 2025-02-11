def move_block_to_back_right_corner(block: TaskObject, workspace: Workspace):
    """
    Move the specified block to the back-right corner of the workspace.
    :param block: The block to be moved.
    :param workspace: The workspace containing the bounds.
    """
    # Calculate the back-right corner position
    back_right_corner = calculate_back_right_corner(workspace.bounds)
    # Move the block to the back-right corner
    move_block_to_position(block, back_right_corner)