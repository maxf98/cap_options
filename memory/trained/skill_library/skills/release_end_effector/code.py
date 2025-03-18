def release_end_effector():
    """releases the end effector, and any object that was previously grasped"""
    import time

    env.ee.release()
    for _ in range(500):
        p.stepSimulation()
        time.sleep(1 / 400)
