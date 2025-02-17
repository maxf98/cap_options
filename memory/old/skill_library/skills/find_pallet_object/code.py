def find_pallet_object(objects: list[TaskObject]) -> TaskObject:
    """
    Find the pallet object from a list of task objects.
    Assumes the pallet can be identified by its objectType.
    :param objects: List of task objects in the environment.
    :return: The pallet object.
    """
    for obj in objects:
        if obj.objectType == "pallet":  # Assuming the pallet is identified by "pallet"
            return obj
    raise ValueError("Pallet object not found in the objects list.")