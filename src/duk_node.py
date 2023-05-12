import os
from typing import Optional
import pyglet
import pyglet.gl as gl

from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.utils import *

class DukNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        scaling: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y)

        self.__scaling = scaling

        self.__idle_animation = pyglet.resource.animation("sprites/rughai/wilds/duk/duk_idle.gif")
        animation_set_anchor(
            animation = self.__idle_animation,
            x = self.__idle_animation.get_max_width() / 2,
            y = 0
        )

        # Load fragment source from file.
        fragment_source: str
        with open(os.path.join(pyglet.resource.path[0], "../shaders/color_swap.frag"), "r") as file:
            fragment_source = file.read()

        # Create shader program from vector and fragment.
        vert_shader = pyglet.graphics.shader.Shader(pyglet.sprite.vertex_source, "vertex")
        frag_shader = pyglet.graphics.shader.Shader(fragment_source, "fragment")
        shader_program = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

        # Load palette texture.
        palette: pyglet.image.TextureRegion = pyglet.resource.image("sprites/rughai/wilds/duk/duk_palette.png")

        # print(shader_program.uniforms["palette"].type)

        # Pass the palette as uniform.
        # shader_program["palette"] = gl.GL_TEXTURE0

        shader_program["mixer"] = 0.8
        # shader_program["hit"] = False

        self.__sprite = SpriteNode(
            resource = self.__idle_animation,
            x = x,
            y = y,
            scaling = scaling,
            on_animation_end = lambda : None,
            shader = shader_program,
            samplers_2d = {
                "palette": palette
            },
            batch = batch
        )

    def draw(self) -> None:
        self.__sprite.draw()