"""
Module containing the main player's classes.
"""

from enum import Enum
import math
import pyglet
import pyglet.math as pm

from amonite.loading_indicator_node import LoadingIndicatorNode
from amonite.utils import utils
from amonite.utils.tween import Tween
import amonite.controllers as controllers
from amonite.animation import Animation
from amonite.collision.collision_node import CollisionNode, CollisionType
from amonite.collision.collision_shape import CollisionRect
from amonite.node import PositionNode
from amonite.sprite_node import SpriteNode
from amonite.settings import GLOBALS, SETTINGS, Keys
from amonite.state_machine import State, StateMachine

from constants import collision_tags, uniques
from scope_node import ScopeNode
from player_stats import PlayerStats
from arrow_node import ArrowNode

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
    FALL = "fall"

class PlayerNode(PositionNode):
    """
    Main player class.
    """

    __slots__ = (
        "batch",
        "run_threshold",
        "stats",
        "__hor_facing",
        "__shoot_mag",
        "draw_time",
        "draw_sound",
        "shoot_sound",
        "__sprite",

        "scope_offset",
        "__scope",
        "draw_indicator",
        "interactor_distance",
        "__shadow_sprite",
        "__collider",
        "__interactor",

        # Cam target info.
        "__cam_target_distance",
        "__cam_target_distance_fill",
        "__cam_target_offset",
        "__cam_target",

        # State machine.
        "__state_machine"
    )

    def __init__(
        self,
        cam_target: PositionNode,
        cam_target_offset: tuple = (0.0, 8.0),
        x: float = 0,
        y: float = 0,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        PositionNode.__init__(
            self,
            x = x,
            y = y
        )

        self.batch: pyglet.graphics.Batch | None = batch

        self.interactor_distance: float = 5.0

        self.run_threshold: float = 0.75

        self.stats: PlayerStats = PlayerStats(
            vitality = 5,
            resistance = 5,
            odds = 5,
            variation = 0.2
        )

        self.__hor_facing: int = 1

        # Current draw time (in seconds).
        self.draw_time: float = 0.0

        # Draw sound.
        self.draw_sound: pyglet.media.StaticSource = pyglet.media.StaticSource(pyglet.resource.media(name = "sounds/iryo_draw_1.wav"))
        self.shoot_sound: pyglet.media.StaticSource = pyglet.media.StaticSource(pyglet.resource.media(name = "sounds/iryo_shoot_1.wav"))

        # Animations.
        self.__sprite = SpriteNode(
            resource = Animation(source = "sprites/iryo/iryo_idle.json").content,
            on_animation_end = self.on_sprite_animation_end,
            x = x,
            y = y,
            batch = batch
        )

        # Scope.
        self.scope_offset: tuple[float, float] = (0.0, 8.0)
        self.__scope = ScopeNode(
            x = self.x,
            y = self.y,
            offset_x = self.scope_offset[0],
            offset_y = self.scope_offset[1],
            batch = batch
        )

        # Draw loading indicator.
        self.draw_indicator: LoadingIndicatorNode = LoadingIndicatorNode(
            foreground_sprite_res = pyglet.resource.image("sprites/loading_foreground.png"),
            background_sprite_res = pyglet.resource.image("sprites/loading_background.png"),
            x = self.x,
            y = self.y,
            offset_y = 4,
            ease_function = Tween.cubeInOut,
            batch = batch
        )

        # Shadow sprite image.
        shadow_image = pyglet.resource.image("sprites/shadow.png")
        utils.set_anchor(shadow_image, center = True)

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
                collision_tags.PLAYER_SENSE,
                collision_tags.FALL
            ],
            passive_tags = [
                collision_tags.DAMAGE
            ],
            shape = CollisionRect(
                x = x,
                y = y,
                anchor_x = 3,
                anchor_y = 3,
                width = 6,
                height = 6,
                batch = batch
            ),
            on_triggered = self.on_collision
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
            shape = CollisionRect(
                x = x,
                y = y,
                anchor_x = 4,
                anchor_y = 4,
                width = 8,
                height = 8,
                batch = batch
            )
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__interactor)

        self.__cam_target_distance = 50.0
        self.__cam_target_distance_fill = 0.0
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
                PlayerStates.SHOOT: PlayerShootState(actor = self),
                PlayerStates.FALL: PlayerFallState(actor = self)
            }
        )

    def delete(self) -> None:
        self.__sprite.delete()
        self.__shadow_sprite.delete()
        self.__collider.delete()
        self.__interactor.delete()
        self.__scope.delete()
        self.draw_indicator.delete()

    # def pre_update(self, dt: float) -> None:
    #     super().pre_update(dt = dt)

    #     # Compute velocity.
    #     velocity: pyglet.math.Vec2 = self.__compute_velocity(dt = dt)

    #     self.__set_velocity(velocity = velocity)

    def update(self, dt) -> None:
        super().update(dt = dt)

        # Update the state machine.
        self.__state_machine.update(dt = dt)

        # Update sprites accordingly.
        self.__update_sprites(dt = dt)

    def set_position(
        self,
        position: tuple[float, float],
        z: float | None = None
    ):
        super().set_position(position = position, z = z)
        self.__collider.set_position(position = position)

    def on_collision(self, tags: list[str], entered: bool) -> None:
        self.__state_machine.on_collision(tags = tags, enter = entered)

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

    def get_input_movement(self) -> bool:
        return controllers.INPUT_CONTROLLER.get_movement()

    def get_input_aim(self) -> bool:
        return False if controllers.INVENTORY_CONTROLLER.is_open or controllers.MENU_CONTROLLER.is_open else controllers.INPUT_CONTROLLER.get_aim()

    def get_input_movement_vec(self) -> pm.Vec2:
        return controllers.INPUT_CONTROLLER.get_movement_vec()

    def get_input_aim_vec(self) -> pm.Vec2:
        return pm.Vec2() if controllers.INVENTORY_CONTROLLER.is_open or controllers.MENU_CONTROLLER.is_open else controllers.INPUT_CONTROLLER.get_aim_vec()

    def get_input_sprint(self) -> bool:
        return controllers.INPUT_CONTROLLER.get_sprint()

    def get_input_shift(self) -> bool:
        return controllers.INPUT_CONTROLLER.get_shift()

    def get_input_interaction(self) -> bool:
        return controllers.INPUT_CONTROLLER.get_interaction()

    def get_input_draw(self) -> bool:
        return controllers.INPUT_CONTROLLER.get_draw()

    def set_animation(self, animation: Animation) -> None:
        self.__sprite.set_image(animation.content)

    # def __compute_velocity(self, dt: float) -> pm.Vec2:
    #     # Define a vector from speed and direction.
    #     return pm.Vec2.from_polar(self.stats.speed * dt, self.stats.move_dir)

    def __set_velocity(self, velocity: pyglet.math.Vec2) -> None:
        # Apply the computed velocity to all colliders.
        self.__collider.set_velocity((round(velocity.x, GLOBALS[Keys.FLOAT_ROUNDING]), round(velocity.y, 5)))
        self.__interactor.set_velocity((round(velocity.x, GLOBALS[Keys.FLOAT_ROUNDING]), round(velocity.y, 5)))

    def move(self, dt: float) -> None:
        # Apply movement after collision.
        self.set_position(self.__collider.get_position())

        # Compute velocity.
        velocity: pyglet.math.Vec2 = pm.Vec2.from_polar(self.stats.speed, self.stats.move_dir)

        self.__set_velocity(velocity = velocity)

    def __update_sprites(self, dt):
        # Only update facing if there's any horizontal movement.
        dir_cos = math.cos(self.stats.look_dir)
        dir_len = abs(dir_cos)
        if dir_len > 0.1:
            self.__hor_facing = int(math.copysign(1.0, dir_cos))

        # Update sprite position.
        self.__sprite.set_position(self.get_position())

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
            position = self.get_position(),
            # z = 0
            z = -(self.y + (SETTINGS[Keys.LAYERS_Z_SPACING] * 0.1))
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
        self.draw_indicator.set_fill(fill = draw_indicator_value / self.stats.min_draw_time)
        self.draw_indicator.set_position(position = self.get_position())
        self.draw_indicator.update(dt = dt)

    def set_cam_target_distance_fill(self, fill: float) -> None:
        """
        Sets the fill (between 0 and 1) for cam target distance.
        """

        assert fill >= 0.0 and fill <= 1.0, "Value out of range"

        self.__cam_target_distance_fill = fill

    def __update_cam_target(self, dt: float):
        # Automatically go to cam target distance if loading or aiming.
        cam_target_distance: float = self.__cam_target_distance * self.__cam_target_distance_fill

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

    def __update_collider(self, dt):
        self.__collider.update(dt)

    def get_bounding_box(self):
        return self.__sprite.get_bounding_box()

