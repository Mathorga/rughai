"""
This file contains the class needed to implement a general animation.
"""

import json
import pyglet

from engine import utils

class Animation:
    """
    Generic animation.
    Takes the path to a json definition file as input.
    The definition file is structured as follows:

    name[string]: name of the animation.
    path[string]: path to the animation file (starting from the application-defined assets directory).
    anchor_x[int](optional): the x component of the animation anchor point.
    anchor_y[int](optional): the y component of the animation anchor point.
    """

    def __init__(
        self,
        source: str,
    ) -> None:
        self.__source = source

        # Read source file.
        source_data: dict = {}
        with open(file = f"{pyglet.resource.path[0]}/{source}", mode = "r", encoding = "UTF-8") as content:
            source_data = json.load(content)

        # Make sure all mandatory fields are present in the definition file.
        assert "path" in source_data.keys() and "name" in source_data.keys()

        # Read animation name.
        self.name = source_data["name"]

        # Read animation path.
        self.animation = pyglet.resource.animation(source_data["path"])

        # Set animation anchor if defined.
        if "anchor_x" in source_data.keys() and "anchor_y" in source_data.keys():
            utils.animation_set_anchor(
                animation = self.animation,
                x = source_data["anchor_x"],
                y = source_data["anchor_y"]
            )