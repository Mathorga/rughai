"""
This file contains the class needed to implement a general animation.
"""

import json
from typing import Any, Dict
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
    center_x[bool](optional): whether the animation should be centered on the x axis. If present, this overrides the "anchor_x" parameter.
    center_y[bool](optional): whether the animation should be centered on the y axis. If present, this overrides the "anchor_y" parameter.
    duration[float](optional): the duration of each animation frame.
    loop[bool](optional): whether the animation should loop or not.
    """

    def __init__(
        self,
        source: str,
    ) -> None:
        # Store the source path.
        self.source = source

        # Read source file.
        self.source_data: Dict[str, Any] = {}
        with open(file = f"{pyglet.resource.path[0]}/{source}", mode = "r", encoding = "UTF-8") as content:
            self.source_data = json.load(content)

        # Make sure all mandatory fields are present in the definition file.
        assert "path" in self.source_data.keys() and "name" in self.source_data.keys()

        # Read animation name.
        self.name = self.source_data["name"]

        # Read animation path.
        self.content = pyglet.resource.animation(self.source_data["path"])

        # Set animation anchor if defined.
        if "anchor_x" in self.source_data.keys():
            utils.set_animation_anchor_x(
                animation = self.content,
                anchor = self.source_data["anchor_x"],
            )
        if "anchor_y" in self.source_data.keys():
            utils.set_animation_anchor_y(
                animation = self.content,
                anchor = self.source_data["anchor_y"],
            )

        if "center_x" in self.source_data.keys() and self.source_data["center_x"] is True:
            utils.x_center_animation(animation = self.content)

        if "center_y" in self.source_data.keys() and self.source_data["center_y"] is True:
            utils.y_center_animation(animation = self.content)

        # Set duration if defined.
        if "duration" in self.source_data.keys():
            utils.set_animation_duration(
                animation = self.content,
                duration = self.source_data["duration"]
            )

        # Set not looping if so specified.
        if "loop" in self.source_data.keys() and self.source_data["loop"] is False:
            self.content.frames[-1].duration = None