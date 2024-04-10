import os
import json
import pyglet

from engine.door_node import DoorNode

directions: dict[str, tuple[float, float]] = {
    "north": (0.0, 1.0),
    "south": (0.0, -1.0),
    "east": (1.0, 0.0),
    "west": (-1.0, 0.0)
}

class DoorsLoader:
    @staticmethod
    def fetch(
        source: str,
        batch: pyglet.graphics.Batch | None = None
    ) -> list[DoorNode]:
        """
        Reads and returns the list of doors from the file provided in [source].
        """

        doors_list: list[DoorNode] = []

        abs_path: str = os.path.join(pyglet.resource.path[0], source)

        # Return an empty list if the source file is not found.
        if not os.path.exists(abs_path):
            return []

        print(f"Loading doors {abs_path}")

        data: dict

        # Load the json file.
        with open(file = abs_path, mode = "r", encoding = "UTF8") as source_file:
            data = json.load(source_file)

        # Just return if no data is read.
        if len(data) <= 0:
            return []

        # Loop through defined wall types.
        for element in data["elements"]:
            # Make sure location, size and direction are defined for the door.
            assert "location" in element
            assert "size" in element
            assert "direction" in element

            # Make sure either destination location or destination door are defined.
            assert "dst_location" in element or ("dst_room" in element and "dst_door" in element)

            location: str = element["location"]
            size: str = element["size"]
            direction: str = element["direction"]

            # Make sure a valid direction is defined.
            assert element["direction"] in directions

            dst_location: tuple[float, float] | None

            if "dst_room" in element and "dst_door" in element:
                # Read the destination door data.
                dst_location = DoorsLoader.read_dst_door_location(
                    dst_room = element["dst_room"],
                    dst_door = element["dst_door"],
                    direction = element["direction"]
                )
            else:
                dst_loc_string: str = element["dst_location"]
                dst_location = map(lambda coord: float(coord), tuple(dst_loc_string.split(",")))

            # Make sure a destination location was found.
            assert dst_location is not None

            # # Loop through single walls.
            # for i in range(len(positions)):
            #     position_string: str = positions[i]
            #     size_string: str = sizes[i]

            #     position: List[float] = list(map(lambda item: float(item), position_string.split(",")))
            #     size: List[float] = list(map(lambda item: float(item), size_string.split(",")))

            #     assert len(position) == 2 and len(size) == 2

            #     # Create a new wall node and add it to the result.
            #     doors_list.append(WallNode(
            #         x = position[0],
            #         y = position[1],
            #         width = size[0],
            #         height = size[1],
            #         tags = element["tags"],
            #         batch = batch
            #     ))

        return doors_list

    @staticmethod
    def read_dst_door_location(dst_room: str, dst_door: str, direction: str) -> tuple[float, float] | None:
        abs_path: str = os.path.join(pyglet.resource.path[0], f"doormaps/{str}.json")

        # Return None if the source file is not found.
        if not os.path.exists(abs_path):
            return None

        data: dict

        with open(file = abs_path, mode = "r", encoding = "UTF8") as source_file:
            data = json.load(source_file)

        # Just return if no data is read.
        if len(data) <= 0:
            return None

        # Search for the desired door in the room.
        dst_door_data: dict | None = next(filter(lambda element: element["id"] == dst_door, data["elements"]), None)
        if dst_door_data is None:
            return None

        if not "location" in dst_door_data:
            return None

        if not "size" in dst_door_data:
            return None

        # Compute destination door center.
        location_string: str = dst_door_data["location"]
        size_string: str = dst_door_data["size"]

        location: tuple[float, float] = map(lambda coord: float(coord), tuple(location_string.split(",")))
        size: tuple[float, float] = map(lambda coord: float(coord), tuple(size_string.split(",")))

        door_center: tuple[float, float] = (
            location[0] + size[0] / 2.0,
            location[1] + size[1] / 2.0
        )

        # Apply direction.
        result: tuple[float, float] = tuple(x + y for x, y in zip(door_center, directions[direction]))

        return result