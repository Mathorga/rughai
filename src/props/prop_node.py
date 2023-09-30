import json
import random
from typing import List, Optional, Tuple
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

        self.__colliders: List[PositionNode] = []
        self.__sensors: List[PositionNode] = []

        # Flags.
        # self.__meet_in_requested = False
        # self.__meet_out_requested = False
        self.__in_meet_in = False
        self.__in_meeting = False
        self.__in_meet_out = False

        data: dict
        with open(file = f"{pyglet.resource.path[0]}/{source}", mode = "r", encoding = "UTF-8") as content:
            data = json.load(content)

        # Read global anchor point.
        anchor_x: Optional[int]
        anchor_y: Optional[int]
        if "anchor_x" in data and "anchor_y" in data:
            anchor_x = data["anchor_x"]
            anchor_y = data["anchor_y"]

        # Load all animations.
        if "sprites_dir" in data.keys():
            # Iterate over animation types.
            for anim_key in self.__animations:
                if anim_key in data:
                    # Iterate over animation files in the source dir.
                    for animation in data[anim_key]:
                        anim = pyglet.resource.animation(f"{data['sprites_dir']}/{animation['name']}.gif")

                        # Read animation-specific anchor point and fall to global if not defined.
                        animation_anchor_x: Optional[int] = animation["anchor_x"] if "anchor_x" in animation else anchor_x
                        animation_anchor_y: Optional[int] = animation["anchor_y"] if "anchor_y" in animation else anchor_y

                        if animation_anchor_x is not None and animation_anchor_y is not None:
                            animation_set_anchor(
                                animation = anim,
                                x = animation_anchor_x,
                                y = animation_anchor_y
                            )

                        self.__animations[anim_key][anim] = animation["weight"]

        # Colliders.
        if "colliders" in data:
            for collider_data in data["colliders"]:
                collider = CollisionNode(
                    x = x,
                    y = y,
                    collision_type = CollisionType.STATIC,
                    tags = collider_data["tags"],
                    shapes = [
                        CollisionRect(
                            x = x + collider_data["offset_x"],
                            y = y + collider_data["offset_y"],
                            width = collider_data["width"],
                            height = collider_data["height"],
                            anchor_x = collider_data["anchor_x"],
                            anchor_y = collider_data["anchor_y"],
                            batch = batch
                        )
                    ]
                )
                self.__colliders.append(collider)
                controllers.COLLISION_CONTROLLER.add_collider(collider)

        # Sensors.
        if "sensors" in data:
            for sensor_data in data["sensors"]:
                sensor = CollisionNode(
                    x = x,
                    y = y,
                    collision_type = CollisionType.STATIC,
                    tags = sensor_data["tags"],
                    sensor = True,
                    shapes = [
                        CollisionRect(
                            x = x + sensor_data["offset_x"],
                            y = y + sensor_data["offset_y"],
                            width = sensor_data["width"],
                            height = sensor_data["height"],
                            anchor_x = sensor_data["anchor_x"],
                            anchor_y = sensor_data["anchor_y"],
                            batch = batch
                        )
                    ],
                    on_triggered = self.__on_sensor_triggered
                )
                self.__sensors.append(sensor)
                controllers.COLLISION_CONTROLLER.add_collider(sensor)

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

    def __on_sensor_triggered(self, entered: bool) -> None:
        self.__in_meet_in = entered
        self.__in_meet_out = not entered

    def set_position(self, position: Tuple[float, float], z: Optional[float] = None):
        super().set_position(position, z)

        if self.__sprite is not None:
            self.__sprite.set_position(position, z)

        for collider in self.__colliders:
            collider.set_position(position, z)

        for sensor in self.__sensors:
            sensor.set_position(position, z)

    def update(self, dt: float) -> None:
        self.__elapsed_anim_time += dt
        if self.__sprite is not None:
            # Meet in and out are abrupt transitions: they happen even if the previous animation hasn't finished yet.
            # On the othe  hand, meeting and idle are patient ones, since they wait for the previous one to finish before taking over.

            # First check for abrupt transitions.
            if self.__in_meet_in:
                self.__meet_in()
                self.__in_meeting = True
                self.__in_meet_in = False
            elif self.__in_meet_out:
                self.__meet_out()
                self.__in_meeting = False
                self.__in_meet_out = False
            else:
                # If no abrupt transition took place, then check whether the previous animation finished.
                # If so, then check for patient transitions.
                if self.__elapsed_anim_time > self.__anim_duration and self.__sprite.get_frame_index() <= 0:
                    if self.__in_meeting:
                        self.__meeting()
                    else:
                        self.__idle()

                    self.__elapsed_anim_time = 0.0

    def __idle(self):
        self.__set_animation("idle_animations")

    def __meet_in(self) -> None:
        self.__set_animation("meet_in_animations")

    def __meeting(self) -> None:
        self.__set_animation("meeting_animations")

    def __meet_out(self) -> None:
        self.__set_animation("meet_out_animations")

    def __set_animation(self, key: str) -> None:
        """
        Sets a random animation from the given array key.
        """
        if self.__sprite is not None and key in self.__animations and len(self.__animations[key]) > 0:
            self.__sprite.set_image(random.choices(list(self.__animations[key].keys()), list(self.__animations[key].values()))[0])

    def delete(self) -> None:
        if self.__sprite is not None:
            self.__sprite.delete()

        for collider in self.__colliders:
            collider.delete()
        self.__colliders.clear()

        for sensor in self.__sensors:
            sensor.delete()
        self.__sensors.clear()