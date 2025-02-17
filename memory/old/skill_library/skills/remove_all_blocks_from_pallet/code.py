def remove_all_blocks_from_pallet():
    """Remove all blocks from the pallet."""
    # Retrieve all objects within the workspace
    objects = get_objects()
    # Identify the pallet object from the list
    pallet_object = find_pallet_object(objects)
    # Get the current pose of the pallet
    pallet_pose = get_object_pose(pallet_object)
    # Define a buffer distance to include blocks that are slightly on the pallet boundaries
    buffer_distance = 0.15
    # Function to determine if a block is on or near the pallet
    def is_block_near_pallet(block_pose: Pose, pallet_pose: Pose):
        # Check if the block is within a certain distance from the pallet center
        return np.linalg.norm(block_pose.position.np_vec - pallet_pose.position.np_vec) < buffer_distance
    # Identify blocks on the pallet or within its buffered area
    blocks_near_pallet = [
        obj for obj in objects if is_block(obj) and is_block_near_pallet(get_object_pose(obj), pallet_pose)
    ]
    # Move each block out of the buffered area around the pallet
    for block in blocks_near_pallet:
        # Retrieve the current pose of the block immediately before movement
        current_block_pose = get_object_pose(block)
        # Designate a new position outside the buffered pallet area
        outside_pallet_x = 0.2  # Assuming a safe position to the side of the pallet
        outside_pallet_position = Point3D(x=outside_pallet_x, y=pallet_pose.position.y, z=pallet_pose.position.z)
        outside_pallet_pose = Pose(position=outside_pallet_position, rotation=current_block_pose.rotation)
        # Move the block to the outside position
        put_first_on_second(pickPose=current_block_pose, placePose=outside_pallet_pose)
        say(f"Moved {block.description} out of the pallet.")