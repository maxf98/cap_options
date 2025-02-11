def place_block_in_back_left_corner(block: TaskObject):
    """
    Place the given block in the back-left corner of the workspace.
    :param block: The block to be placed.
    """
    workspace = Workspace()
    back_left_corner = calculate_back_left_corner(workspace.bounds)
    move_block_to_position(block, back_left_corner)
    say(f"Block {block.description} has been moved to the back-left corner.")