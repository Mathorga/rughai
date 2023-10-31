import json
import random
from typing import Dict, List, Optional, Tuple
import pyglet

from engine import controllers
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionRect
from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.utils import set_animation_anchor
from constants import collision_tags

class IdlePropNode(PositionNode):
    """
        Generic idle prop node.
        Takes the path to a json definition file as input.
        The definition file is structured as follows:

        animation_specs[array]: array of all animation definitions. Every element is structured as follows:
            path[string]: a path to the animation file (starting from the application-defined assets directory).
            name[string]: a name used to reference the single animation across the file.
            anchor_x[int](optional): the x component of the animation-specific anchor point.
            anchor_y[int](optional): the y component of the animation-specific anchor point.
        animations[object]: object defining all animations by category. Categories are "idle", "meet_in", "meeting", "meet_out", "interact", "hit" and "destroy". Every element in each category is defined as follows:
            name[string]: the name of the animation name, as defined in animation_specs.
            weight[int]: the selection weight of the specific animation, used during the animation selection algorithm. Probability for a specific animation is calculated as:
                1 / (category_weight_sum - animation_weight)
        anchor_x[int](optional): x component of the global animation anchor point, this is used when no animation-specific anchor point is defined.
        anchor_y[int](optional): y component of the global animation anchor point, this is used when no animation-specific anchor point is defined.
        health_points[int](optional): amount of damage the prop can take before breaking. If this is not set, then an infinite amount is used, aka the prop cannot be broken.
        colliders[array](optional): array of all colliders (responsible for "blocking" collisions). Every element in defined as follows:
            tags[array]: array of all collision tags the single collider reacts to.
            offset_x[int]: horizontal displacement, relative to the prop's position.
            offset_y[int]: vertical displacement, relative to the prop's position.
            width[int]: collider width
            height[int]: collider height
            anchor_x[int]: x component of the collider's anchor point.
            anchor_y[int]: y component of the collider's anchor point.
        sensors[array](optional): array of all sensors (responsible for "non blocking" collisions). Every element in defined as follows:
            tags[array]: array of all collision tags the single sensor reacts to.
            offset_x[int]: horizontal displacement, relative to the prop's position.
            offset_y[int]: vertical displacement, relative to the prop's position.
            width[int]: sensor width
            height[int]: sensor height
            anchor_x[int]: x component of the sensor's anchor point.
            anchor_y[int]: y component of the sensor's anchor point.
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
        self.__animations_data: Dict[str, pyglet.image.animation.Animation] = {}
        self.__animations = {
            "idle": {},
            "meet_in": {},
            "meeting": {},
            "meet_out": {},
            "hit": {},
            "destroy": {}
        }

        self.__colliders: List[PositionNode] = []
        self.__sensors: List[PositionNode] = []

        # Flags.
        self.__in_meet_in = False
        self.__in_meeting = False
        self.__in_meet_out = False

        data: dict = {}
        with open(file = f"{pyglet.resource.path[0]}/{source}", mode = "r", encoding = "UTF-8") as content:
            data = json.load(content)

        # Read health points.
        self.__max_health_points: Optional[int] = None
        self.__health_points = 0
        if "health_points" in data:
            self.__max_health_points = data["health_points"]
            self.__health_points = self.__max_health_points

        # Read global anchor point.
        anchor_x: Optional[int] = None
        anchor_y: Optional[int] = None
        if "anchor_x" in data and "anchor_y" in data:
            anchor_x = data["anchor_x"]
            anchor_y = data["anchor_y"]

        # Load all animations.
        if "animation_specs" in data.keys() and "animations" in data.keys():
            for anim_spec in data["animation_specs"]:
                # Every animation spec should at least include "name" and "path".
                if not "name" in anim_spec and not "path" in anim_spec:
                    continue

                anim_ref = pyglet.resource.animation(anim_spec["path"])
                self.__animations_data[anim_spec["name"]] = anim_ref

                # Read animation-specific anchor point and fall to global if not defined.
                anim_anchor_x: Optional[int] = anim_spec["anchor_x"] if "anchor_x" in anim_spec else anchor_x
                anim_anchor_y: Optional[int] = anim_spec["anchor_y"] if "anchor_y" in anim_spec else anchor_y

                if anim_anchor_x is not None and anim_anchor_y is not None:
                    set_animation_anchor(
                        animation = anim_ref,
                        x = anim_anchor_x,
                        y = anim_anchor_y
                    )

            # Iterate over animation types.
            for anim_key, anim_content in self.__animations.items():
                if anim_key in data["animations"]:
                    # Read animation reference and store it accordingly.
                    for anim_ref in data["animations"][anim_key]:
                        if anim_ref["name"] in self.__animations_data:
                            animation = self.__animations_data[anim_ref["name"]]
                            anim_content[animation] = anim_ref["weight"]

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
                    ],
                    on_triggered = self.__on_collider_triggered
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

        if len(self.__animations["idle"]) > 0:
            # Sprite.
            self.__sprite = SpriteNode(
                resource = list(self.__animations["idle"].keys())[0],
                x = x,
                y = y,
                batch = batch
            )

    def __on_collider_triggered(self, tags: List[str], entered: bool) -> None:
        """
        Handles all colliders' trigger events.
        """

        # Reduce health points if a damage occurred and health points were defined in the first place.
        if entered and collision_tags.DAMAGE in tags and self.__max_health_points is not None:
            self.__health_points -= 1

            if self.__health_points <= 0:
                self.__destroy()
            else:
                self.__hit()

    def __on_sensor_triggered(self, tags: List[str], entered: bool) -> None:
        """
        Handles all sensors' trigger events.
        """

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
        self.__set_animation("idle")

    def __meet_in(self) -> None:
        self.__set_animation("meet_in")

    def __meeting(self) -> None:
        self.__set_animation("meeting")

    def __meet_out(self) -> None:
        self.__set_animation("meet_out")

    def __interact(self) -> None:
        self.__set_animation("interact")

    def __hit(self) -> None:
        self.__set_animation("hit")

    def __destroy(self) -> None:
        self.__set_animation("destroy")

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