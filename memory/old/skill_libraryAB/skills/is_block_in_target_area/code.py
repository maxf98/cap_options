def is_block_in_target_area(block_bbox: AABBBoundingBox, target_position: Point3D) -> bool:
    """
    Check if a block is in the target area.
    :param block_bbox: The bounding box of the block.
    :param target_position: The target position to check against.
    :return: True if the block is in the target area, False otherwise.
    """
    # Check if the block's bounding box overlaps with the target position
    return (block_bbox.minPoint.x <= target_position.x <= block_bbox.maxPoint.x and
            block_bbox.minPoint.y <= target_position.y <= block_bbox.maxPoint.y and
            block_bbox.minPoint.z <= target_position.z <= block_bbox.maxPoint.z)