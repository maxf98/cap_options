def build_jenga_tower_with_rotations():
    """
    Builds a Jenga tower with 3 layers of 3 blocks each. Each layer is rotated 90 degrees from the previous layer.
    """
    # Step 1: Retrieve all blocks in the environment.
    blocks = get_objects()
    # Ensure we have enough blocks to complete the task.
    if len(blocks) < 9:
        say("Not enough blocks to build a 3-layer Jenga tower.")
        return
    # Step 2: Define the position for the base layer
    base_position = calculate_workspace_center(Workspace())
    # Get the standard rotation and create a 90 degree rotation around the z-axis
    standard_rotation = get_end_effector_pose().rotation
    ninety_degree_rotation = Rotation.from_euler('z', np.pi / 2.0)
    # Step 3: Split blocks into sets for each layer
    layer_blocks = [blocks[i:i + 3] for i in range(0, 9, 3)]
    block_height = blocks[0].size[2]
    gap = 0.008
    # Step 4: Build each Jenga layer, with alternating rotations
    for i, block_set in enumerate(layer_blocks):
        layer_height = i * (block_height + gap)
        layer_position = Point3D(base_position.x, base_position.y, base_position.z + layer_height)
        # Alternate the rotation of each layer
        if i % 2 == 0:
            layer_rotation = standard_rotation
        else:
            layer_rotation = standard_rotation * ninety_degree_rotation
        layer_pose = Pose(position=layer_position, rotation=layer_rotation)
        build_jenga_layer_at_pose(block_set, layer_pose, gap)
    say("Jenga tower with 3 layers and alternating rotations has been constructed.")