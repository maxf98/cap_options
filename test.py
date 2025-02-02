from environments.environment import Environment
from tasks.task_primitives import EnvironmentConfiguration
import time
import pybullet as p


if __name__ == "__main__":
    env = Environment(
        "environments/assets",
        disp=True,
        shared_memory=False,
        hz=480,
        record_cfg={
            "save_video": False,
            "save_video_path": "${data_dir}/${task}-cap/videos/",
            "add_text": True,
            "add_task_text": True,
            "fps": 20,
            "video_height": 640,
            "video_width": 720,
        },
    )
    from tasks.tasks.many_blocks import ManyBlocksTask
    from tasks.tasks.precision_cylinder_tower import PrecisionCylinderTower
    from tasks.task_primitives import LoadedTask

    env.set_task(ManyBlocksTask())
    env.reset()

    time.sleep(10)

    # for i in range(1000):
    #     p.stepSimulation()
    
    # config = env.task.get_current_configuration(env)

    # config.dump("config.pkl")

    # time.sleep(10)

 