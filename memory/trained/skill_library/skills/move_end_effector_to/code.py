def move_end_effector_to(pose: Pose, speed=0.001):
    """moves the end effector from its current Pose to a given new Pose"""
    suction_height = 0.05
    pose0 = _to_pybullet_pose(get_end_effector_pose())
    pose1 = _to_pybullet_pose(pose)
    pos0 = np.float32(pose0[0])
    pos1 = np.float32((pose1[0][0], pose1[0][1], pose1[0][2] + suction_height))
    vec = np.float32(pos1) - np.float32(pos0)
    length = np.linalg.norm(vec)
    vec = vec / length
    pos0 -= vec * 0.02
    pos1 -= vec * 0.05

    rot = (pose1[1] + np.pi) % (2 * np.pi) - np.pi
    timeout = env.movep((pos0, rot))

    n_push = np.int32(np.floor(np.linalg.norm(pos1 - pos0) / 0.01))
    for _ in range(n_push):
        target = pos0 + vec * n_push * 0.01
        timeout |= env.movep((target, rot), speed=speed)
    timeout |= env.movep((pos1, rot), speed=speed)
