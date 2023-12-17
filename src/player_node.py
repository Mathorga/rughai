"""
Module containing the main player's classes.
"""

from enum import Enum
import math
from typing import Optional, Tuple

import pyglet
import pyglet.math as pm
from arrow_node import ArrowNode
from engine.loading_indicator_node import LoadingIndicatorNode
from engine.utils import scale
from scope_node import ScopeNode

from constants import collision_tags, scenes
from engine.animation import Animation

from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionRect
from engine.node import PositionNode
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
    DRAW_WALK = "draw_walk"
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

        self.batch = batch

        self.interactor_distance = 5.0

        self.run_threshold = 0.75

        self.stats = PlayerStats(
            vitality = 5,
            resistance = 5,
            odds = 5,
            variation = 0.2
        )

        self.__hor_facing: int = 1

        # Shooting magnitude: defines how strong the shot will be (must be between 0 and 1).
        self.__shoot_mag: float = 0.0

        # Current draw time (in seconds).
        self.draw_time: float = 0.0

        # Animations.
        self.__sprite = SpriteNode(
            resource = Animation(source = "sprites/iryo/iryo_idle.json").content,
            on_animation_end = self.on_sprite_animation_end,
            x = x,
            y = y,
            batch = batch
        )

        # Scope.
        self.scope_offset: Tuple[float, float] = (0.0, 8.0)
        self.__scope = ScopeNode(
            x = self.x,
            y = self.y,
            offset_y = self.scope_offset[1],
            batch = batch
        )

        # Draw loading indicator.
        self.draw_indicator: LoadingIndicatorNode = LoadingIndicatorNode(
            foreground_sprite_res = pyglet.resource.image("sprites/loading_foreground.png"),
            background_sprite_res = pyglet.resource.image("sprites/loading_background.png"),
            x = self.x,
            y = self.y,
            offset_y = 4.0,
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
            active_tags = [
                collision_tags.PLAYER_COLLISION,
                collision_tags.PLAYER_SENSE
            ],
            passive_tags = [
                collision_tags.DAMAGE
            ],
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
            active_tags = [collision_tags.PLAYER_INTERACTION],
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

        # State machine.
        self.__state_machine = PlayerStateMachine(
            states = {
                PlayerStates.IDLE: PlayerIdleState(actor = self),
                PlayerStates.WALK: PlayerWalkState(actor = self),
                PlayerStates.RUN: PlayerRunState(actor = self),
                PlayerStates.ROLL: PlayerRollState(actor = self),
                PlayerStates.LOAD: PlayerLoadState(actor = self),
                PlayerStates.AIM: PlayerAimState(actor = self),
                PlayerStates.AIM_WALK: PlayerAimWalkState(actor = self),
                PlayerStates.DRAW: PlayerDrawState(actor = self),
                PlayerStates.DRAW_WALK: PlayerDrawWalkState(actor = self),
                PlayerStates.SHOOT: PlayerShootState(actor = self)
            }
        )

    def delete(self) -> None:
        self.__sprite.delete()
        self.__shadow_sprite.delete()
        self.__collider.delete()
        self.__interactor.delete()
        self.__scope.delete()
        self.draw_indicator.delete()

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

        self.__state_machine.disable_input()

    def enable_controls(self) -> None:
        """
        Enables user controls over the player.
        """

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

        # Update scope.
        self.__update_scope(dt)

        # Update shadow sprite.
        self.__update_shadow(dt)

        self.__update_draw_indicator(dt)

        # Update camera target.
        self.__update_cam_target(dt)

        # Update interactor.
        self.__update_interactor(dt)

    def __update_scope(self, dt):
        """
        Updates the scope sign.
        """

        self.__scope.set_direction(direction = self.stats.look_dir)
        self.__scope.set_position(position = self.get_position())
        self.__scope.update(dt = dt)

    def __update_shadow(self, dt):
        self.__shadow_sprite.set_position(
            position = (self.x, self.y),
            # z = 0
            z = -(self.y + (SETTINGS[Builtins.LAYERS_Z_SPACING] * 0.5))
        )
        self.__shadow_sprite.update(dt)

    def __update_draw_indicator(self, dt):
        """
        Updates the draw indicator.
        """

        draw_indicator_value: float = pm.clamp(
            num = self.draw_time,
            min_val = 0.0,
            max_val = self.stats.min_draw_time
        )
        self.draw_indicator.set_value(value = draw_indicator_value / self.stats.min_draw_time)
        self.draw_indicator.set_position(position = self.get_position())
        self.draw_indicator.update(dt = dt)

    def set_cam_target_distance_mag(self, mag: float) -> None:
        """
        Sets the magnitude (between 0 and 1) for cam target distance.
        """

        assert mag >= 0.0 and mag <= 1.0, "Value out of range"

        self.__cam_target_distance_mag = mag

    def __update_cam_target(self, dt: float):
        # Automatically go to cam target distance if loading or aiming.
        cam_target_distance: float = self.__cam_target_distance * self.__cam_target_distance_mag

        cam_target_vec: pyglet.math.Vec2 = pyglet.math.Vec2.from_polar(cam_target_distance, self.stats.look_dir)
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

    def load_scope(self) -> None:
        self.__scope.load()

    def unload_scope(self) -> None:
        self.__scope.unload()

    def get_shoot_mag(self) -> float:
        return self.__shoot_mag

    def set_shoot_mag(self, mag: float) -> None:
        if mag >= 0.0 and mag <= 1.0:
            self.__shoot_mag = mag

    def __update_collider(self, dt):
        self.__collider.update(dt)

    def get_bounding_box(self):
        return self.__sprite.get_bounding_box()

class PlayerStateMachine(StateMachine):
    def enable_input(self) -> None:
        # Just return if there's no current state.
        if self.current_key is None:
            return

        # Retrieve the current state.
        current_state: State = self.states[self.current_key]

        if isinstance(current_state, PlayerState):
            current_state.enable_input()

    def disable_input(self) -> None:
        # Just return if there's no current state.
        if self.current_key is None:
            return

        # Retrieve the current state.
        current_state: State = self.states[self.current_key]

        if isinstance(current_state, PlayerState):
            current_state.disable_input()

class PlayerState(State):
    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__()

        self.input_enabled: bool = True
        self.actor: PlayerNode = actor

    def onAnimationEnd(self) -> None:
        pass

    def enable_input(self) -> None:
        self.input_enabled = True

    def disable_input(self) -> None:
        self.input_enabled = False

class PlayerIdleState(PlayerState):
    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_idle.json")

        # Input.
        self.__move: bool = False
        self.__aim: bool = False
        self.__sprint: bool = False
        self.__interact: bool = False

    def start(self) -> None:
        self.actor.draw_time = 0.0
        self.actor.set_animation(self.__animation)
        self.actor.unload_scope()

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move = controllers.INPUT_CONTROLLER.get_movement()
            self.__aim = controllers.INPUT_CONTROLLER.get_aim()
            self.__sprint = controllers.INPUT_CONTROLLER.get_sprint()
            self.__interact = controllers.INPUT_CONTROLLER.get_interaction()

    def update(self, dt: float) -> Optional[str]:
        # Read inputs.
        self.__fetch_input()

        # Interaction.
        if self.__interact:
            controllers.INTERACTION_CONTROLLER.interact()

        # Check for state changes.
        if self.__aim:
            return PlayerStates.LOAD

        if self.__move:
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

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__aim: bool = False
        self.__shift: bool = False
        self.__sprint: bool = False
        self.__interact: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = controllers.INPUT_CONTROLLER.get_movement_vec()
            self.__aim = controllers.INPUT_CONTROLLER.get_aim()
            self.__shift = controllers.INPUT_CONTROLLER.get_shift()
            self.__sprint = controllers.INPUT_CONTROLLER.get_sprint()
            self.__interact = controllers.INPUT_CONTROLLER.get_interaction()

    def update(self, dt: float) -> Optional[str]:
        # Read inputs.
        self.__fetch_input()

        # Interaction.
        if self.__interact:
            controllers.INTERACTION_CONTROLLER.interact()

        target_speed: float = 0.0
        if self.__move_vec.mag > 0.0:
            # Only set dirs if there's any move input.
            self.actor.stats.move_dir = self.__move_vec.heading
            self.actor.stats.look_dir = self.__move_vec.heading

            target_speed = self.actor.stats.max_speed
            if self.__shift:
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
        if self.__aim:
            return PlayerStates.LOAD

        if self.__sprint:
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

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__aim: bool = False
        self.__shift: bool = False
        self.__sprint: bool = False
        self.__interact: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = controllers.INPUT_CONTROLLER.get_movement_vec()
            self.__aim = controllers.INPUT_CONTROLLER.get_aim()
            self.__shift = controllers.INPUT_CONTROLLER.get_shift()
            self.__sprint = controllers.INPUT_CONTROLLER.get_sprint()
            self.__interact = controllers.INPUT_CONTROLLER.get_interaction()

    def update(self, dt: float) -> Optional[str]:
        # Read inputs.
        self.__fetch_input()

        # Interaction.
        if self.__interact:
            controllers.INTERACTION_CONTROLLER.interact()

        target_speed: float = 0.0
        if self.__move_vec.mag > 0.0:
            # Only set dirs if there's any move input.
            self.actor.stats.move_dir = self.__move_vec.heading
            self.actor.stats.look_dir = self.__move_vec.heading

            target_speed = self.actor.stats.max_speed
            if self.__shift:
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
        if self.__aim:
            return PlayerStates.LOAD

        if self.__sprint:
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

        # Read input.
        aim_vec: pyglet.math.Vec2 = controllers.INPUT_CONTROLLER.get_aim_vec()

        # Set aim direction.
        self.actor.stats.look_dir = aim_vec.heading

    def on_animation_end(self) -> Optional[str]:
        return PlayerStates.AIM

class PlayerAimState(PlayerState):
    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_atk_hold_0.json")

        # Input.
        self.__move: bool = False
        self.__aim: bool = False
        self.__aim_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__draw: bool = False

    def start(self) -> None:
        self.actor.draw_time = 0.0
        self.actor.set_animation(self.__animation)
        self.actor.load_scope()

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move = controllers.INPUT_CONTROLLER.get_movement()
            self.__aim = controllers.INPUT_CONTROLLER.get_aim()
            self.__aim_vec = controllers.INPUT_CONTROLLER.get_aim_vec()
            self.__draw = controllers.INPUT_CONTROLLER.get_draw()

    def update(self, dt: float) -> Optional[str]:
        # Read input.
        self.__fetch_input()

        self.actor.set_cam_target_distance_mag(mag = self.__aim_vec.mag * 0.75)

        # Check for state changes.
        if self.__move:
            return PlayerStates.AIM_WALK

        if not self.__aim:
            return PlayerStates.IDLE

        if self.__draw:
            return PlayerStates.DRAW

        # Set aim direction.
        self.actor.stats.look_dir = self.__aim_vec.heading

class PlayerAimWalkState(PlayerState):
    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_atk_hold_0_walk.json")

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__aim_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__draw: bool = False

    def start(self) -> None:
        self.actor.draw_time = 0.0
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = controllers.INPUT_CONTROLLER.get_movement_vec()
            self.__aim_vec = controllers.INPUT_CONTROLLER.get_aim_vec()
            self.__draw = controllers.INPUT_CONTROLLER.get_draw()

    def update(self, dt: float) -> Optional[str]:
        # Read input.
        self.__fetch_input()

        self.actor.set_cam_target_distance_mag(mag = self.__aim_vec.mag * 0.75)

        # Set move direction.
        self.actor.stats.move_dir = self.__move_vec.heading

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
        if self.__move_vec.mag <= 0:
            return PlayerStates.AIM

        if self.__aim_vec.mag <= 0.0:
            return PlayerStates.IDLE

        if self.__draw:
            return PlayerStates.DRAW

        # Set aim direction.
        self.actor.stats.look_dir = self.__aim_vec.heading

class PlayerDrawState(PlayerState):
    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_atk_hold_1.json")

        # Input.
        self.__move: bool = False
        self.__aim_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__draw: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move = controllers.INPUT_CONTROLLER.get_movement()
            self.__aim_vec = controllers.INPUT_CONTROLLER.get_aim_vec()
            self.__draw = controllers.INPUT_CONTROLLER.get_draw()

    def update(self, dt: float) -> Optional[str]:
        # Read input.
        self.__fetch_input()

        # Update draw time.
        self.actor.draw_time = self.actor.draw_time + dt

        self.actor.set_cam_target_distance_mag(mag = self.__aim_vec.mag)

        # Set aim direction.
        self.actor.stats.look_dir = self.__aim_vec.heading

        # Build shoot magnitude.
        if self.actor.draw_time >= self.actor.stats.min_draw_time:
            shoot_mag: float = self.actor.get_shoot_mag()
            self.actor.set_shoot_mag(shoot_mag + dt)

        # Check for state changes.
        if self.__move:
            return PlayerStates.DRAW_WALK

        if self.__aim_vec.mag <= 0.0:
            # Reset shoot magnitude.
            self.actor.set_shoot_mag(0.0)

            return PlayerStates.IDLE

        if not self.__draw:
            if self.actor.draw_time > self.actor.stats.min_draw_time:
                return PlayerStates.SHOOT
            else:
                return PlayerStates.AIM

class PlayerDrawWalkState(PlayerState):
    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_atk_hold_1_walk.json")

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__aim_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__draw: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = controllers.INPUT_CONTROLLER.get_movement_vec()
            self.__aim_vec = controllers.INPUT_CONTROLLER.get_aim_vec()
            self.__draw = controllers.INPUT_CONTROLLER.get_draw()

    def update(self, dt: float) -> Optional[str]:
        # Read input.
        self.__fetch_input()

        # Update draw time.
        self.actor.draw_time = self.actor.draw_time + dt

        self.actor.set_cam_target_distance_mag(mag = self.__aim_vec.mag)

        # Set aim direction.
        self.actor.stats.look_dir = self.__aim_vec.heading
        self.actor.stats.move_dir = self.__move_vec.heading

        target_speed: float = self.actor.stats.max_speed / 4

        # Set player stats.
        if self.actor.stats.speed < target_speed:
            self.actor.stats.speed += self.actor.stats.accel * dt
        else:
            self.actor.stats.speed -= self.actor.stats.accel * dt
        self.actor.stats.speed = pm.clamp(self.actor.stats.speed, 0.0, self.actor.stats.max_speed)

        # Move the player.
        self.actor.move(dt = dt)

        # Build shoot magnitude.
        if self.actor.draw_time >= self.actor.stats.min_draw_time:
            shoot_mag: float = self.actor.get_shoot_mag()
            self.actor.set_shoot_mag(shoot_mag + dt)

        # Check for state changes.
        if self.__move_vec.mag <= 0:
            return PlayerStates.DRAW

        if self.__aim_vec.mag <= 0.0:
            # Reset shoot magnitude.
            self.actor.set_shoot_mag(0.0)

            return PlayerStates.IDLE

        if not self.__draw:
            if self.actor.draw_time > self.actor.stats.min_draw_time:
                return PlayerStates.SHOOT
            else:
                return PlayerStates.AIM_WALK

class PlayerShootState(PlayerState):
    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_atk_shoot_1.json")

        # Input.
        self.__aim: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

        # Create a projectile.
        if scenes.ACTIVE_SCENE is not None:
            scenes.ACTIVE_SCENE.add_child(ArrowNode(
                x = self.actor.x + self.actor.scope_offset[0],
                y = self.actor.y + self.actor.scope_offset[1],
                speed = scale(self.actor.get_shoot_mag(), (0.0, 1.0), (100.0, 500.0)),
                direction = self.actor.stats.look_dir,
                batch = self.actor.batch
            ))

            scenes.ACTIVE_SCENE.shake_camera(magnitude = 5.0, duration = 0.1)

    def end(self) -> None:
        # Reset shoot magnitude.
        self.actor.set_shoot_mag(0.0)
        self.actor.set_cam_target_distance_mag(mag = 0.0)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__aim = controllers.INPUT_CONTROLLER.get_aim()

    def update(self, dt: float) -> Optional[str]:
        # Read input.
        self.__fetch_input()

    def on_animation_end(self) -> Optional[str]:
        if not self.__aim:
            return PlayerStates.IDLE
        else:
            return PlayerStates.AIM