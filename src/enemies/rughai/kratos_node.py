from enum import Enum
from typing import Optional
import pyglet
from amonite.animation import Animation

from amonite.node import PositionNode
from amonite.sprite_node import SpriteNode
from amonite.state_machine import State, StateMachine

class KratosStates(str, Enum):
    IDLE = "idle"

class KratosNode(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        self.batch: Optional[pyglet.graphics.Batch] = batch

        # Animations.
        self.__sprite = SpriteNode(
            resource = Animation(source = "sprites/iryo/iryo_idle.json").content,
            on_animation_end = self.on_sprite_animation_end,
            x = x,
            y = y,
            batch = batch
        )

        # State machine.
        self.__state_machine = StateMachine(
            states = {
                KratosStates.IDLE: KratosIdleState(actor = self)
            }
        )

    def on_sprite_animation_end(self):
        self.__state_machine.on_animation_end()

class KratosState(State):
    """
    Base class for Kratos states.
    """

    def __init__(
        self,
        actor: KratosNode
    ) -> None:
        super().__init__()

        self.actor = actor

class KratosIdleState(KratosState):
    def __init__(
        self,
        actor: KratosNode
    ) -> None:
        super().__init__(actor)