def touch_back_side_of_block_with_end_effector():
    """
    Touch the back side of a block with the end effector, ensuring it's perpendicular,
    and approach it from a distance.
    """
    # Retrieve all objects in the workspace
    objects = get_objects()
    # Identify a block to interact with
    block = find_block_to_place(objects)
    if not block:
        say("No blocks available to interact with.")
        return
    # Retrieve the block's pose and bounding box
    block_pose = get_object_pose(block)
    block_bbox = get_bbox(block)
    block_width = block_bbox.size[0]
    # Calculate the target pose for touching the back side of the block
    touch_position = Point3D(
        block_pose.position.x - block_width / 2 - 0.01,  # slightly offset from the back
        block_pose.position.y,
        block_pose.position.z
    )
    # Calculate an approach pose, further back from the back side
    approach_position = Point3D(
        touch_position.x - 0.05,  # approach from a further distance
        touch_position.y,
        touch_position.z
    )
    # Rotate the end effector to ensure it's perpendicular to the block's back side
    target_rotation = Rotation.from_euler('z', 90, degrees=True)
    # Create Pose for the approach and touch
    approach_pose = Pose(position=approach_position, rotation=target_rotation)
    touch_pose = Pose(position=touch_position, rotation=target_rotation)
    # Move the end effector to the approach pose first
    move_end_effector_to(approach_pose)
    # Then move to the touch pose
    move_end_effector_to(touch_pose)
    say(f"Touched the back side of {block.description} with the end effector.")