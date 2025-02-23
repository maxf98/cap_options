# TASK:stack all the blocks in the middle of the workspace

blocks = get_objects()
workspace_center = Point3D((Workspace.bounds[0][0] + Workspace.bounds[0][1]) / 2, (Workspace.bounds[1][0] + Workspace.bounds[1][1]) / 2, Workspace.bounds[2][0])
base_block = blocks[0]
other_blocks = blocks[1:]
base_pose = Pose(position=workspace_center, rotation=get_object_pose(base_block).rotation)
move_end_effector_to(base_pose)
put_first_on_second(get_object_pose(base_block), base_pose)
stack_blocks(base_block, other_blocks)