from enum import Enum
from typing import List, Optional, Tuple
import pyglet
import pyglet.math as pm

from engine.animation import Animation
from engine.node import PositionNode
from engine.settings import SETTINGS, Builtins
from engine.sprite_node import SpriteNode
from engine.state_machine import State, StateMachine

class ArrowStates(str, Enum):
    FLY = "fly"
    HIT = "hit"

class ArrowNode(PositionNode):
    """
    Arrow projectile class.
    """

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        direction: float = 0.0,
        speed: float = 0.0,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        self.batch: Optional[pyglet.graphics.Batch] = batch

        self.direction: float = direction
        self.speed: float = speed

        # Animation handlers.
        self.animations: List[Animation] = [
            Animation(source = "sprites/scope/scope_load_0.json"),
            Animation(source = "sprites/scope/scope_load_0.json"),
            Animation(source = "sprites/scope/scope_load_1.json"),
            Animation(source = "sprites/scope/scope_load_2.json"),
            Animation(source = "sprites/scope/scope_load_3.json"),
            Animation(source = "sprites/scope/scope_load_4.json")
        ]

        # Distance between each sprite.
        self.sprites_delta: float = 1.5

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
                ArrowStates.FLY: ArrowFlyState(actor = self),
                ArrowStates.HIT: ArrowFlyState(actor = self)
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

        aim_vec = pyglet.math.Vec2.from_polar(1.0, self.direction)
        for index, sprite in enumerate(self.sprites):
            sprite.set_position(
                position = (
                    position[0] + aim_vec.x + aim_vec.x * self.sprites_delta * (index + 1),
                    position[1] + aim_vec.y + aim_vec.y * self.sprites_delta * (index + 1)
                ),
                z = position[1] + SETTINGS[Builtins.LAYERS_Z_SPACING] * 0.5
            )

class ArrowState(State):
    def __init__(
        self,
        actor: ArrowNode
    ) -> None:
        super().__init__()

        self.actor: ArrowNode = actor

class ArrowFlyState(ArrowState):
    def update(self, dt: float) -> Optional[str]:
        # Define a vector from speed and direction.
        movement: pm.Vec2 = pm.Vec2.from_polar(self.actor.speed * dt, self.actor.direction)
        actor_position: Tuple[float, float] = self.actor.get_position()
        self.actor.set_position((actor_position[0] + movement.x, actor_position[1] + movement.y))