import json
from json.tool import main
import os
import random
from tkinter import W
from turtle import width
from typing import List, Optional, Tuple
import pyglet
from constants import collision_tags

from engine import controllers
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionRect, CollisionShape
from engine.node import PositionNode
from engine.shapes.rect_node import RectNode
from engine.sprite_node import SpriteNode
from engine.utils import animation_set_anchor

class PropNode(PositionNode):
    def __init__(
        self,
        main_idle_anim: pyglet.image.animation.Animation,
        # Proportion between main and secondary animations.
        main_to_sec: float = 0.99,
        # Animation duration.
        anim_duration: float = 1.0,
        sec_idle_anims: List[pyglet.image.animation.Animation] = [],
        x: float = 0,
        y: float = 0,
        z: float = 0,
        collision_shapes: List[CollisionShape] = [],
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        # Make sure at least one idle animation is provided.
        assert len(sec_idle_anims) > 0

        self.main_idle_anim = main_idle_anim
        self.main_to_sec = main_to_sec
        self.__anim_duration = anim_duration
        self.__elapsed_anim_time = 0.0

        self.sec_idle_anims = sec_idle_anims

        # Sprite.
        self.__sprite = SpriteNode(
            resource = main_idle_anim,
            x = x,
            y = y,
            batch = batch
        )

        self.__collider: Optional[CollisionNode] = None
        if len(collision_shapes) > 0:
            # Collider.
            self.__collider = CollisionNode(
                x = x,
                y = y,
                collision_type = CollisionType.STATIC,
                tags = [collision_tags.PLAYER_COLLISION],
                shapes = collision_shapes
            )
            controllers.COLLISION_CONTROLLER.add_collider(self.__collider)

    def set_position(self, position: Tuple[float, float], z: Optional[float] = None):
        super().set_position(position, z)
        self.__sprite.set_position(position, z)

        if self.__collider is not None:
            self.__collider.set_position(position, z)

    def update(self, dt: float) -> None:
        self.__elapsed_anim_time += dt
        if self.__elapsed_anim_time > self.__anim_duration and self.__sprite.get_frame_index() <= 0:
            self.update_animation()
            self.__elapsed_anim_time = 0.0

    def delete(self) -> None:
        self.__sprite.delete()

        if self.__collider is not None:
            self.__collider.delete()

    def update_animation(self):
        if random.random() < self.main_to_sec:
            self.__sprite.set_image(self.main_idle_anim)
        else:
            self.__sprite.set_image(self.sec_idle_anims[random.randint(0, len(self.sec_idle_anims) - 1)])

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
        interact_animations:
        hit_animations:
        anchor_x:
        anchor_y:
        collider:
        sensor:
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
        self.__idle_animations = {}
        self.__meet_in_animations = {}
        self.__meeting_animations = {}
        self.__meet_out_animations = {}

        self.__collider: Optional[CollisionNode] = None

        data: dict
        with open(file = f"{pyglet.resource.path[0]}/{source}", mode = "r", encoding = "UTF-8") as content:
            data = json.load(content)

        # Load all idle animations.
        if "sprites_dir" in data.keys():

            if "idle_animations" in data.keys():
                # Iterate over animation files in the source dir.
                for animation in data["idle_animations"]:
                    anim = pyglet.resource.animation(f"{data['sprites_dir']}/{animation['name']}.gif")
                    self.__idle_animations[anim] = animation["weight"]

            if "meet_in_animations" in data.keys():
                # Iterate over animation files in the source dir.
                for animation in data["meet_in_animations"]:
                    anim = pyglet.resource.animation(f"{data['sprites_dir']}/{animation['name']}.gif")
                    self.__meet_in_animations[anim] = animation["weight"]

            if "meeting_animations" in data.keys():
                # Iterate over animation files in the source dir.
                for animation in data["meeting_animations"]:
                    anim = pyglet.resource.animation(f"{data['sprites_dir']}/{animation['name']}.gif")
                    self.__meeting_animations[anim] = animation["weight"]

            if "meet_out_animations" in data.keys():
                # Iterate over animation files in the source dir.
                for animation in data["meet_out_animations"]:
                    anim = pyglet.resource.animation(f"{data['sprites_dir']}/{animation['name']}.gif")
                    self.__meet_out_animations[anim] = animation["weight"]

        if "anchor_x" in data.keys() and "anchor_y" in data.keys():
            anchor_x = data["anchor_x"]
            anchor_y = data["anchor_y"]

            # Apply anchor to all animations.
            for anim in list(self.__idle_animations.keys()) + list(self.__meet_in_animations.keys()) + list(self.__meeting_animations.keys()) + list(self.__meet_out_animations.keys()):
                animation_set_anchor(
                    animation = anim,
                    x = anchor_x,
                    y = anchor_y
                )

        if "collider" in data.keys():
            # Collider.
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

        self.__sprite: Optional[SpriteNode] = None
        self.__anim_duration = anim_duration
        self.__elapsed_anim_time = 0.0

        if len(self.__idle_animations) > 0:
            # Sprite.
            self.__sprite = SpriteNode(
                resource = list(self.__idle_animations.keys())[0],
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

    def update(self, dt: float) -> None:
        self.__elapsed_anim_time += dt
        if self.__elapsed_anim_time > self.__anim_duration and self.__sprite.get_frame_index() <= 0:
            self.update_animation()
            self.__elapsed_anim_time = 0.0

    def delete(self) -> None:
        if self.__sprite is not None:
            self.__sprite.delete()

        if self.__collider is not None:
            self.__collider.delete()

    def update_animation(self):
        if self.__sprite is not None and len(self.__idle_animations) > 0:
            self.__sprite.set_image(random.choices(list(self.__idle_animations.keys()), list(self.__idle_animations.values()))[0])