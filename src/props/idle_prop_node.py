import os
from enum import Enum
import json
import random
import pyglet

from amonite import controllers
from amonite.collision.collision_node import CollisionNode, CollisionType
from amonite.collision.collision_shape import CollisionRect
from amonite.interaction_node import InteractionNode
from amonite.settings import SETTINGS, Keys
from amonite.sprite_node import SpriteNode
from amonite.state_machine import State, StateMachine
from amonite.utils.utils import set_animation_anchor_x, set_animation_anchor_y, x_center_animation, y_center_animation
from constants import uniques
from props.prop_node import PropNode

class IdlePropStates(str, Enum):
    IDLE = "idle"
    MEET_IN = "meet_in"
    MEETING = "meeting"
    MEET_OUT = "meet_out"
    INTERACT = "interact"
    HIT = "hit"
    DESTROY = "destroy"
    DESTROYED = "destroyed"

class IdlePropNode(PropNode):
    """
        Generic idle prop node.
        Takes the path to a json definition file as input.
        The definition file is structured as follows:

        animation_specs[array]: array of all animation definitions. Every element is structured as follows:
            path[string]: a path to the animation file (starting from the application-defined assets directory).
            name[string]: a name used to reference the single animation across the file.
            center_x[bool](optional): whether the animation should be centered on its x-axis.
            center_y[bool](optional): whether the animation should be centered on its y-axis.
            anchor_x[int](optional): the x component of the animation-specific anchor point. This is ignored if "center_x" is true.
            anchor_y[int](optional): the y component of the animation-specific anchor point. This is ignored if "center_y" is true.
            loop[bool](optional): whether the animation should loop or not. Defaults to true. This is useful when a non looping state should stick for a long time (e.g. destroyed or destroy when no destroy is provided).
        animations[object]: object defining all animations by category. Categories are "idle", "meet_in", "meeting", "meet_out", "interact", "hit", "destroy" and "destroyed". Every element in each category is defined as follows:
            name[string]: the name of the animation name, as defined in animation_specs.
            weight[int]: the selection weight of the specific animation, used during the animation selection algorithm. Probability for a specific animation is calculated as animation_weight / category_weight_sum
        anchor_x[int](optional): x component of the global animation anchor point, this is used when no animation-specific anchor point is defined.
        anchor_y[int](optional): y component of the global animation anchor point, this is used when no animation-specific anchor point is defined.
        layer[string][optional]: layer in which to place the prop. Possible options are "dig", "rat" and "pid", which respectively place the prop below, in or above the player movement layer. Defaults to "rat".
        health_points[int](optional): amount of damage the prop can take before breaking. If this is not set, then an infinite amount is used, aka the prop cannot be broken.
        colliders[array](optional): array of all colliders (responsible for "blocking" collisions). Every element in defined as follows:
            tags[array]: array of all collision tags causing blocking collisions.
            offset_x[int]: horizontal displacement, relative to the prop's position.
            offset_y[int]: vertical displacement, relative to the prop's position.
            width[int]: collider width
            height[int]: collider height
            anchor_x[int]: x component of the collider's anchor point.
            anchor_y[int]: y component of the collider's anchor point.
        sensors[array](optional): array of all sensors (responsible for "non blocking" collisions). Every element in defined as follows:
            meet_tags[array]: array of all collision tags causing meeting.
            interact_tags[array]: array of all collision tags causing interaction.
            hit_tags[array]: array of all collision tags causing hit.
            offset_x[int]: horizontal displacement, relative to the prop's position.
            offset_y[int]: vertical displacement, relative to the prop's position.
            width[int]: sensor width
            height[int]: sensor height
            anchor_x[int]: x component of the sensor's anchor point.
            anchor_y[int]: y component of the sensor's anchor point.
    }
    """

    __slots__ = (
        "source",

        # Animation data.
        "__animations_data",
        "animations",

        "__interactor",
        "__colliders",
        "__sensors",
        "__sensors_tags",

        "max_health_points",
        "health_points",

        "sprite",
        "anim_duration",

        "__state_machine"
    )

    def __init__(
        self,
        source: str,
        # Animation duration.
        anim_duration: float = 1.0,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        # Read id from source.
        id: str = os.path.basename(source).split(".")[0]
        super().__init__(
            id = id,
            x = x,
            y = y,
            world_batch = batch
        )

        self.source = source
        self.__animations_data: dict[str, pyglet.image.animation.Animation] = {}
        self.animations = {
            "idle": {},
            "meet_in": {},
            "meeting": {},
            "meet_out": {},
            "interact": {},
            "hit": {},
            "destroy": {},
            "destroyed": {}
        }

        self.__interactor: InteractionNode | None = None
        self.__colliders: list[CollisionNode] = []
        self.__sensors: list[CollisionNode] = []
        self.__sensors_tags: list[dict[str, list[str]]] = []

        data: dict = {}
        with open(file = f"{pyglet.resource.path[0]}/{source}", mode = "r", encoding = "UTF-8") as content:
            data = json.load(content)

        # Read health points.
        self.max_health_points: int | None = None
        self.health_points = 0
        if "health_points" in data:
            self.max_health_points = data["health_points"]
            self.health_points = self.max_health_points

        # Read global anchor point.
        anchor_x: int | None = None
        anchor_y: int | None = None
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
                anim_anchor_x: int | None = anim_spec["anchor_x"] if "anchor_x" in anim_spec else anchor_x
                anim_anchor_y: int | None = anim_spec["anchor_y"] if "anchor_y" in anim_spec else anchor_y

                # Read animation centering.
                center_x: bool = anim_spec["center_x"] if "center_x" in anim_spec else False
                center_y: bool = anim_spec["center_y"] if "center_y" in anim_spec else False

                # Set x anchor.
                if center_x:
                    x_center_animation(animation = anim_ref)
                elif anim_anchor_x is not None:
                    set_animation_anchor_x(animation = anim_ref, anchor = anim_anchor_x)

                # Set y anchor.
                if center_y:
                    y_center_animation(animation = anim_ref)
                elif anim_anchor_y is not None:
                    set_animation_anchor_y(animation = anim_ref, anchor = anim_anchor_y)

                # Set not looping if so specified.
                if "loop" in anim_spec and anim_spec["loop"] is False:
                    anim_ref.frames[-1].duration = None

            # Iterate over animation types.
            for anim_key, anim_content in self.animations.items():
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
                    passive_tags = collider_data["tags"],
                    shape = CollisionRect(
                        x = x + collider_data["offset_x"],
                        y = y + collider_data["offset_y"],
                        width = collider_data["width"],
                        height = collider_data["height"],
                        anchor_x = collider_data["anchor_x"],
                        anchor_y = collider_data["anchor_y"],
                        batch = batch
                    ),
                    on_triggered = self.__on_collider_triggered
                )
                self.__colliders.append(collider)
                controllers.COLLISION_CONTROLLER.add_collider(collider)

        # Sensors.
        if "sensors" in data:
            # Create interactor if interact tags are declared.
            if any("interact_tags" in sensor for sensor in data["sensors"]):
                self.__interactor = InteractionNode(
                    on_interaction = self.__on_interaction,
                )
                controllers.INTERACTION_CONTROLLER.add_interaction(self.__interactor)

            for index, sensor_data in enumerate(data["sensors"]):
                meet_tags: list[str] = sensor_data["meet_tags"] or [] if "meet_tags" in sensor_data else []
                interact_tags: list[str] = sensor_data["interact_tags"] or [] if "interact_tags" in sensor_data else []
                hit_tags: list[str] = sensor_data["hit_tags"] or [] if "hit_tags" in sensor_data else []

                sensor = CollisionNode(
                    x = x,
                    y = y,
                    collision_type = CollisionType.STATIC,
                    passive_tags = [
                        *meet_tags,
                        *interact_tags,
                        *hit_tags
                    ],
                    sensor = True,
                    shape = CollisionRect(
                        x = x + sensor_data["offset_x"],
                        y = y + sensor_data["offset_y"],
                        width = sensor_data["width"],
                        height = sensor_data["height"],
                        anchor_x = sensor_data["anchor_x"],
                        anchor_y = sensor_data["anchor_y"],
                        batch = batch
                    ),
                    on_triggered = lambda tags, entered: self.__on_sensor_triggered(tags = tags, entered = entered, index = index)
                )
                self.__sensors_tags.append({})
                self.__sensors_tags[index]["meet"] = meet_tags
                self.__sensors_tags[index]["interact"] = interact_tags
                self.__sensors_tags[index]["hit"] = hit_tags
                self.__sensors.append(sensor)

                controllers.COLLISION_CONTROLLER.add_collider(sensor)

        layer: str = data["layer"] if "layer" in data else "rat"

        self.sprite: SpriteNode | None = None
        self.anim_duration = anim_duration

        if len(self.animations["idle"]) > 0:
            # Sprite.
            self.sprite = SpriteNode(
                resource = list(self.animations["idle"].keys())[0],
                on_animation_end = self.__on_animation_end,
                x = x,
                y = y,
                batch = batch
            )

            # Set z coord according to the provided layer.
            match layer:
                case "dig":
                    self.sprite.sprite.z = -y - SETTINGS[Keys.LAYERS_Z_SPACING] * 0.5
                case "rat":
                    self.sprite.sprite.z = -y
                case "pid":
                    self.sprite.sprite.z = -y + SETTINGS[Keys.LAYERS_Z_SPACING] * 0.5

        # State machine.
        self.__state_machine = IdlePropStateMachine(
            states = {
                IdlePropStates.IDLE: IdlePropIdleState(actor = self),
                IdlePropStates.MEET_IN: IdlePropMeetInState(actor = self),
                IdlePropStates.MEETING: IdlePropMeetingState(actor = self),
                IdlePropStates.MEET_OUT: IdlePropMeetOutState(actor = self),
                IdlePropStates.INTERACT: IdlePropInteractState(actor = self),
                IdlePropStates.HIT: IdlePropHitState(actor = self),
                IdlePropStates.DESTROY: IdlePropDestroyState(actor = self),
                # IdlePropStates.DESTROYED: IdlePropIdleState(actor = self)
            }
        )

    def __on_interaction(self) -> None:
        """
        """

        self.__state_machine.interact()

    def __on_collider_triggered(self, tags: list[str], entered: bool) -> None:
        """
        Handles all colliders' trigger events.
        """

        self.__state_machine.on_collision(tags = tags, enter = entered)

    def __on_sensor_triggered(self, tags: list[str], entered: bool, index: int) -> None:
        """
        Handles all sensors' trigger events.
        """

        if bool(set(tags) & set(self.__sensors_tags[index]["meet"])):
            self.__state_machine.meet(entered = entered)
        elif bool(set(tags) & set(self.__sensors_tags[index]["interact"])):
            if self.__interactor is not None:
                controllers.INTERACTION_CONTROLLER.toggle(self.__interactor, enable = entered)
        elif entered and bool(set(tags) & set(self.__sensors_tags[index]["hit"])):
            self.__state_machine.hit()

    def set_position(self, position: tuple[float, float], z: float | None = None):
        super().set_position(position, z)

        if self.sprite is not None:
            self.sprite.set_position(position, z)

        for collider in self.__colliders:
            collider.set_position(position, z)

        for sensor in self.__sensors:
            sensor.set_position(position, z)

    def update(self, dt: float) -> None:
        self.__state_machine.update(dt = dt)

    def __on_animation_end(self) -> None:
        self.__state_machine.on_animation_end()

    def set_animation(self, key: str) -> None:
        """
        Sets a random animation from the given array key.
        """

        if self.sprite is not None:
            if key in self.animations and len(self.animations[key]) > 0:
                self.sprite.set_image(random.choices(list(self.animations[key].keys()), list(self.animations[key].values()))[0])
            else:
                self.__on_animation_end()

    def delete_colliders(self) -> None:
        """
        Removes and destroys all colliders and sensors.
        """

        for collider in self.__colliders:
            controllers.COLLISION_CONTROLLER.remove_collider(collider = collider)
            collider.delete()
        self.__colliders.clear()

        for sensor in self.__sensors:
            controllers.COLLISION_CONTROLLER.remove_collider(collider = sensor)
            sensor.delete()
        self.__sensors.clear()

    def delete(self) -> None:
        if self.sprite is not None:
            self.sprite.delete()

        # Destroy all colliders and sensors.
        self.delete_colliders()

        # Remove from the current scene.
        if uniques.ACTIVE_SCENE is not None:
            uniques.ACTIVE_SCENE.remove_child(self)

