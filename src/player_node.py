"""
Module containing the main player's classes.
"""

from enum import Enum
import math
from typing import Dict, Optional

import pyglet
import pyglet.math as pm
from aim_node import AimNode

from constants import collision_tags
from engine.animation import Animation

from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionRect
from engine.node import Node, PositionNode
from engine.sprite_node import SpriteNode
from engine.settings import SETTINGS, Builtins

import engine.controllers as controllers
from engine.state_machine import State, StateMachine
from player_stats import PlayerStats

class PlayerStates(str, Enum):
    IDLE = "idle"
    WALK = "walk"
    RUN = "run"
    ROLL = "roll"
    LOAD = "load"
    AIM = "aim"
    AIM_WALK = "aim_walk"
    DRAW = "draw"
    SHOOT = "shoot"

class PlayerNode(PositionNode):
    """
    Main player class.
    """

    def __init__(
        self,
        cam_target: PositionNode,
        cam_target_offset: tuple = (0.0, 8.0),
        x: float = 0,
        y: float = 0,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        PositionNode.__init__(
            self,
            x = x,
            y = y
        )

        self.__state_machine = StateMachine(
            states = {
                PlayerStates.IDLE: PlayerIdleState(actor = self),
                PlayerStates.WALK: PlayerWalkState(actor = self),
                PlayerStates.RUN: PlayerRunState(actor = self),
                PlayerStates.ROLL: PlayerRollState(actor = self),
                PlayerStates.LOAD: PlayerLoadState(actor = self),
                PlayerStates.AIM: PlayerAimState(actor = self),
                PlayerStates.AIM_WALK: PlayerAimWalkState(actor = self)
            }
        )

        self.interactor_distance = 5.0

        self.run_threshold = 0.75

        self.stats = PlayerStats(
            vitality = 5,
            resistance = 5,
            odds = 5,
            variation = 0.2
        )

        self.__hor_facing: int = 1


        # Animations.
        self.__sprite = SpriteNode(
            resource = Animation(source = "sprites/iryo/iryo_idle.json").content,
            on_animation_end = self.on_sprite_animation_end,
            x = x,
            y = y,
            batch = batch
        )

        # Aim target.
        self.__aim = AimNode(
            x = self.x,
            y = self.y,
            offset_y = 8.0,
            batch = batch
        )

        # Shadow sprite image.
        shadow_image = pyglet.resource.image("sprites/shadow.png")
        shadow_image.anchor_x = shadow_image.width / 2
        shadow_image.anchor_y = shadow_image.height / 2

        self.__shadow_sprite = SpriteNode(
            resource = shadow_image,
            x = x,
            y = y,
            batch = batch
        )

        # Collider.
        self.__collider = CollisionNode(
            x = x,
            y = y,
            collision_type = CollisionType.DYNAMIC,
            tags = [collision_tags.PLAYER_COLLISION],
            shapes = [
                CollisionRect(
                    x = x,
                    y = y,
                    anchor_x = 3,
                    anchor_y = 3,
                    width = 6,
                    height = 6,
                    batch = batch
                )
            ]
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__collider)

        # Interaction finder.
        # This collider is responsible for searching for interactables.
        self.__interactor = CollisionNode(
            x = x,
            y = y,
            sensor = True,
            collision_type = CollisionType.DYNAMIC,
            tags = [collision_tags.PLAYER_INTERACTION],
            shapes = [
                CollisionRect(
                    x = x,
                    y = y,
                    anchor_x = 4,
                    anchor_y = 4,
                    width = 8,
                    height = 8,
                    batch = batch
                )
            ]
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__interactor)

        self.__cam_target_distance = 50.0
        self.__cam_target_distance_mag = 0.0
        self.__cam_target_offset = cam_target_offset
        self.__cam_target = cam_target
        self.__cam_target.x = x + cam_target_offset[0]
        self.__cam_target.y = y + cam_target_offset[1]

    def delete(self) -> None:
        self.__sprite.delete()
        self.__shadow_sprite.delete()
        self.__collider.delete()
        self.__interactor.delete()
        self.__aim.delete()

    def update(self, dt) -> None:
        self.__state_machine.update(dt = dt)

        # Update sprites accordingly.
        self.__update_sprites(dt)

    def on_sprite_animation_end(self):
        self.__state_machine.on_animation_end()

    def disable_controls(self) -> None:
        """
        Disables user controls over the player and stops all existing inputs.
        """

        self.__aim_input = pm.Vec2()
        self.__move_input = pm.Vec2()
        self.__controls_enabled = False

        self.__state_machine.disable_input()

    def enable_controls(self) -> None:
        """
        Enables user controls over the player.
        """

        self.__controls_enabled = True

        self.__state_machine.enable_input()

    def set_animation(self, animation: Animation) -> None:
        self.__sprite.set_image(animation.content)

    def __compute_velocity(self, dt) -> pm.Vec2:
        # Define a vector from speed and direction.
        return pm.Vec2.from_polar(self.stats.speed * dt, self.stats.move_dir)

    def move(self, dt: float) -> None:
        # Apply movement after collision.
        self.set_position(self.__collider.get_position())

        # Compute velocity.
        velocity: pyglet.math.Vec2 = self.__compute_velocity(dt)

        # Apply the computed velocity to all colliders.
        self.__collider.set_velocity((round(velocity.x, 5), round(velocity.y, 5)))
        self.__interactor.set_velocity((round(velocity.x, 5), round(velocity.y, 5)))

    def __update_sprites(self, dt):
        # Only update facing if there's any horizontal movement.
        dir_cos = math.cos(self.stats.look_dir)
        dir_len = abs(dir_cos)
        if dir_len > 0.1:
            self.__hor_facing = int(math.copysign(1.0, dir_cos))

        # Update sprite position.
        self.__sprite.set_position((self.x, self.y))

        # Flip sprite if moving to the left.
        self.__sprite.set_scale(x_scale = self.__hor_facing)

        # Update aim sprite.
        self.__update_aim(dt)

        # Update shadow sprite.
        self.__update_shadow(dt)

        # Update camera target.
        self.__update_cam_target(dt)

        # Update interactor.
        self.__update_interactor(dt)

    def __update_aim(self, dt):
        """
        Updates the aim sign.
        """

        self.__aim.set_direction(direction = self.stats.look_dir)
        self.__aim.set_position(position = self.get_position())
        self.__aim.update(dt = dt)

    def __update_shadow(self, dt):
        self.__shadow_sprite.set_position(
            position = (self.x, self.y),
            # z = 0
            z = -(self.y + (SETTINGS[Builtins.LAYERS_Z_SPACING] * 0.5))
        )
        self.__shadow_sprite.update(dt)

    def set_cam_target_distance_mag(self, mag: float) -> None:
        """
        Sets the magnitude (between 0 and 1) for cam target distance.
        """

        if mag < 0 or mag > 1:
            return

        self.__cam_target_distance_mag = mag

    def __update_cam_target(self, dt: float):
        # Automatically go to cam target distance if loading or aiming.
        cam_target_distance = self.__cam_target_distance * self.__cam_target_distance_mag

        cam_target_vec = pyglet.math.Vec2.from_polar(cam_target_distance, self.stats.look_dir)
        self.__cam_target.x = self.x + self.__cam_target_offset[0] + cam_target_vec.x
        self.__cam_target.y = self.y + self.__cam_target_offset[1] + cam_target_vec.y
        self.__cam_target.update(dt)

    # def set_cam_target_position(self, )

    def __update_interactor(self, dt):
        aim_vec = pyglet.math.Vec2.from_polar(self.interactor_distance, self.stats.look_dir)
        self.__interactor.set_position(
            position = (
                self.x + aim_vec.x,
                self.y + aim_vec.y
            ),
        )

        self.__interactor.update(dt)

    def __update_collider(self, dt):
        self.__collider.update(dt)

    def get_bounding_box(self):
        return self.__sprite.get_bounding_box()

class PlayerState(State):
    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__()

        self.actor: PlayerNode = actor

    def onAnimationEnd(self) -> None:
        pass

class PlayerIdleState(PlayerState):
    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_idle.json")
        self.__move_input: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__aim_input: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__sprint: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_input = controllers.INPUT_CONTROLLER.get_movement()
            self.__aim_input = controllers.INPUT_CONTROLLER.get_aim()
            self.__sprint = controllers.INPUT_CONTROLLER.get_sprint()

    def update(self, dt: float) -> Optional[str]:
        # Read inputs.
        self.__fetch_input()

        # Check for state changes.
        if self.__aim_input.mag > 0.0:
            return PlayerStates.LOAD

        if self.__move_input.mag > 0.0:
            return PlayerStates.WALK

        if self.__sprint:
            return PlayerStates.ROLL

class PlayerWalkState(PlayerState):
    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_walk.json")

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def update(self, dt: float) -> Optional[str]:
        # Read player input.
        move_input: pyglet.math.Vec2 = controllers.INPUT_CONTROLLER.get_movement()

        target_speed: float = 0.0
        if move_input.mag > 0.0:
            # Only set dirs if there's any move input.
            self.actor.stats.move_dir = move_input.heading
            self.actor.stats.look_dir = move_input.heading

            target_speed = self.actor.stats.max_speed
            if controllers.INPUT_CONTROLLER.get_shift():
                target_speed = target_speed / 2

        # Set player stats.
        if self.actor.stats.speed < target_speed:
            self.actor.stats.speed += self.actor.stats.accel * dt
        else:
            self.actor.stats.speed -= self.actor.stats.accel * dt
        self.actor.stats.speed = pm.clamp(self.actor.stats.speed, 0.0, self.actor.stats.max_speed)

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if controllers.INPUT_CONTROLLER.get_aim().mag > 0.0:
            return PlayerStates.LOAD

        if controllers.INPUT_CONTROLLER.get_sprint():
            return PlayerStates.ROLL

        if self.actor.stats.speed <= 0.0:
            return PlayerStates.IDLE

        if self.actor.stats.speed > self.actor.stats.max_speed * self.actor.run_threshold:
            return PlayerStates.RUN

class PlayerRunState(PlayerState):
    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_run.json")

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def update(self, dt: float) -> Optional[str]:
        # Read input.
        move_input: pyglet.math.Vec2 = controllers.INPUT_CONTROLLER.get_movement()

        target_speed: float = 0.0
        if move_input.mag > 0.0:
            # Only set dirs if there's any move input.
            self.actor.stats.move_dir = move_input.heading
            self.actor.stats.look_dir = move_input.heading

            target_speed = self.actor.stats.max_speed
            if controllers.INPUT_CONTROLLER.get_shift():
                target_speed = target_speed / 2

        # Set player stats.
        if self.actor.stats.speed < target_speed:
            self.actor.stats.speed += self.actor.stats.accel * dt
        else:
            self.actor.stats.speed -= self.actor.stats.accel * dt
        self.actor.stats.speed = pm.clamp(self.actor.stats.speed, 0.0, self.actor.stats.max_speed)

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if controllers.INPUT_CONTROLLER.get_aim().mag > 0.0:
            return PlayerStates.LOAD

        if controllers.INPUT_CONTROLLER.get_sprint():
            return PlayerStates.ROLL

        if self.actor.stats.speed <= self.actor.stats.max_speed * self.actor.run_threshold:
            return PlayerStates.WALK

class PlayerRollState(PlayerState):
    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_roll.json")
        self.__startup: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.__startup = True

    def update(self, dt: float) -> Optional[str]:
        if self.__startup:
            self.actor.stats.speed = self.actor.stats.max_speed * 2
            self.__startup = False
        else:
            self.actor.stats.speed -= (self.actor.stats.accel / 2) * dt

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if self.actor.stats.speed <= 0.0:
            return PlayerStates.IDLE

    def on_animation_end(self) -> Optional[str]:
        if self.actor.stats.speed <= 0.0:
            return PlayerStates.IDLE
        else:
            return PlayerStates.WALK

class PlayerLoadState(PlayerState):
    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_atk_load.json")

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def update(self, dt: float) -> str | None:
        # Read input.
        aim_input: pyglet.math.Vec2 = controllers.INPUT_CONTROLLER.get_aim()

        # Set aim direction.
        self.actor.stats.look_dir = aim_input.heading

    def on_animation_end(self) -> str | None:
        return PlayerStates.AIM

class PlayerAimState(PlayerState):
    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_atk_hold_0.json")

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def update(self, dt: float) -> Optional[str]:
        # Read input.
        aim_input: pyglet.math.Vec2 = controllers.INPUT_CONTROLLER.get_aim()

        self.actor.set_cam_target_distance_mag(mag = aim_input.mag)

        # Set aim direction.
        self.actor.stats.look_dir = aim_input.heading

        # Check for state changes.
        if controllers.INPUT_CONTROLLER.get_movement().mag > 0.0:
            return PlayerStates.AIM_WALK

        if controllers.INPUT_CONTROLLER.get_aim().mag <= 0.0:
            return PlayerStates.IDLE

    def end(self) -> None:
        # self.actor.set_cam_target_distance_mag(mag = 0.0)
        pass

class PlayerAimWalkState(PlayerState):
    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_atk_hold_0_walk.json")

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def update(self, dt: float) -> Optional[str]:
        # Read input.
        aim_input: pyglet.math.Vec2 = controllers.INPUT_CONTROLLER.get_aim()
        move_input: pyglet.math.Vec2 = controllers.INPUT_CONTROLLER.get_movement()

        self.actor.set_cam_target_distance_mag(mag = aim_input.mag)

        # Set aim direction.
        self.actor.stats.look_dir = aim_input.heading
        self.actor.stats.move_dir = move_input.heading

        target_speed: float = self.actor.stats.max_speed / 2

        # Set player stats.
        if self.actor.stats.speed < target_speed:
            self.actor.stats.speed += self.actor.stats.accel * dt
        else:
            self.actor.stats.speed -= self.actor.stats.accel * dt
        self.actor.stats.speed = pm.clamp(self.actor.stats.speed, 0.0, self.actor.stats.max_speed)

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if move_input.mag <= 0:
            return PlayerStates.AIM

        if controllers.INPUT_CONTROLLER.get_movement().mag > 0.0:
            return PlayerStates.AIM_WALK

        if controllers.INPUT_CONTROLLER.get_aim().mag <= 0.0:
            return PlayerStates.IDLE