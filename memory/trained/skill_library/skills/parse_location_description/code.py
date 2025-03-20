from utils.core_types import *


def parse_location_description(location_description: str) -> Point3D:
    """
    Translates a natural language description of a location (e.g., "top-left corner", "left side", "middle",
    "top-right corner", "middle of the back edge") within the workspace into a specific Point3D coordinate.
    Args:
        location_description (str): A natural language description specifying a location in the workspace.
    Returns:
        Point3D: The corresponding 3D point in cartesian coordinates within the specified workspace.
    """
    if location_description == "top-left corner":
        return Point3D(0.25, -0.5, 0.0)
    elif location_description == "left side":
        return Point3D(0.5, -0.5, 0.0)  # Middle of the left side
    elif location_description == "middle":
        return Point3D(0.5, 0.0, 0.0)  # Center of the top surface
    elif location_description == "top-right corner":
        return Point3D(0.25, 0.5, 0.0)
    elif location_description in [
        "back-right corner",
        "top-right corner",
    ]:  # Treat "back" as "top"
        return Point3D(0.25, 0.5, 0.0)  # Top-right corner (formerly "back-right")
    elif location_description == "front-right corner":
        return Point3D(0.75, 0.5, 0.0)
    elif location_description == "front-left corner":
        return Point3D(0.75, -0.5, 0.0)
    elif location_description == "middle of the front edge":
        return Point3D(0.75, 0.0, 0.0)  # Middle of the front edge
    elif location_description == "middle of the back edge":
        return Point3D(0.25, 0.0, 0.0)  # Middle of the back edge
    elif location_description == "back left":
        return Point3D(0.25, -0.5, 0.0)
    elif location_description == "back right":
        return Point3D(0.25, 0.5, 0.0)
    elif location_description == "front middle":
        return Point3D(0.75, 0.0, 0.0)
    elif location_description == "front left":
        return Point3D(0.75, -0.5, 0.0)
    else:
        say(
            f"Location description '{location_description}' not recognized. Defaulting to the center of the workspace."
        )
        return Point3D(0.5, 0.0, 0.0)
