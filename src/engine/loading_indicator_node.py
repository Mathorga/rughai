import os
from typing import Optional, Tuple, Union
import pyglet

from engine.animation import Animation
from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine import utils

class LoadingIndicatorNode(PositionNode):
    def __init__(
        self,
        foreground_sprite_res: Union[pyglet.image.animation.Animation, pyglet.image.TextureRegion],
        background_sprite_res: Optional[Union[pyglet.image.animation.Animation, pyglet.image.TextureRegion]] = None,
        frame_sprite_res: Optional[Union[pyglet.image.animation.Animation, pyglet.image.TextureRegion]] = None,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        starting_value: float = 1.0,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        # Load fragment source from file.
        fragment_source: str
        with open(file = os.path.join(pyglet.resource.path[0], "../shaders/loading_indicator.frag"), mode = "r", encoding = "UTF8") as file:
            fragment_source = file.read()

        # Create shader program from vector and fragment.
        vert_shader = pyglet.graphics.shader.Shader(pyglet.sprite.vertex_source, "vertex")
        frag_shader = pyglet.graphics.shader.Shader(fragment_source, "fragment")
        self.shader_program = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

        # Pass non sampler uniforms.
        self.shader_program["value"] = starting_value

        self.foreground_sprite: SpriteNode = SpriteNode(
            resource = foreground_sprite_res,
            x = x,
            y = y,
            z = y,
            shader = self.shader_program,
            batch = batch
        )

        self.background_sprite: SpriteNode = SpriteNode(
            resource = background_sprite_res,
            x = x,
            y = y,
            z = y - 1,
            batch = batch
        )

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        super().set_position(position, z)

        self.foreground_sprite.set_position(position = position, z = z if z is not None else position[1])
        self.background_sprite.set_position(position = position, z = (z if z is not None else position[1]) - 1)

    def set_value(self, value: float) -> None:
        assert value >= 0.0 and value <= 0.0, "Value out of range"

        # self.foreground_sprite.set_scale(x_scale = value)

        self.shader_program["value"] = value