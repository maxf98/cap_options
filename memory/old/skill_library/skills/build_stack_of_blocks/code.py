def build_stack_of_blocks(
    blocks: list[TaskObject],
    number_of_blocks: int,
    stack_base_position: Point3D,
    standard_rotation: Rotation,
):
    """
    Build a stack of the given number of blocks starting at a specified position with a consistent rotation.
    :param blocks: The list of TaskObjects available for stacking.
    :param number_of_blocks: The number of blocks to stack upon each other.
    :param stack_base_position: The base position in 3D space where the stack should start.
    :param standard_rotation: The standard rotation to keep consistent across all blocks in the stack.
    """
    if len(blocks) < number_of_blocks:
        say(
            f"Not enough blocks to build a stack of {number_of_blocks}. Only {len(blocks)} blocks are provided."
        )
        return
    # Initialize the position for the base of the stack
    current_position = stack_base_position
    for i in range(number_of_blocks):
        # Get the current block pose
        current_block_pose = get_object_pose(blocks[i])
        # Calculate the new position directly on top of the previous block
        # Ensure no vertical gap between stacked blocks
        new_position = Point3D(
            current_position.x,
            current_position.y,
            current_position.z + (i * blocks[i - 1].size[2] if i > 0 else 0),
        )
        # Create a new pose for where the current block will be placed with the standard rotation
        new_pose = Pose(new_position, standard_rotation)
        # Use the pick-and-place function to stack the current block
        put_first_on_second(current_block_pose, new_pose)
        # Update current position for the next block
        current_position = new_position
    say(f"Successfully built a stack of {number_of_blocks} blocks.")
