def move_block_to_center():
    """
    Finds a block available to move and places it in the center of the workspace.
    This function utilizes pre-defined methods to select a block and calculate the center position,
    to ensure modularity and reusability.
    """
    # Get all objects in the workspace
    objects = get_objects()
    # Find a block to place
    block_to_place = find_block_to_place(objects)
    # Calculate the workspace center position
    workspace = Workspace()  # The workspace boundaries are predefined
    center_position = calculate_workspace_center(workspace)
    # Get current Pose of the block
    current_pose = get_object_pose(block_to_place)
    # Create a new Pose at the center of the workspace with the current rotation
    center_pose = Pose(position=center_position, rotation=current_pose.rotation)
    # Move the block to the center of the workspace
    put_first_on_second(pickPose=current_pose, placePose=center_pose)