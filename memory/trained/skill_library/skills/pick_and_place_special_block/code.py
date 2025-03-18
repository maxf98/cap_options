from utils.core_types import *


def pick_and_place_special_object(special_object: TaskObject, place_pose: Pose):
    """Picks up a special object from the workspace and places it at a specified position.
    The function determines the appropriate grasp pose for picking up the object and uses the specified place pose for placement.
    Args:
        special_object (TaskObject): The special object to be picked up and placed.
        place_pose (Pose): The pose to be used for placing the special object.
    """
    special_object_pose = get_object_pose(special_object)
    size = get_object_size(special_object)

    # Calculate the distance as half of the object's length in its longest dimension
    distance = max(size) / 2

    # Get both ends' positions
    point_end1 = get_point_at_distance_and_rotation_from_point(
        special_object_pose.position, special_object_pose.rotation, -distance
    )
    point_end2 = get_point_at_distance_and_rotation_from_point(
        special_object_pose.position, special_object_pose.rotation, distance
    )

    # Choose one end to grasp, here we choose end1 arbitrarily
    special_object_pick_pose = Pose(point_end1, special_object_pose.rotation)
    put_first_on_second(special_object_pick_pose, place_pose)
