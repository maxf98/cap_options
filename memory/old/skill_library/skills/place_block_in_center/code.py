def place_block_in_center():
    """Move a block to the center of the workspace."""
    blocks = get_objects()
    selected_block = find_block_to_place(blocks)
    center_position = calculate_workspace_center(Workspace())
    current_block_pose = get_object_pose(selected_block)
    center_pose = Pose(position=center_position, rotation=current_block_pose.rotation)
    put_first_on_second(pickPose=current_block_pose, placePose=center_pose)
    say(f"Placed {selected_block.description} at the center of the workspace.")