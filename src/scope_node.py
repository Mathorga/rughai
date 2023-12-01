from enum import Enum
from typing import List, Optional, Tuple
import pyglet
from engine.animation import Animation

from engine.node import PositionNode
from engine.settings import SETTINGS, Builtins
from engine.sprite_node import SpriteNode
from engine.state_machine import State, StateMachine

class ScopeStates(str, Enum):
    IDLE = "idle"
    LOAD = "load"

class ScopeNode(PositionNode):
    """
    Player scope class.
    """

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        self.batch: Optional[pyglet.graphics.Batch] = batch

        # Aim sprite offset, defines the offset from self.x and self.y, respectively.
        self.sprite_offset: Tuple[float, float] = (offset_x, offset_y)

        # Sprite distance, defines the distance at which the sprite floats.
        self.sprite_distance: float = 10.0

        self.direction = 0.0

        # State sprite.
        self.animations: List[Animation] = [
            Animation(source = "sprites/scope/scope_load_0.json"),
            Animation(source = "sprites/scope/scope_load_0.json"),
            Animation(source = "sprites/scope/scope_load_1.json"),
            Animation(source = "sprites/scope/scope_load_2.json"),
            Animation(source = "sprites/scope/scope_load_3.json"),
            Animation(source = "sprites/scope/scope_load_4.json")
        ]

        self.animations.reverse()

        # Distance between each sprite.
        self.sprites_delta: float = 0.0

        # Create sprites.
        self.sprites: List[SpriteNode] = []
        for animation in self.animations:
            self.sprites.append(
                SpriteNode(
                    resource = animation.content,
                    x = x,
                    y = y,
                    batch = batch
                )
            )

        # State machine.
        self.__state_machine = StateMachine(
            states = {
                ScopeStates.IDLE: ScopeIdleState(actor = self),
                ScopeStates.LOAD: ScopeLoadState(actor = self)
            }
        )

    def update(self, dt: float) -> None:
        super().update(dt)

        self.__state_machine.update(dt = dt)

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        super().set_position(position = position, z = z)

        aim_vec = pyglet.math.Vec2.from_polar(self.sprite_distance, self.direction)
        for index, sprite in enumerate(self.sprites):
            sprite.set_position(
                position = (
                    position[0] + self.sprite_offset[0] + aim_vec.x + aim_vec.x * self.sprites_delta * (index + 1),
                    position[1] + self.sprite_offset[1] + aim_vec.y + aim_vec.y * self.sprites_delta * (index + 1)
                ),
                z = position[1] + SETTINGS[Builtins.LAYERS_Z_SPACING] * 0.5
            )

    def set_direction(
        self,
        direction: float
    ) -> None:
        self.direction = direction

    def load(self) -> None:
        self.__state_machine.set_state(ScopeStates.LOAD)

    def unload(self) -> None:
        self.__state_machine.set_state(ScopeStates.IDLE)

    def delete(self) -> None:
        # Delete all sprites.
        for sprite in self.sprites:
            sprite.delete()

        self.sprites.clear()

class ScopeState(State):
    def __init__(
        self,
        actor: ScopeNode
    ) -> None:
        super().__init__()

        self.actor: ScopeNode = actor

class ScopeIdleState(ScopeState):
    def __init__(
        self,
        actor: ScopeNode
    ) -> None:
        super().__init__(actor)

        # Distance between each sprite.
        self.__target_delta: float = 0.0
        self.__delta_speed: float = 1.5

    def update(self, dt: float) -> Optional[str]:
        if self.actor.sprites_delta > self.__target_delta:
            self.actor.sprites_delta = self.actor.sprites_delta - self.__delta_speed * dt

class ScopeLoadState(ScopeState):
    def __init__(
        self,
        actor: ScopeNode
    ) -> None:
        super().__init__(actor)

        # Distance between each sprite.
        self.__target_delta: float = 0.15
        self.__delta_speed: float = 2.0

    def update(self, dt: float) -> Optional[str]:
        if self.actor.sprites_delta < self.__target_delta:
            self.actor.sprites_delta = self.actor.sprites_delta + self.__delta_speed * dt