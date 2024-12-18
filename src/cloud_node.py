import os
import random
from typing import Optional
import math
import pyglet
import pyglet.math as pm

from amonite.node import PositionNode
from amonite.sprite_node import SpriteNode
from amonite.settings import SETTINGS, Keys

class CloudNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = SETTINGS[Keys.LAYERS_Z_SPACING]
        )

        self.speed = 5
        self.dir = 10

        # Pick a random cloud sprite.
        self.image = pyglet.resource.image(f"sprites/clouds/cloud_{random.randint(0, 7)}.png")
        # Center sprite.
        self.image.anchor_x = int(self.image.width / 2)
        self.image.anchor_y = int(self.image.height / 2)

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
        shader_program["alpha"] = 0.25

        self.sprite = SpriteNode(
            x = x,
            y = y,
            z = self.z,
            y_sort = False,
            resource = self.image,
            shader = shader_program,
            batch = batch
        )

    def get_bounding_box(self) -> tuple[float, float, float, float]:
        return (
            self.x - self.image.anchor_x,
            self.y - self.image.anchor_y,
            self.image.width,
            self.image.height
        )

    def update(self, dt: int) -> None:
        # movement = pm.Vec2.from_polar(self.speed * dt, self.dir * (math.pi / 180.0))
        movement = pm.Vec2(self.speed * dt, math.sin(self.x / 10) * 2 * dt)
        self.set_position(
            position = (self.x + movement.x, self.y + movement.y),
        )
        self.sprite.set_position(
            position = (self.x + movement.x, self.y + movement.y),
            z = self.z
        )

    def delete(self) -> None:
        self.sprite.delete()