class IdlePropStateMachine(StateMachine):

    def on_collision(self, tags: list[str], enter: bool) -> None:
        return super().on_collision(tags, enter)

    def meet(self, entered: bool) -> None:
        # Just return if there's no current state.
        if self.current_key is None:
            return

        # Retrieve the current state.
        current_state: State = self.states[self.current_key]

        if isinstance(current_state, IdlePropState):
            self.transition(current_state.meet(entered = entered))

    def interact(self) -> None:
        # Just return if there's no current state.
        if self.current_key is None:
            return

        # Retrieve the current state.
        current_state: State = self.states[self.current_key]

        if isinstance(current_state, IdlePropState):
            self.transition(current_state.interact())

    def hit(self) -> None:
        # Just return if there's no current state.
        if self.current_key is None:
            return

        # Retrieve the current state.
        current_state: State = self.states[self.current_key]

        if isinstance(current_state, IdlePropState):
            self.transition(current_state.hit())

class IdlePropState(State):
    def __init__(
        self,
        actor: IdlePropNode
    ) -> None:
        super().__init__()

        self.actor: IdlePropNode = actor

    def meet(self, entered: bool) -> str | None:
        if entered:
            return IdlePropStates.MEET_IN
        else:
            return IdlePropStates.MEET_OUT

    def interact(self) -> str | None:
        return IdlePropStates.INTERACT

    def hit(self) -> str | None:
        # Reduce health points if a damage occurred and health points were defined in the first place.
        if self.actor.max_health_points is not None and self.actor.health_points is not None:
            self.actor.health_points -= 1

            if self.actor.health_points <= 0:
                return IdlePropStates.DESTROY
            else:
                return IdlePropStates.HIT

