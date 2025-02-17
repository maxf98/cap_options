def clear_block_top(block: TaskObject):
    """
    Ensure that a block has no other blocks on top of it by removing them first.
    :param block: The block to clear.
    """
    objects = get_objects()
    blocks_on_top = get_objects_on_top(block, objects)
    if blocks_on_top:
        for b in blocks_on_top:
            # Move the block on top to a safe location
            current_pose = get_object_pose(b)
            safe_position = Point3D(x=current_pose.position.x + 0.2, y=current_pose.position.y, z=current_pose.position.z)
            safe_pose = Pose(position=safe_position, rotation=current_pose.rotation)
            put_first_on_second(current_pose, safe_pose)
            say(f"Moved {b.description} from top of {block.description} to ensure clearance.")