from environments.environment import Environment

def get_obj_pos(env: Environment, obj_id: int) -> tuple[float, float, float]:
    return env.get_obj_pos(obj_id)
