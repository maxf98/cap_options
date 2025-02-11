def is_block_on_zone(block_bbox: AABBBoundingBox, zone_bbox: AABBBoundingBox) -> bool:
    """
    Check if a block is on the specified zone based on x and y overlap.
    :param block_bbox: The bounding box of the block.
    :param zone_bbox: The bounding box of the zone.
    :return: True if the block overlaps with the zone in the x and y dimensions, False otherwise.
    """
    # Check if the block's x and y bounds overlap with the zone's x and y bounds
    return (zone_bbox.minPoint.x <= block_bbox.maxPoint.x and
            zone_bbox.maxPoint.x >= block_bbox.minPoint.x and
            zone_bbox.minPoint.y <= block_bbox.maxPoint.y and
            zone_bbox.maxPoint.y >= block_bbox.minPoint.y)