class PlayerStateMachine(StateMachine):
    """
    Player state machine specialization. Handles player state transitions and adds input management.
    """

    def enable_input(self) -> None:
        """
        Enables input handling on the current state.
        """

        # Just return if there's no current state.
        if self.current_key is None:
            return

        # Retrieve the current state.
        current_state: State = self.states[self.current_key]

        if isinstance(current_state, PlayerState):
            current_state.enable_input()

    def disable_input(self) -> None:
        """
        Disables input handling on the current state.
        """

        # Just return if there's no current state.
        if self.current_key is None:
            return

        # Retrieve the current state.
        current_state: State = self.states[self.current_key]

        if isinstance(current_state, PlayerState):
            current_state.disable_input()

    def on_collision(self, tags: list[str], enter: bool) -> None:
        # Transition to fall state if a fall collision is met.
        if enter and collision_tags.FALL in tags:
            self.transition(PlayerStates.FALL)

class PlayerState(State):
    """
    Base class for player states.
    """

    __slots__ = (
        "input_enabled",
        "actor"
    )

    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__()

        self.input_enabled: bool = True
        self.actor: PlayerNode = actor

    def enable_input(self) -> None:
        """
        Enables all input reading.
        """

        self.input_enabled = True

    def disable_input(self) -> None:
        """
        Disables all input reading.
        """

        self.input_enabled = False

