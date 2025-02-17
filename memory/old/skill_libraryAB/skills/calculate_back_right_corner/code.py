def calculate_back_right_corner(bounds: np.array) -> Point3D:
    """
    Calculate the back-right corner position of the workspace.
    :param bounds: The bounds of the workspace as a numpy array.
    :return: The back-right corner position as a Point3D object.
    """
    x_max = bounds[0][1]
    y_max = bounds[1][1]
    z_min = bounds[2][0]  # Assuming we want to place the block on the ground
    return Point3D(x_max, y_max, z_min)