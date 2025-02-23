# TASK:pick up and put down all the green blocks in the environment

green_blocks = retrieve_blocks(color='green')
starting_pose = Pose(Point3D(0.5, 0, 0.1), None)
for block in green_blocks:
    block_pose = get_object_pose(block)
    put_first_on_second(block_pose, starting_pose)
    put_first_on_second(starting_pose, block_pose)