class PlayerIdleState(PlayerState):
    """
    Player IDLE state.
    Plays idle animations and defines state transitions to LOAD, WALK and ROLL.
    """

    __slots__ = (
        "__animation",

        # Input buffers.
        "__move",
        "__aim",
        "__sprint",
        "__interact"
    )

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
        self.actor.draw_indicator.hide()

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move = self.actor.get_input_movement()
            self.__aim = self.actor.get_input_aim()
            self.__sprint = self.actor.get_input_sprint()
            self.__interact = self.actor.get_input_interaction()

    def update(self, dt: float) -> str | None:
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
    """
    Player WALK state.
    Plays walk animations and defines state transitions to LOAD, ROLL, IDLE and RUN.
    """

    __slots__ = (
        "__animation",

        # Input buffers.
        "__move_vec",
        "__aim",
        "__shift",
        "__sprint",
        "__interact"
    )

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
            self.__move_vec = self.actor.get_input_movement_vec()
            self.__aim = self.actor.get_input_aim()
            self.__shift = self.actor.get_input_shift()
            self.__sprint = self.actor.get_input_sprint()
            self.__interact = self.actor.get_input_interaction()

    def update(self, dt: float) -> str | None:
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
    """
    Player RUN state.
    Plays run animations and defines state transitions to LOAD, ROLL and WALK.
    """

    __slots__ = (
        "__animation",

        # Input buffers.
        "__move_vec",
        "__aim",
        "__shift",
        "__sprint",
        "__interact"
    )

    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_run_2.json")

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
            self.__move_vec = self.actor.get_input_movement_vec()
            self.__aim = self.actor.get_input_aim()
            self.__shift = self.actor.get_input_shift()
            self.__sprint = self.actor.get_input_sprint()
            self.__interact = self.actor.get_input_interaction()

    def update(self, dt: float) -> str | None:
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
    """
    Player ROLL state.
    Plays roll animations and defines state transitions to IDLE and WALK.
    """

    __slots__ = (
        "__animation",
        "__startup"
    )

    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_roll_1.json")
        self.__startup: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.__startup = True

    def update(self, dt: float) -> str | None:
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

    def on_animation_end(self) -> str | None:
        if self.actor.stats.speed <= 0.0:
            return PlayerStates.IDLE
        else:
            return PlayerStates.WALK

