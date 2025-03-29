# TASK: stack all the cylinders in the top left corner

cylinders = get_cylinders()
stacking_start_pose = Pose(Point3D(0.25, -0.5, 0), Rotation.identity())
stack_blocks(cylinders, stacking_start_pose)