def pick(object: TaskObject) -> bool:
    """moves end effector to the pick pose and activates"""
    object_pose = get_object_pose(object)
    size = get_object_size(object)
    pick_pose = Pose(
        object_pose.position.translate(Point3D(0, 0, size[2] / 2)), object_pose.rotation
    )
    pick_pose = _to_pybullet_pose(pick_pose)
    speed = 0.001
    # Execute picking primitive.
    prepick_to_pick = ((0, 0, 0.32), (0, 0, 0, 1))
    prepick_pose = utils.multiply(pick_pose, prepick_to_pick)
    timeout = env.movep(prepick_pose, speed)

    # Move towards pick pose until contact is detected.
    delta = (np.float32([0, 0, -0.001]), utils.eulerXYZ_to_quatXYZW((0, 0, 0)))
    targ_pose = prepick_pose
    while not env.ee.detect_contact():  # and target_pose[2] > 0:
        targ_pose = utils.multiply(targ_pose, delta)
        timeout |= env.movep(targ_pose)
        if timeout:
            return True

    # Activate end effector, move up, and check picking success.
    env.ee.activate()
    pick_success = env.ee.check_grasp()
    return pick_success
