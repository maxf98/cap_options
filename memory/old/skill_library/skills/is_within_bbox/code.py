def is_within_bbox(position: Point3D, bbox: AABBBoundingBox) -> bool:
    """Check if a position is within the bounding box defined by min and max points in the x-y plane."""
    return (
        bbox.minPoint.x <= position.x <= bbox.maxPoint.x and
        bbox.minPoint.y <= position.y <= bbox.maxPoint.y
    )