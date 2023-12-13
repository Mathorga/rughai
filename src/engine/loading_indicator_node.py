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
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        background_color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0),
        foreground_color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        starting_value: float = 1.0,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        # Center all sprites.
        foreground_sprite_res.anchor_x = foreground_sprite_res.width / 2 + offset_x
        foreground_sprite_res.anchor_y = foreground_sprite_res.height / 2 + offset_y
        if background_sprite_res is not None:
            background_sprite_res.anchor_x = background_sprite_res.width / 2 + offset_x
            background_sprite_res.anchor_y = background_sprite_res.height / 2 + offset_y
        if frame_sprite_res is not None:
            frame_sprite_res.anchor_x = frame_sprite_res.width / 2 + offset_x
            frame_sprite_res.anchor_y = frame_sprite_res.height / 2 + offset_y

        # Load shader sources from file.
        fragment_source: str
        with open(file = os.path.join(pyglet.resource.path[0], "../shaders/loading_indicator.frag"), mode = "r", encoding = "UTF8") as file:
            fragment_source = file.read()

        # Create shader program from vector and fragment.
        vert_shader = pyglet.graphics.shader.Shader(pyglet.sprite.vertex_source, "vertex")
        frag_shader = pyglet.graphics.shader.Shader(fragment_source, "fragment")
        self.shader_program = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

        # Pass non sampler uniforms.
        # self.shader_program["value"] = starting_value

        self.foreground_sprite: SpriteNode = SpriteNode(
            resource = foreground_sprite_res,
            x = x,
            y = y,
            z = y,
            shader = self.shader_program,
            batch = batch
        )

        self.background_sprite: Optional[SpriteNode] = SpriteNode(
            resource = background_sprite_res,
            x = x,
            y = y,
            z = y - 1,
            batch = batch
        ) if background_sprite_res is not None else None

        self.frame_sprite: Optional[SpriteNode] = SpriteNode(
            resource = frame_sprite_res,
            x = x,
            y = y,
            z = y + 1,
            batch = batch
        ) if frame_sprite_res is not None else None

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        super().set_position(position, z)

        self.foreground_sprite.set_position(position = position, z = z if z is not None else position[1])

        if self.background_sprite is not None:
            self.background_sprite.set_position(position = position, z = (z if z is not None else position[1]) - 1)

        if self.frame_sprite is not None:
            self.frame_sprite.set_position(position = position, z = (z if z is not None else position[1]) + 1)

    def set_value(self, value: float) -> None:
        assert value >= 0.0 and value <= 0.0, "Value out of range"

        # self.foreground_sprite.set_scale(x_scale = value)

        texture_coords: Tuple[
            float, float, float,
            float, float, float,
            float, float, float,
            float, float, float
        ]

        # Also pass bottom-left and top-right texture coords.
        if isinstance(self.foreground_sprite.sprite.image, pyglet.image.animation.Animation):
            texture_coords = self.foreground_sprite.sprite.image.frames[self.foreground_sprite.sprite.frame_index].tex_coords
        else:
            texture_coords = self.foreground_sprite.sprite.image.tex_coords

        self.shader_program["sw_coord"] = texture_coords[0:3]
        self.shader_program["ne_coord"] = texture_coords[6:9]
        self.shader_program["value"] = value

    def delete(self) -> None:
        self.foreground_sprite.delete()

        if self.background_sprite is not None:
            self.background_sprite.delete()

        if self.frame_sprite is not None:
            self.frame_sprite.delete()