import os
import json
import pyglet

from engine.fall_node import FallNode


class FallsLoader:
    @staticmethod
    def fetch(
        source: str,
        batch: pyglet.graphics.Batch | None = None
    ) -> list[FallNode]:
        """
        Reads and returns the list of falls from the file provided in [source].
        """

        falls_list: list[FallNode] = []

        abs_path: str = os.path.join(pyglet.resource.path[0], source)

        # Return an empty list if the source file is not found.
        if not os.path.exists(abs_path):
            return []

        print(f"Loading falls {abs_path}")

        data: dict

        # Load the json file.
        with open(file = abs_path, mode = "r", encoding = "UTF8") as source_file:
            data = json.load(source_file)

        # Just return if no data is read.
        if len(data) <= 0:
            return []

        # Loop through defined fall types.
        for element in data["elements"]:
            positions: list[str] = element["positions"]
            sizes: list[str] = element["sizes"]

            assert len(positions) == len(sizes)

            # Loop through single falls.
            for i in range(len(positions)):
                position_string: str = positions[i]
                size_string: str = sizes[i]

                position: list[float] = list(map(lambda item: float(item), position_string.split(",")))
                size: list[float] = list(map(lambda item: float(item), size_string.split(",")))

                assert len(position) == 2 and len(size) == 2

                # Create a new fall node and add it to the result.
                falls_list.append(FallNode(
                    x = position[0],
                    y = position[1],
                    width = int(size[0]),
                    height = int(size[1]),
                    tags = element["tags"],
                    batch = batch
                ))

        return falls_list

    @staticmethod
    def store(
        dest: str,
        falls: list[FallNode]
    ) -> None:
        """
        Saves a fallmap file to store all provided falls.
        Falls are internally sorted by tags.
        """

        # Group falls by tags.
        falls_data: dict[str, list[FallNode]] = {}
        for fall in falls:
            key: str = ",".join(fall.tags)
            if not key in falls_data:
                falls_data[key] = [fall]
            else:
                falls_data[key].append(fall)

        # Prepare falls data for storage.
        result: list[dict[str, list[str]]] = []
        for key, value in falls_data.items():
            element: dict[str, list[str]] = {
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