class IdlePropIdleState(IdlePropState):
    def __init__(self, actor: IdlePropNode) -> None:
        super().__init__(actor)
        self.__elapsed_anim_time: float = 0.0

    def start(self) -> None:
        self.actor.set_animation("idle")

    def update(self, dt: float) -> str | None:
        self.__elapsed_anim_time += dt

        if self.actor.sprite is not None:
            # Fetch current frame index.
            current_frame_index: int = self.actor.sprite.get_frame_index()

            if self.__elapsed_anim_time > self.actor.anim_duration and current_frame_index <= 0:
                self.actor.set_animation("idle")

                self.__elapsed_anim_time = 0.0

class IdlePropMeetInState(IdlePropState):
    def start(self) -> None:
        self.actor.set_animation("meet_in")

    def on_animation_end(self) -> str | None:
        return IdlePropStates.MEETING

class IdlePropMeetingState(IdlePropState):
    def __init__(self, actor: IdlePropNode) -> None:
        super().__init__(actor)
        self.__elapsed_anim_time: float = 0.0

    def start(self) -> None:
        self.actor.set_animation("meeting")

    def update(self, dt: float) -> str | None:
        self.__elapsed_anim_time += dt

        if self.actor.sprite is not None:
            # Fetch current frame index.
            current_frame_index: int = self.actor.sprite.get_frame_index()

            if self.__elapsed_anim_time > self.actor.anim_duration and current_frame_index <= 0:
                self.actor.set_animation("meeting")

                self.__elapsed_anim_time = 0.0

