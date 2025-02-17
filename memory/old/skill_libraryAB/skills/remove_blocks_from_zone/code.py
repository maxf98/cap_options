def remove_blocks_from_zone(target_position: Point3D):
    """
    Remove all blocks from the specified zone and place them at the target position.
    :param target_position: The position where the blocks will be moved to.
    """
    # Get the zone object and its bounding box
    zone = get_zone_object()
    zone_bbox = get_bbox(zone)
    # Get all objects in the environment
    blocks = get_objects()
    # Iterate over each block and check if it is on the zone
    for block in blocks:
        block_bbox = get_bbox(block)
        if is_block_on_zone(block_bbox, zone_bbox):
            # Move the block to the target position
            move_block_to_position(block, target_position)
            say(f"Moved {block.description} to target position.")