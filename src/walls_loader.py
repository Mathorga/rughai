import os
import json
from typing import Dict, List, Optional, Set
import pyglet

from engine.wall_node import WallNode


class WallsLoader:
    @staticmethod
    def fetch(
        source: str,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> List[WallNode]:
        """
        Reads and returns the list of walls from the file provided in [source].
        """

        walls_list: List[WallNode] = []

        abs_path: str = os.path.join(pyglet.resource.path[0], source)

        # Return an empty list if the source file is not found.
        if not os.path.exists(abs_path):
            return []

        print(f"Loading walls {abs_path}")

        data: dict

        # Load the json file.
        with open(file = abs_path, mode = "r", encoding = "UTF8") as source_file:
            data = json.load(source_file)

        # Just return if no data is read.
        if len(data) <= 0:
            return []

        # Loop through defined wall types.
        for element in data["elements"]:
            positions: List[str] = element["positions"]
            sizes: List[str] = element["sizes"]

            assert len(positions) == len(sizes)

            # Loop through single walls.
            for i in range(len(positions)):
                position_string: str = positions[i]
                size_string: str = sizes[i]

                position: List[float] = list(map(lambda item: float(item), position_string.split(",")))
                size: List[float] = list(map(lambda item: float(item), size_string.split(",")))

                assert len(position) == 2 and len(size) == 2

                # Create a new wall node and add it to the result.
                walls_list.append(WallNode(
                    x = position[0],
                    y = position[1],
                    width = size[0],
                    height = size[1],
                    tags = element["tags"],
                    batch = batch
                ))

        return walls_list

    @staticmethod
    def store(
        dest: str,
        walls: List[WallNode]
    ) -> None:
        """
        Saves a wallmap file to store all provided walls.
        Walls are internally sorted by tags.
        """

        # Group walls by tags.
        walls_data: Dict[str, List[WallNode]] = {}
        for wall in walls:
            key: str = ",".join(wall.tags)
            if not key in walls_data:
                walls_data[key] = [wall]
            else:
                walls_data[key].append(wall)

        # Prepare walls data for storage.
        result: List[Dict[str, List[str]]] = []
        for key, value in walls_data.items():
            element: Dict[str, List[str]] = {
                "tags": key.split(","),
                "positions": list(map(lambda w: f"{w.x},{w.y}", value)),
                "sizes": list(map(lambda w: f"{w.width},{w.height}", value)),
            }
            result.append(element)

        # Write to dest file.
        with open(file = dest, mode = "w", encoding = "UTF8") as dest_file:
            dest_file.write(json.dumps(
                {
                    "elements": result
                },
                indent = 4
            ))