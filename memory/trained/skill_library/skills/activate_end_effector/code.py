def activate_end_effector():
    """activates the gripper - if there is an object in contact with the gripper, it will grasp this object
    if there is no object, it just won't work"""
    env.ee.activate()
