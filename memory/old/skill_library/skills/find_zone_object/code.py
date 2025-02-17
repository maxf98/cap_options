def find_zone_object(objects: list[TaskObject]) -> TaskObject:
    """
    Find the zone object from a list of task objects.
    Assumes the zone is identified by a specific objectType or other attributes.
    """
    for obj in objects:
        if obj.objectType == "zone":
            return obj
    raise ValueError("Zone object not found in the objects list.")