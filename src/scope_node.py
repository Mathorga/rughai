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

        # State machine.
        self.__state_machine = ScopeStateMachine(
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

        self.__state_machine.set_position(position = position, z = z)

    def set_direction(
        self,
        direction: float
    ) -> None:
        self.direction = direction

    def load(self) -> None:
        self.__state_machine.set_state(ScopeStates.LOAD)

    def unload(self) -> None:
        self.__state_machine.set_state(ScopeStates.IDLE)

class ScopeStateMachine(StateMachine):
    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        if self.current_key is None:
            return

        # Retrieve the current state.
        current_state: State = self.states[self.current_key]

        if isinstance(current_state, ScopeState):
            current_state.set_position(position = position, z = z)

    def set_direction(
        self,
        direction: float
    ) -> None:
        if self.current_key is None:
            return

        # Retrieve the current state.
        current_state: State = self.states[self.current_key]

        if isinstance(current_state, ScopeState):
            current_state.set_direction(direction = direction)

class ScopeState(State):
    def __init__(
        self,
        actor: ScopeNode
    ) -> None:
        super().__init__()

        self.input_enabled: bool = True
        self.actor: ScopeNode = actor

    def onAnimationEnd(self) -> None:
        pass

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        pass

    def set_direction(
        self,
        direction: float
    ) -> None:
        pass

class ScopeIdleState(ScopeState):
    def __init__(
        self,
        actor: ScopeNode
    ) -> None:
        super().__init__(actor)

        self.__animation: Animation = Animation(source = "sprites/scope/scope_idle.json")
        self.__sprite: Optional[SpriteNode] = None

    def start(self) -> None:
        # State sprite.
        self.__sprite = SpriteNode(
            resource = self.__animation.content,
            x = self.actor.x,
            y = self.actor.y,
            batch = self.actor.batch
        )

    def end(self) -> None:
        self.__sprite.delete()

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        if self.__sprite is None:
            return

        aim_vec = pyglet.math.Vec2.from_polar(self.actor.sprite_distance, self.actor.direction)
        self.__sprite.set_position(
            position = (
                position[0] + self.actor.sprite_offset[0] + aim_vec.x + aim_vec.x,
                position[1] + self.actor.sprite_offset[1] + aim_vec.y + aim_vec.y
            ),
            z = position[1] + SETTINGS[Builtins.LAYERS_Z_SPACING] * 0.5
        )

class ScopeLoadState(ScopeState):
    def __init__(
        self,
        actor: ScopeNode
    ) -> None:
        super().__init__(actor)

        # State sprite.
        self.__animation: Animation = Animation(source = "sprites/scope/scope_idle.json")

        # Number of adjacent sprites to draw.
        self.__sprites_num: int = 15

        # Distance between each sprite.
        self.__sprites_delta: float = 0.5

        self.__sprites: List[SpriteNode] = []

    def start(self) -> None:
        for i in range(self.__sprites_num):
            print(self.__sprites)
            self.__sprites.append(
                SpriteNode(
                    resource = self.__animation.content,
                    x = self.actor.x,
                    y = self.actor.y,
                    batch = self.actor.batch
                )
            )

    def end(self) -> None:
        for i in range(self.__sprites_num):
            self.__sprites[i].delete()

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        aim_vec = pyglet.math.Vec2.from_polar(self.actor.sprite_distance, self.actor.direction)
        for index, sprite in enumerate(self.__sprites):
            print(index)
            sprite.set_position(
                position = (
                    position[0] + self.actor.sprite_offset[0] + aim_vec.x + aim_vec.x * self.__sprites_delta * (index + 1),
                    position[1] + self.actor.sprite_offset[1] + aim_vec.y + aim_vec.y * self.__sprites_delta * (index + 1)
                ),
                z = position[1] + SETTINGS[Builtins.LAYERS_Z_SPACING] * 0.5
            )