class PlayerLoadState(PlayerState):
    """
    Player LOAD state.
    Plays load animations and defines state transitions to AIM.
    """

    __slots__ = (
        "__animation"
    )

    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_atk_load.json")

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.actor.draw_indicator.hide()

        # Read input.
        aim_vec: pyglet.math.Vec2 = controllers.INPUT_CONTROLLER.get_aim_vec()

        # Set aim direction.
        self.actor.stats.look_dir = aim_vec.heading

        # Stop moving.
        self.actor.stats.speed = 0.0

    def on_animation_end(self) -> str | None:
        return PlayerStates.AIM

class PlayerAimState(PlayerState):
    """
    Player AIM state.
    Plays load animations and defines state transitions to AIM_WALK, IDLE and DRAW.
    """

    __slots__ = (
        "__animation",

        # Input buffers.
        "__move",
        "__aim",
        "__aim_vec",
        "__draw"
    )

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
        self.actor.draw_indicator.hide()

        # Stop moving.
        self.actor.stats.speed = 0.0

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move = self.actor.get_input_movement()
            self.__aim = self.actor.get_input_aim()
            self.__aim_vec = self.actor.get_input_aim_vec()
            self.__draw = self.actor.get_input_draw()

    def update(self, dt: float) -> str | None:
        # Read input.
        self.__fetch_input()

        self.actor.set_cam_target_distance_fill(fill = self.__aim_vec.mag * 0.75)

        # Check for state changes.
        if self.__move:
            return PlayerStates.AIM_WALK

        if not self.__aim:
            return PlayerStates.IDLE

        if self.__draw:
            controllers.SOUND_CONTROLLER.play_effect(self.actor.draw_sound)
            return PlayerStates.DRAW

        # Set aim direction.
        self.actor.stats.look_dir = self.__aim_vec.heading

class PlayerAimWalkState(PlayerState):
    """
    Player AIM_WALK state.
    Plays walking aim animations and defines state transitions to AIM, IDLE and DRAW.
    """

    __slots__ = (
        "__animation",

        # Input buffers.
        "__move_vec",
        "__aim_vec",
        "__draw"
    )

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
        self.actor.draw_indicator.hide()

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = self.actor.get_input_movement_vec()
            self.__aim_vec = self.actor.get_input_aim_vec()
            self.__draw = self.actor.get_input_draw()

    def update(self, dt: float) -> str | None:
        # Read input.
        self.__fetch_input()

        self.actor.set_cam_target_distance_fill(fill = self.__aim_vec.mag * 0.75)

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
            controllers.SOUND_CONTROLLER.play_effect(self.actor.draw_sound)
            return PlayerStates.DRAW

        # Set aim direction.
        self.actor.stats.look_dir = self.__aim_vec.heading

class PlayerDrawState(PlayerState):
    """
    Player DRAW state.
    Plays draw animations and defines state transitions to DRAW_WALK, IDLE, SHOOT and AIM.
    """

    __slots__ = (
        "__animation",

        # Input buffers.
        "__move",
        "__aim_vec",
        "__draw"
    )

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
        self.actor.draw_indicator.show()

        # Stop moving.
        self.actor.stats.speed = 0.0

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move = self.actor.get_input_movement()
            self.__aim_vec = self.actor.get_input_aim_vec()
            self.__draw = self.actor.get_input_draw()

    def update(self, dt: float) -> str | None:
        # Read input.
        self.__fetch_input()

        # Update draw time.
        self.actor.draw_time = self.actor.draw_time + dt

        self.actor.set_cam_target_distance_fill(fill = self.__aim_vec.mag)

        # Set aim direction.
        self.actor.stats.look_dir = self.__aim_vec.heading

        # Check for state changes.
        if self.__move:
            return PlayerStates.DRAW_WALK

        if self.__aim_vec.mag <= 0.0:
            return PlayerStates.IDLE

        if not self.__draw:
            if self.actor.draw_time > self.actor.stats.min_draw_time:
                return PlayerStates.SHOOT
            else:
                return PlayerStates.AIM

