import os
import json
from typing import Optional
import pyglet

from engine.door_node import DoorNode


class DoorsLoader:
    @staticmethod
    def fetch(
        source: str,
        batch: pyglet.graphics.Batch | None = None
    ) -> list[DoorNode]:
        """
        Reads and returns the list of doors from the file provided in [source].
        """

        doors_list: List[DoorNode] = []

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

            location: str = element["location"]
            size: str = element["size"]
            direction: str = element["direction"]

            if "dst_room" in element and "dst_door" in element:
                # Read the destination room data.
                dst_door: list[str] = DoorsLoader.read_dst_door()

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
    def read_dst_door() -> list[str]:
        # TODO
        pass