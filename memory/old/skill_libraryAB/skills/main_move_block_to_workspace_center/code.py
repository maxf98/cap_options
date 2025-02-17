def main_move_block_to_workspace_center():
    """
    Main function to move a block to the center of the workspace.
    """
    # Calculate the center of the workspace
    workspace_center = calculate_workspace_center(Workspace.bounds)
    # Get all objects in the environment
    objects = get_objects()
    # Assume the first block in the list is the one to be moved
    block_to_move = objects[0]
    # Clear the target area at the center of the workspace
    clear_target_area([workspace_center], objects)
    # Move the block to the center of the workspace
    move_block_to_center(block_to_move, workspace_center)
    # Notify the user
    say(f"Moved {block_to_move.description} to the center of the workspace.")