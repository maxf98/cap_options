def stack_blocks(blocks: list[TaskObject]):
    """ 
    Stacks multiple blocks on top of each other. The order of stacking is as provided in the list,
    with the first block in the list being placed at the bottom and each subsequent block stacked above the previous one.
    Args:
        blocks (list[TaskObject]): A list of TaskObject instances representing the blocks to be stacked.
    """
    workspace_center = Point3D(0.5, 0.0, 0.0)
    current_pose = Pose(workspace_center, None)  # Assuming no specific rotation needed
    # Stack each block on top of the previous one
    for block in blocks:
        pick_pose = get_object_pose(block)
        put_first_on_second(pick_pose, current_pose)
        # Update the current pose to be on top of the placed block
        bbox = get_bbox(block)
        height = bbox.size[2]
        current_pose.position.z += height