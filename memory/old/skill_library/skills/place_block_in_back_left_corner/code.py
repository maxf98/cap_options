def place_block_in_back_left_corner(workspace: Workspace, blocks: list[TaskObject]) -> None:
    """
    Place a selected block in the back left corner of the workspace, from the robot's perspective.
    :param workspace: The workspace with bounds.
    :param blocks: List of task objects in the environment.
    """
    # Retrieve all objects
    objects = get_objects()
    # Select a block to place in the corner
    selected_block = find_block_to_place(objects)
    # Calculate the back left corner position (from robot's perspective)
    # In workspace terms, back left is minimum x and y with minimum z
    back_left_x = workspace.bounds[0, 0]  # minimum x
    back_left_y = workspace.bounds[1, 0]  # minimum y
    back_left_z = workspace.bounds[2, 0]  # minimum z
    corner_position = Point3D(back_left_x, back_left_y, back_left_z)
    # Get the current pose of the block
    block_pose = get_object_pose(selected_block)
    # Move the block to the back left corner
    put_first_on_second(block_pose, Pose(position=corner_position, rotation=block_pose.rotation))
    # Notify user
    say(f"Moved {selected_block.description} to the back left corner of the workspace.")