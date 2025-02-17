def build_2x2x2_cube(blocks: list[TaskObject], cube_pose: Pose, gap: float):
    """
    Build a 2x2x2 cube using 8 blocks, starting from a given pose and with specified gaps between blocks.
    :param blocks: The list of TaskObjects to use for building the cube.
    :param cube_pose: The Pose where the base of the cube should be positioned (includes position and rotation).
    :param gap: The gap to maintain between adjacent blocks.
    """
    if len(blocks) < 8:
        say("Not enough blocks to build the 2x2x2 cube. Need exactly 8 blocks.")
        return
    # Extract position and rotation from the cube_pose
    base_position = cube_pose.position
    standard_rotation = cube_pose.rotation
    # Build first layer positions (2x2)
    layer_1_positions = [
        base_position,
        get_point_at_distance_and_rotation_from_point(base_position, standard_rotation, distance=0.04 + gap, direction=np.array([1, 0, 0])),
        get_point_at_distance_and_rotation_from_point(base_position, standard_rotation, distance=0.04 + gap, direction=np.array([0, 1, 0])),
        get_point_at_distance_and_rotation_from_point(base_position, standard_rotation, distance=0.04 + gap, direction=np.array([1, 1, 0]))
    ]
    # Place first layer blocks
    for i in range(4):
        place_pose = Pose(layer_1_positions[i], standard_rotation)
        put_first_on_second(get_object_pose(blocks[i]), place_pose)
    # Calculate the positions for the second layer, directly above the first
    height_offset = 0.04 + gap  # Single block height including gap
    layer_2_positions = [
        Point3D(pos.x, pos.y, pos.z + height_offset) for pos in layer_1_positions
    ]
    # Place second layer blocks
    for i in range(4, 8):
        place_pose = Pose(layer_2_positions[i - 4], standard_rotation)
        put_first_on_second(get_object_pose(blocks[i]), place_pose)
    say("2x2x2 cube has been built at the specified pose with the specified gap.")