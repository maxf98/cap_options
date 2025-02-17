def put_block_in_zone():
    """
    Put a block into the zone object within the workspace.
    """
    # Retrieve all objects within the workspace
    objects = get_objects()
    # Identify the zone object from the list
    zone_object = find_zone_object(objects)
    # Select a block to put into the zone
    block_to_place = find_block_to_place(objects)
    # Get the current pose of the block
    block_pose = get_object_pose(block_to_place)
    # Get the pose of the zone
    zone_pose = get_object_pose(zone_object)
    # Move the block to the zone's position
    put_first_on_second(pickPose=block_pose, placePose=zone_pose)
    # Notify the user
    say(f"Moved {block_to_place.description} into the zone.")