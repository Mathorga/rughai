import pyglet
import pyglet.gl as gl

fragment_source = """
    #version 150 core
    in vec4 vertex_colors;
    in vec3 texture_coords;
    out vec4 final_colors;

    uniform sampler2D sprite_texture;

    void main() {
        final_colors = texture(sprite_texture, texture_coords.xy) * vertex_colors;

        // No GL_ALPHA_TEST in core, use shader to discard.
        if (final_colors.a < 0.01) {
            discard;
        }
    }
"""
vert_shader = pyglet.graphics.shader.Shader(pyglet.sprite.vertex_source, "vertex")
frag_shader = pyglet.graphics.shader.Shader(fragment_source, "fragment")
depth_shader_program = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

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

    def __init__(
        self,
        img,
        x = 0,
        y = 0,
        z = 0,
        blend_src = gl.GL_SRC_ALPHA,
        blend_dest = gl.GL_ONE_MINUS_SRC_ALPHA,
        batch = None,
        group = None,
        subpixel = False,
        program = None
    ):
        super().__init__(
            img,
            x,
            y,
            z,
            blend_src,
            blend_dest,
            batch,
            group,
            subpixel,
            # program
            program if program is not None else depth_shader_program
        )