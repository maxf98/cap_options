def compute_center_from_size_and_corner_pose(
    size: tuple[float, float], pose: Pose
) -> Point3D:
    """utility function to compute the center of a rectangle, based on the pose from its top-left corner"""
    center = get_point_at_distance_and_rotation_from_point(
        pose.position, pose.rotation, size[0] / 2
    )
    center = get_point_at_distance_and_rotation_from_point(
        center, pose.rotation, size[1] / 2, [0, 1, 0]
    )

    return center
