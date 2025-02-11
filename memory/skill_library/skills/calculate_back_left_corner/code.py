def calculate_back_left_corner(bounds: np.array) -> Point3D:
    """
    Calculate the back-left corner position of the workspace.
    :param bounds: The bounds of the workspace as a numpy array.
    :return: The back-left corner position as a Point3D object.
    """
    x_min = bounds[0][0]
    y_min = bounds[1][0]
    z_min = bounds[2][0]  # Assuming we want to place the block on the ground
    return Point3D(x_min, y_min, z_min)