from enum import Enum
import os
import pyglet
from amonite.animation import Animation

from amonite.node import PositionNode
from amonite.settings import SETTINGS, Keys
from amonite.sprite_node import SpriteNode
from amonite.state_machine import State, StateMachine

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
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(x, y, z)

        self.batch: pyglet.graphics.Batch | None = batch

        # Aim sprite offset, defines the offset from self.x and self.y, respectively.
        self.sprite_offset: tuple[float, float] = (offset_x, offset_y)

        # Sprite distance, defines the distance at which the sprite floats.
        self.sprite_distance: float = 10.0

        self.direction = 0.0

        # State sprite.
        self.animations: list[Animation] = [
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

        # Load fragment source from file.
        fragment_source: str
        with open(
            file = os.path.join(pyglet.resource.path[0], "../shaders/alpha_blend.frag"),
            mode = "r",
            encoding = "UTF8"
        ) as file:
            fragment_source = file.read()

        # Create shader program from vector and fragment.
        vert_shader = pyglet.graphics.shader.Shader(pyglet.sprite.vertex_source, "vertex")
        frag_shader = pyglet.graphics.shader.Shader(fragment_source, "fragment")
        shader_program = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)
        shader_program["alpha"] = 0.5

        # Create sprites.
        self.sprites: list[SpriteNode] = []
        for animation in self.animations:
            self.sprites.append(
                SpriteNode(
                    resource = animation.content,
                    x = x,
                    y = y,
                    shader = shader_program,
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
        position: tuple[float, float],
        z: float | None = None
    ) -> None:
        super().set_position(position = position, z = z)

        aim_vec = pyglet.math.Vec2.from_polar(self.sprite_distance, self.direction)
        for index, sprite in enumerate(self.sprites):
            sprite.set_position(
                position = (
                    position[0] + self.sprite_offset[0] + aim_vec.x + aim_vec.x * self.sprites_delta * (index + 1),
                    position[1] + self.sprite_offset[1] + aim_vec.y + aim_vec.y * self.sprites_delta * (index + 1)
                ),
                z = position[1] + SETTINGS[Keys.LAYERS_Z_SPACING] * 0.5
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

    def update(self, dt: float) -> str | None:
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

    def update(self, dt: float) -> str | None:
        if self.actor.sprites_delta < self.__target_delta:
            self.actor.sprites_delta = self.actor.sprites_delta + self.__delta_speed * dt