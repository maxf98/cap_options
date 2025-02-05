from environments.environment import Environment
from tasks.task import EnvironmentConfiguration
import time
import pybullet as p


if __name__ == "__main__":
    # env = Environment(
    #     "environments/assets",
    #     disp=True,
    #     shared_memory=False,
    #     hz=480,
    #     record_cfg={
    #         "save_video": False,
    #         "save_video_path": "${data_dir}/${task}-cap/videos/",
    #         "add_text": True,
    #         "add_task_text": True,
    #         "fps": 20,
    #         "video_height": 640,
    #         "video_width": 720,
    #     },
    # )

    # from tasks.task import Task
    # from tasks.tasks.build_cube import ManyBlocksTask

    # # task = Task(config_path="config.pkl")

    # env.reset()

    # time.sleep(10)

    # for i in range(1000):
    #     p.stepSimulation()

    # config = env.task.get_current_configuration(env)

    # config.dump("config.pkl")

    # time.sleep(10)

    x = None
    b = x or 5
    y = 6
    c = y or 5
    print(b)
    print(c)
