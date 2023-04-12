from typing import Optional, Union
import pyglet
import pyglet.gl as gl

from engine.node import PositionNode
from engine.sprites_manager import SpritesManager

class DepthSpriteGroup(pyglet.sprite.SpriteGroup):
    def set_state(self):
        self.program.use()

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(self.texture.target, self.texture.id)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(self.blend_src, self.blend_dest)

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LESS)

    def unset_state(self):
        gl.glDisable(gl.GL_BLEND)
        gl.glDisable(gl.GL_DEPTH_TEST)
        self.program.stop()


class DepthSprite(pyglet.sprite.AdvancedSprite):
    group_class = DepthSpriteGroup

fragment_source = """#version 150 core
    in vec4 vertex_colors;
    in vec3 texture_coords;
    out vec4 final_colors;

    uniform sampler2D sprite_texture;

    void main()
    {
        final_colors = texture(sprite_texture, texture_coords.xy) * vertex_colors;
        
        // No GL_ALPHA_TEST in core, use shader to discard.
        if(final_colors.a < 0.01){
            discard;
        }
    }
"""

class SpriteNode(PositionNode):
    def __init__(
        self,
        resource: Union[pyglet.image.TextureRegion, pyglet.image.animation.Animation],
        sprites_manager: Optional[SpritesManager] = None,
        on_animation_end = None,
        x: int = 0,
        y: int = 0,
        z: Optional[int] = None,
        scaling: int = 1,
        group: Optional[pyglet.graphics.Group] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = z if z is not None else y
        )

        self.__sprites_manager = sprites_manager
        self.__scaling = scaling
        # vertex_source = """
        #     #version 150 core
        #     in vec2 position;
        #     in vec4 color;
        #     out vec4 vertex_color;

        #     uniform mat4 projection;

        #     void main() {
        #         gl_Position = projection * vec4(position, 0.0, 1.0);
        #         vertex_color = color;
        #     }
        # """

        # fragment_source = """
        #     #version 150 core
        #     in vec4 vertex_color;
        #     in vec3 texture_coords;
        #     out vec4 final_color;

        #     uniform sampler2D sprite_texture;

        #     void main() {
        #         final_color = texture(sprite_texture, texture_coords.xy) * vertex_color;
        #         if (final_color.a == 0) discard;
        #     }
        # """
        vert_shader = pyglet.graphics.shader.Shader(pyglet.sprite.vertex_source, "vertex")
        frag_shader = pyglet.graphics.shader.Shader(fragment_source, "fragment")
        shader_program = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

        self.sprite = DepthSprite(
            img = resource,
            x = x * scaling,
            y = y * scaling,
            z = int(-z if z is not None else -y),
            group = group,
            program = shader_program
        )
        self.sprite.scale = scaling
        self.sprite.push_handlers(self)

        self.__z_label = pyglet.text.Label(
            text = str(self.z),
            color = (0x00, 0x00, 0x00, 0xFF),
            x = x * scaling + 5,
            y = y * scaling + 5
        )

        if self.__sprites_manager is not None:
            self.__sprites_manager.add_sprite(self.sprite)
            self.__sprites_manager.add_sprite(self.__z_label)

        self.__on_animation_end = on_animation_end

    def delete(self) -> None:
        self.sprite.delete()

    def get_image(self):
        return self.sprite.image

    def set_position(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None
    ) -> None:
        if x is not None:
            self.x = x
            # self.__sprite.x = x * self.__scaling
            self.__z_label.x = x * self.__scaling + 5

        if y is not None:
            self.y = y
            # self.__sprite.y = y * self.__scaling
            self.z = y
            # self.__sprite.z = y
            self.__z_label.y = y * self.__scaling + 5

        self.sprite.position = (
            self.x * self.__scaling,
            self.y * self.__scaling,
            int(-self.z)
        )

    def set_scale(
        self,
        x_scale: Optional[int] = None,
        y_scale: Optional[int] = None
    ) -> None:
        if x_scale is not None:
            self.sprite.scale_x = x_scale

        if y_scale is not None:
            self.sprite.scale_y = y_scale

    def set_image(self, image) -> None:
        if image != None and (self.sprite.image != image or (self.sprite.image != None and self.sprite.frame_index >= len(self.sprite.image.frames) - 1)):
            self.sprite.image = image

    def on_animation_end(self):
        if self.__on_animation_end:
            self.__on_animation_end()

    def draw(self) -> None:
        self.sprite.draw()
        self.__z_label.draw()

    def update(self, dt) -> None:
        self.__z_label.text = f"{self.sprite.z}"
        self.__z_label.x = self.x * self.__scaling + 5
        self.__z_label.y = self.y * self.__scaling + 5

    def get_bounding_box(self):
        if isinstance(self.sprite.image, pyglet.image.TextureRegion):
            return (
                self.sprite.x - self.sprite.image.anchor_x * self.__scaling,
                self.sprite.y - self.sprite.image.anchor_y * self.__scaling,
                self.sprite.width,
                self.sprite.height
            )
        elif isinstance(self.sprite.image, pyglet.image.animation.Animation):
            return (
                self.sprite.x - self.sprite.image.frames[0].image.anchor_x * self.__scaling,
                self.sprite.y - self.sprite.image.frames[0].image.anchor_y * self.__scaling,
                self.sprite.width,
                self.sprite.height
            )

        return super().get_bounding_box()