def calculate_workspace_center(bounds: np.array) -> Point3D:
    """
    Calculate the center point of the workspace.
    :param bounds: The bounds of the workspace as a numpy array.
    :return: The center point of the workspace as a Point3D object.
    """
    center_x = (bounds[0][0] + bounds[0][1]) / 2
    center_y = (bounds[1][0] + bounds[1][1]) / 2
    center_z = (bounds[2][0] + bounds[2][1]) / 2
    return Point3D(center_x, center_y, center_z)