from random import Random


def random_walk(
    map_width: int,
    map_height: int,
    lifespan: int,
    max_reach: int,
    seed: int | float | str | bytes | bytearray | None = None
) -> None:
    """
    Generates a complete dungeon map implementing the random walk algorithm.
    """

    # Make sure the given lifespan is greater than 0.
    assert lifespan > 0
    assert max_reach > 0

    # Create a RNG for later use.
    random: Random = Random()

    # Feed the RNG with the provided seed.
    random.seed(seed)

    # Define a map filled with walls.
    dungeon_map: list[list[int]] = []
    for i in range(map_height):
        row = []
        for j in range(map_width):
            row.append(1)
        dungeon_map.append(row)

    # Pick a random starting location in the map.
    location: tuple[int, int] = (
        random.randint(0, map_width - 1),
        random.randint(0, map_height - 1)
    )

    # Save the picked location as walkable.
    dungeon_map[location[0]][location[1]] = 0

    # print(map, location)

    # Define all possible directions.
    # Directions are defined as west, north, east, south.
    directions: tuple[tuple[int, int]] = (
        (-1, 0),
        (0, 1),
        (1, 0),
        (0, -1),
    )

    # Define a list containing the latest directions taken.
    latest_directions: list[tuple[int, int]] = []

    # Define a starting direction and save it to latest directions.
    direction: tuple[int, int] = random.choice(directions)
    latest_directions.append(tuple(direction))

    # Current walker life.
    life: int = lifespan

    # Loop as long as the walker is alive.
    while life > 0:
        # Fetch the latest direction.
        latest_dir: tuple[int, int] = latest_directions[-1]

        # Pick a new direction that is different from the latest one and its opposite.
        direction = random.choice(list(filter(lambda dir: dir[0] != latest_dir[0] and dir[1] != latest_dir[1], directions)))
        latest_directions.append(tuple(direction))

        # Pick a length within the given max reach.
        reach: int = random.randint(1, max_reach)
        length: int = 0

        # Walk for the defined length in the defined direction.
        while length < reach:
            # Compute the new possible location.
            new_loc: tuple[int, int] = tuple(x + y for x, y in zip(location, direction))

            # Check for edge-of-map collisions.
            if (new_loc[0] < 0 or
                new_loc[0] > map_width - 1 or
                new_loc[1] < 0 or
                new_loc[1] > map_height - 1):
                break

            # Set the newly visited location as walkable.
            location = tuple(new_loc)
            dungeon_map[location[0]][location[1]] = 0
            length += 1

        # Repeat the latest step if a zero-length tunnel was generated.
        if length <= 0:
            latest_directions[-1] = direction
            continue

        life -= 1

    # Return the newly generated map.
    return dungeon_map