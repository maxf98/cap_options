def get_highest_point_on_stack(stack_base_pose, stack_height, block_size):
    """
    Calculate the highest point on the current stack.
    :param stack_base_pose: Pose of the base of the stack.
    :param stack_height: Current height of the stack.
    :param block_size: Size of a single block.
    :return: Pose representing the highest point on the stack.
    """
    new_position = Point3D(stack_base_pose.position.x, stack_base_pose.position.y, stack_base_pose.position.z + stack_height * block_size[2])
    return Pose(new_position, stack_base_pose.rotation)