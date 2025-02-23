def stack_blocks(base_block: TaskObject, other_blocks: list[TaskObject]):
    """Stacks a list of blocks on top of a base block."""
    base_pose = get_object_pose(base_block)
    current_pose = base_pose
    for block in other_blocks:
        # Get the size of the block to calculate the next placement position
        bbox = get_bbox(block)
        block_height = bbox.size[2]
        # Calculate the new position to place the block on top of the current pose
        new_position = Point3D(
            current_pose.position.x,
            current_pose.position.y,
            current_pose.position.z + block_height
        )
        new_pose = Pose(position=new_position, rotation=current_pose.rotation)
        # Place the block
        put_first_on_second(get_object_pose(block), new_pose)
        # Update the current pose to the new pose for the next iteration
        current_pose = new_pose