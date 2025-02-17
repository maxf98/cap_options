def get_zone_object() -> TaskObject:
    """
    Retrieve the zone object by its objectType.
    :return: The TaskObject representing the zone.
    """
    objects = get_objects()
    for obj in objects:
        if obj.objectType == "zone":
            return obj
    raise ValueError("Zone object not found.")