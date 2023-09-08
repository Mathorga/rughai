import json
import random
from typing import Optional, Tuple
import pyglet

from engine import controllers
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionRect
from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.utils import animation_set_anchor

class IdlePropNode(PositionNode):
    """
        Generic idle prop node.
        Takes the path to a json definition file as input.
        The definition file is structured as follows:

        sprites_dir: directory containing all the prop's sprites, relative to the pyglet resources dir.
        idle_animations: array of all idle animation files. The first one is used as main, while all the othes as secondary.
        intersect_animations: array of all intersect animation files.
        meet_in_animations: array of all entering animation files. One of these is played randomly when a triggering enter intersection happens.
        meeting_animations: array of all during-meet animation files. One of these is played randomly during a triggering intersection, after meet_in and before meet_out.
        meet_out_animations: array of all exiting animation files. One of these is played randomly when a triggering exit intersection happens.
        interact_animations: array of all interacting animation files. One of these is played randomly when a triggering interaction happens.
        hit_animations: array of all hit animation files. One of these is played randomly when a hit happens.
        anchor_x: x axis anchor for all animations.
        anchor_y: y axis anchor for all animations.
        collider: collider details. The collider defined here is responsible for actual (blocking) collisions.
        sensor: sensor details. The collider defined here is responsible for all non-blocking collisions (interactions and meeting).
    }
    """

    def __init__(
        self,
        source: str,
        # Animation duration.
        anim_duration: float = 1.0,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        self.__source = source
        self.__animations = {
            "idle_animations": {},
            "meet_in_animations": {},
            "meeting_animations": {},
            "meet_out_animations": {},
            "hit_animations": {}
        }

        self.__collider: Optional[CollisionNode] = None
        self.__sensor: Optional[CollisionNode] = None

        # Flags.
        self.__meeting = False

        data: dict
        with open(file = f"{pyglet.resource.path[0]}/{source}", mode = "r", encoding = "UTF-8") as content:
            data = json.load(content)

        # Load all animations.
        if "sprites_dir" in data.keys():
            # Iterate over animation types.
            for anim_key in self.__animations:
                if anim_key in data:
                    # Iterate over animation files in the source dir.
                    for animation in data[anim_key]:
                        anim = pyglet.resource.animation(f"{data['sprites_dir']}/{animation['name']}.gif")
                        self.__animations[anim_key][anim] = animation["weight"]

        if "anchor_x" in data and "anchor_y" in data:
            anchor_x = data["anchor_x"]
            anchor_y = data["anchor_y"]

            # Apply anchor to all animations.
            for anim_key, animations in self.__animations.items():
                for anim in animations:
                    animation_set_anchor(
                        animation = anim,
                        x = anchor_x,
                        y = anchor_y
                    )

        # Collider.
        if "collider" in data:
            self.__collider = CollisionNode(
                x = x,
                y = y,
                collision_type = CollisionType.STATIC,
                tags = data["collider"]["tags"],
                shapes = [
                    CollisionRect(
                        x = x + data["collider"]["offset_x"],
                        y = y + data["collider"]["offset_y"],
                        width = data["collider"]["width"],
                        height = data["collider"]["height"],
                        anchor_x = data["collider"]["anchor_x"],
                        anchor_y = data["collider"]["anchor_y"],
                        batch = batch
                    )
                ]
            )
            controllers.COLLISION_CONTROLLER.add_collider(self.__collider)

        # Sensor.
        if "sensor" in data:
            self.__sensor = CollisionNode(
                x = x,
                y = y,
                collision_type = CollisionType.STATIC,
                tags = data["sensor"]["tags"],
                sensor = True,
                shapes = [
                    CollisionRect(
                        x = x + data["sensor"]["offset_x"],
                        y = y + data["sensor"]["offset_y"],
                        width = data["sensor"]["width"],
                        height = data["sensor"]["height"],
                        anchor_x = data["sensor"]["anchor_x"],
                        anchor_y = data["sensor"]["anchor_y"],
                        batch = batch
                    )
                ]
            )
            controllers.COLLISION_CONTROLLER.add_collider(self.__sensor)

        self.__sprite: Optional[SpriteNode] = None
        self.__anim_duration = anim_duration
        self.__elapsed_anim_time = 0.0

        if len(self.__animations["idle_animations"]) > 0:
            # Sprite.
            self.__sprite = SpriteNode(
                resource = list(self.__animations["idle_animations"].keys())[0],
                x = x,
                y = y,
                batch = batch
            )

    def set_position(self, position: Tuple[float, float], z: Optional[float] = None):
        super().set_position(position, z)

        if self.__sprite is not None:
            self.__sprite.set_position(position, z)

        if self.__collider is not None:
            self.__collider.set_position(position, z)

        if self.__sensor is not None:
            self.__sensor.set_position(position, z)

    def update(self, dt: float) -> None:
        self.__elapsed_anim_time += dt
        if self.__sprite is not None:
            if self.__elapsed_anim_time > self.__anim_duration and self.__sprite.get_frame_index() <= 0:
                self.update_animation()
                self.__elapsed_anim_time = 0.0

    def delete(self) -> None:
        if self.__sprite is not None:
            self.__sprite.delete()

        if self.__collider is not None:
            self.__collider.delete()

        if self.__sensor is not None:
            self.__sensor.delete()

    def update_animation(self):
        if self.__sprite is not None and len(self.__animations["idle_animations"]) > 0:
            self.__sprite.set_image(random.choices(list(self.__animations["idle_animations"].keys()), list(self.__animations["idle_animations"].values()))[0])