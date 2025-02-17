def calculate_aligned_pose(block1: TaskObject, block2: TaskObject, gap: float = 0.008) -> Pose:
    """
    Calculate the pose for block2 such that it is aligned lengthwise with block1.
    Parameters:
    - block1: The first block to align with.
    - block2: The second block to be moved.
    - gap: The gap to maintain between the blocks to avoid collision.
    Returns:
    - Pose: The new pose for block2.
    """
    pose1 = get_object_pose(block1)
    # Calculate the distance to move block2 to align lengthwise with block1
    # Assuming the longer side is along the x-axis
    distance = block1.size[1] / 2 + block2.size[1] / 2 + gap
    # Calculate the new position for block2 using the helper function
    new_position = get_point_at_distance_and_rotation_from_point(
        pose1.position, pose1.rotation, distance, direction=np.array([0, 1, 0])
    )
    # Use the same rotation as block1 for alignment
    new_pose = Pose(position=new_position, rotation=pose1.rotation)
    return new_pose