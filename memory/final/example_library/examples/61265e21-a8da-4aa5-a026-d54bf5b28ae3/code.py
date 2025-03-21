# TASK: stack all the blocks in the middle of the workspace

blocks = get_objects()
workspace_center = Point3D(0.5, 0.0, 0.0)
middle_block = blocks[0]
middle_block_position = get_object_pose(middle_block).position
blocks.sort(key=lambda block: get_object_pose(block).position.z)
current_base_pose = Pose(workspace_center, Rotation.identity())
put_first_on_second(get_object_pose(middle_block), current_base_pose)
current_base_pose = get_object_pose(middle_block)
for block in blocks:
    if block != middle_block:
        block_pose = get_object_pose(block)
        put_first_on_second(block_pose, current_base_pose)
        current_base_pose = get_object_pose(block)