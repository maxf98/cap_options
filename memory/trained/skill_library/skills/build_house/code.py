def build_house():
    """Builds a house in the middle of the workspace.
    Assumes all the necessary objects are available in the workspace, and moves them out of the way before building the house.
    """

    objects = get_blocks_by_color()
    base_blocks = get_blocks_by_color("yellow")
    if len(base_blocks) != 14:
        raise Exception("Not enough blocks to build the house")
    roof_base = identify_roof_base(objects)
    if not roof_base:
        raise Exception("Can't find the roof base")
    roof_beam = identify_beam_block(objects)
    if not roof_beam:
        raise Exception("Can't find the roof beam")
    roof_tiles = identify_roof_tiles(objects)
    if not roof_tiles:
        raise Exception("Can't find the roof tiles")

    # Move objects out of the way
    # Move base blocks to back edge of workspace
    back_left = parse_location_description("back left")
    make_line_with_blocks(
        base_blocks, Pose(back_left, Rotation.from_euler("z", np.pi / 2))
    )

    # Move roof tiles to right side of workspace
    back_right = parse_location_description("back right")
    make_line_with_blocks(roof_tiles, Pose(back_right, Rotation.identity()))

    # Move roof beam to front edge of workspace
    front_left = parse_location_description("front left")
    put_first_on_second(
        get_object_pose(roof_beam), Pose(front_left, Rotation.identity())
    )

    # Move roof base to middle of the front edge
    front_middle = parse_location_description("front middle")
    put_first_on_second(
        get_object_pose(roof_base), Pose(front_middle, Rotation.identity())
    )

    # Build the house
    middle = parse_location_description("middle")
    build_house_base(base_blocks, Pose(middle, Rotation.identity()))

    assemble_roof(roof_base, roof_beam, roof_tiles, Pose(middle, Rotation.identity()))
