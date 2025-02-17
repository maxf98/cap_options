def remove_all_blocks_from_zone_with_buffer():
    """Remove all blocks from the zone, including those slightly around it."""
    # Retrieve all objects within the workspace
    objects = get_objects()
    # Identify the zone object from the list
    zone_object = find_zone_object(objects)
    # Get the pose of the zone to determine blocks that are nearby
    zone_pose = get_object_pose(zone_object)
    # Define a buffer distance to extend the zone boundary
    buffer_distance = 0.15
    # Initialize a list to hold blocks that are within or near the zone
    blocks_near_zone = []
    # Function to determine if a block is near the zone
    def is_block_near_zone(block_pose: Pose, zone_pose: Pose):
        # Check if the block is within a certain distance from the zone center
        if np.linalg.norm(block_pose.position.np_vec - zone_pose.position.np_vec) < buffer_distance:
            return True
        return False
    # Identify blocks within the zone or near its buffered area
    for obj in objects:
        if obj.objectType == "block":
            block_pose = get_object_pose(obj)
            if is_block_near_zone(block_pose, zone_pose):
                blocks_near_zone.append((obj, block_pose))
    # Move each block out of the buffered area around the zone
    for block, block_pose in blocks_near_zone:
        # Designate a new position outside the buffered zone area
        outside_zone_position = Point3D(x=zone_pose.position.x - 0.3, y=zone_pose.position.y, z=zone_pose.position.z)
        outside_zone_pose = Pose(position=outside_zone_position, rotation=block_pose.rotation)
        # Move the block to the outside position
        put_first_on_second(pickPose=block_pose, placePose=outside_zone_pose)
        say(f"Moved {block.description} out of the zone.")