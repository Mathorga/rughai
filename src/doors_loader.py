import os
import json
from typing import Callable
import pyglet

from constants import collision_tags, events
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
        tile_size: tuple[float, float],
        on_triggered: Callable[[bool, dict], None] | None = None,
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
            # Make sure location, size, direction and destination room are defined for the door.
            assert "location" in element
            assert "size" in element
            assert "direction" in element
            assert "dst_room" in element

            # Make sure either destination location or destination door are defined.
            assert "dst_location" in element or "dst_door" in element

            location_string: str = element["location"]
            location: tuple[float, float] = tuple[float, float](map(lambda element: float(element), tuple(location_string.split(","))))
            size_string: str = element["size"]
            size: tuple[float, float] = tuple[float, float](map(lambda element: float(element), tuple(size_string.split(","))))
            direction: str = element["direction"]
            dst_room: str = element["dst_room"]

            # Make sure a valid direction is defined.
            assert element["direction"] in directions

            dst_location: tuple[float, float] | None = None

            if "dst_door" in element:
                # Read the destination location from destination door.
                dst_location = DoorsLoader.dst_location_from_door(
                    dst_room = dst_room,
                    dst_door = element["dst_door"],
                    direction = direction
                )
            else:
                dst_loc_string: str = element["dst_location"]
                dst_location = tuple[float, float](map(lambda element: float(element), tuple(dst_loc_string.split(","))))

            # Make sure a destination location was found.
            assert dst_location is not None

            print("DST_LOCATION", dst_location)

            # Create a new door node with all data.
            door: DoorNode = DoorNode(
                x = location[0] * tile_size[0],
                y = location[1] * tile_size[1],
                width = int(size[0] * tile_size[0]),
                height = int(size[1] * tile_size[1]),
                tags = [collision_tags.PLAYER_SENSE],
                on_triggered = lambda tags, entered: on_triggered(
                    entered,
                    {
                        "event": events.CHANGE_ROOM,
                        "next_scene": dst_room,
                        "player_position": [
                            dst_location[0] * tile_size[0],
                            dst_location[1] * tile_size[1]
                        ]
                    }
                ) if on_triggered is not None and dst_location is not None else None,
                batch = batch
            )

            # Add the newly created door to the result list.
            doors_list.append(door)

        return doors_list

    @staticmethod
    def dst_location_from_door(dst_room: str, dst_door: str, direction: str) -> tuple[float, float] | None:
        abs_path: str = os.path.join(pyglet.resource.path[0], f"doormaps/{dst_room}.json")

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

        location: tuple[float, float] = tuple[float, float](map(lambda coord: float(coord), tuple(location_string.split(","))))
        size: tuple[float, float] = tuple[float, float](map(lambda coord: float(coord), tuple(size_string.split(","))))

        door_center: tuple[float, float] = (
            location[0] + size[0] / 2.0,
            location[1] + size[1] / 2.0
        )

        # Apply direction.
        result: tuple[float, float] = tuple[float, float](x + y for x, y in zip(door_center, directions[direction]))

        return result