def remove_all_blocks_from_zone(target_position: Point3D):
    """
    Remove all blocks from the specified zone and place them at the target position.
    :param target_position: The position where the blocks will be moved to.
    """
    # Retrieve the zone object
    zone_object = get_zone_object()
    zone_bbox = get_bbox(zone_object)
    # Get all objects in the environment
    all_objects = get_objects()
    # Filter out blocks that are within the zone
    blocks_in_zone = []
    for obj in all_objects:
        if obj.objectType == 'block':
            block_bbox = get_bbox(obj)
            if is_block_on_zone(block_bbox, zone_bbox):
                blocks_in_zone.append(obj)
    # Remove blocks from the zone and place them at the target position
    for block in blocks_in_zone:
        move_block_to_position(block, target_position)