class IdlePropMeetOutState(IdlePropState):
    def start(self) -> None:
        self.actor.set_animation("meet_out")

    def on_animation_end(self) -> str | None:
        return IdlePropStates.IDLE

class IdlePropInteractState(IdlePropState):
    def __init__(self, actor: IdlePropNode) -> None:
        super().__init__(actor)
        self.__animation_ended: bool = False

    def start(self) -> None:
        self.actor.set_animation("interact")

        # Reset animation end state.
        self.__animation_ended = False

    def update(self, dt: float) -> str | None:
        super().update(dt)

        if self.__animation_ended:
            return IdlePropStates.IDLE

    def on_animation_end(self) -> None:
        self.__animation_ended = True

class IdlePropHitState(IdlePropState):
    def start(self) -> None:
        self.actor.set_animation("hit")

    def on_animation_end(self) -> str | None:
        return IdlePropStates.IDLE

class IdlePropDestroyState(IdlePropState):
    def __init__(self, actor: IdlePropNode) -> None:
        super().__init__(actor)
        self.__animation_ended: bool = False

    def start(self) -> None:
        self.actor.set_animation("destroy")

        # Destroy all colliders and sensors.
        self.actor.delete_colliders()

        # Reset animation end state.
        self.__animation_ended = False

    def update(self, dt: float) -> str | None:
        super().update(dt)

        if self.__animation_ended:
            return IdlePropStates.DESTROYED

    def on_animation_end(self) -> None:
        self.__animation_ended = True

class IdlePropDestroyedState(IdlePropState):
    def start(self) -> None:
        self.actor.set_animation("destroyed")