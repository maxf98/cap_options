def place_block_in_middle_of_left_side():
    """
    Place a block at the middle of the side with the minimal y-coordinate (left side) of the workspace.
    """
    # Retrieve all objects within the workspace
    objects = get_objects()
    # Select a block to place
    block = find_block_to_place(objects)
    if not block:
        say("No blocks available to move.")
        return
    # Calculate the middle position of the left side
    middle_of_left_side_position = calculate_middle_of_min_y_side(Workspace())
    # Retrieve the block's current pose
    current_pose = get_object_pose(block)
    # Create a new pose for placing the block at the middle of the left side position
    place_pose = Pose(position=middle_of_left_side_position, rotation=current_pose.rotation)
    # Move the block to the middle of the left side location
    put_first_on_second(pickPose=current_pose, placePose=place_pose)
    say(f"Placed {block.description} at the middle of the left side of the workspace.")