class PlayerDrawWalkState(PlayerState):
    """
    Player DRAW_WALK state.
    Plays walking draw animations and defines state transitions to DRAW, IDLE, SHOOT and AIM_WALK.
    """

    __slots__ = (
        "__animation",

        # Input buffers.
        "__move_vec",
        "__aim_vec",
        "__draw"
    )

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
        self.actor.draw_indicator.show()

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = self.actor.get_input_movement_vec()
            self.__aim_vec = self.actor.get_input_aim_vec()
            self.__draw = self.actor.get_input_draw()

    def update(self, dt: float) -> str | None:
        # Read input.
        self.__fetch_input()

        # Update draw time.
        self.actor.draw_time = self.actor.draw_time + dt

        self.actor.set_cam_target_distance_fill(fill = self.__aim_vec.mag)

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

        # Check for state changes.
        if self.__move_vec.mag <= 0:
            return PlayerStates.DRAW

        if self.__aim_vec.mag <= 0.0:
            return PlayerStates.IDLE

        if not self.__draw:
            if self.actor.draw_time > self.actor.stats.min_draw_time:
                return PlayerStates.SHOOT
            else:
                return PlayerStates.AIM_WALK

class PlayerShootState(PlayerState):
    """
    Player SHOOT state.
    Plays shoot animations and defines state transitions to IDLE and AIM.
    """

    __slots__ = (
        "__animation",

        # Input buffers.
        "__aim"
    )

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

        # Hide loading indicator.
        self.actor.draw_indicator.hide()

        if uniques.ACTIVE_SCENE is not None:
            # Create a projectile.
            uniques.ACTIVE_SCENE.add_child(ArrowNode(
                x = self.actor.x + self.actor.scope_offset[0],
                y = self.actor.y + self.actor.scope_offset[1],
                speed = 500.0,
                direction = self.actor.stats.look_dir,
                batch = self.actor.batch
            ))

            # Camera feedback.
            uniques.ACTIVE_SCENE.apply_cam_impulse(
                impulse = pyglet.math.Vec2.from_polar(
                    mag = 10.0,
                    angle = self.actor.stats.look_dir
                )
            )

        controllers.SOUND_CONTROLLER.play_effect(self.actor.shoot_sound)

        # Stop moving.
        self.actor.stats.speed = 0.0

    def end(self) -> None:
        self.actor.set_cam_target_distance_fill(fill = 0.0)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled and not (controllers.INVENTORY_CONTROLLER.is_open or controllers.MENU_CONTROLLER.is_open):
            self.__aim = controllers.INPUT_CONTROLLER.get_aim()

    def update(self, dt: float) -> str | None:
        # Read input.
        self.__fetch_input()

    def on_animation_end(self) -> str | None:
        if not self.__aim:
            return PlayerStates.IDLE
        else:
            return PlayerStates.AIM

class PlayerFallState(PlayerState):
    def __init__(
        self,
        actor: PlayerNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_fall.json")

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

        # Hide loading indicator.
        self.actor.draw_indicator.hide()

    def on_animation_end(self) -> str | None:
        dir: float = self.actor.stats.move_dir + math.pi
        displacement_vec: pyglet.math.Vec2 = pyglet.math.Vec2.from_polar(mag = 10.0, angle = dir)
        self.actor.set_position((self.actor.x + displacement_vec.x, self.actor.y + displacement_vec.y))

        return PlayerStates.IDLE