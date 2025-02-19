def touch_left_side_of_block_with_end_effector():
    """
    Touch the left side of a block with the end effector, ensuring it's perpendicular,
    and approach it in three steps: move in XY-plane, move vertically, and then finalize positioning.
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
    block_depth = block_bbox.size[1]
    # Get the current end effector pose
    current_end_effector_pose = get_end_effector_pose()
    # Step 1: Move horizontally in the XY-plane above the target position
    xy_approach_position = Point3D(
        block_pose.position.x,
        block_pose.position.y - block_depth / 2 - 0.05,  # approach from further left
        current_end_effector_pose.position.z  # keep the current height of the end effector
    )
    move_end_effector_to(Pose(position=xy_approach_position, rotation=current_end_effector_pose.rotation))
    # Step 2: Move vertically down to align with the block height
    vertical_approach_position = Point3D(
        xy_approach_position.x,
        xy_approach_position.y,
        block_pose.position.z  # align vertically with the block
    )
    move_end_effector_to(Pose(position=vertical_approach_position, rotation=current_end_effector_pose.rotation))
    # Step 3: Finalize position and touch the left side of the block
    touch_position = Point3D(
        block_pose.position.x,
        block_pose.position.y - block_depth / 2 - 0.01,  # slightly offset for safety
        block_pose.position.z
    )
    move_end_effector_to(Pose(position=touch_position, rotation=current_end_effector_pose.rotation))
    say(f"Touched the left side of {block.description} with the end effector.")