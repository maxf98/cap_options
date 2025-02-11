def is_block_on_pallet(block: TaskObject, pallet_bbox: AABBBoundingBox) -> bool:
    """
    Check if a block is on top of the pallet using its position.
    :param block: The block to check.
    :param pallet_bbox: The bounding box of the pallet.
    :return: True if the block is on top of the pallet, False otherwise.
    """
    block_bbox = get_bbox(block)
    block_position = Point3D(
        (block_bbox.minPoint.x + block_bbox.maxPoint.x) / 2,
        (block_bbox.minPoint.y + block_bbox.maxPoint.y) / 2,
        (block_bbox.minPoint.z + block_bbox.maxPoint.z) / 2
    )
    # Check if the block's position is within the pallet's bounding box in the x and y dimensions
    # and above the pallet's top surface in the z dimension
    return (pallet_bbox.minPoint.x <= block_position.x <= pallet_bbox.maxPoint.x and
            pallet_bbox.minPoint.y <= block_position.y <= pallet_bbox.maxPoint.y and
            block_position.z > pallet_bbox.maxPoint.z)