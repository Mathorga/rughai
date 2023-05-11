from typing import Dict, Optional
import pyglet
import pyglet.gl as gl

fragment_source = """
    #version 150 core
    in vec4 vertex_colors;
    in vec3 texture_coords;
    out vec4 final_color;

    uniform sampler2D sprite_texture;

    void main() {
        final_color = texture(sprite_texture, texture_coords.xy) * vertex_colors;

        // Inverted colors.
        //final_color = vec4(1.0 - final_color.r, 1.0 - final_color.g, 1.0 - final_color.b, final_color.a);

        // Rotated channels.
        //final_color = vec4(final_color.g, final_color.b, final_color.r, final_color.a);

        // No GL_ALPHA_TEST in core, use shader to discard.
        if (final_color.a < 0.01) {
            discard;
        }
    }
"""
vert_shader = pyglet.graphics.shader.Shader(pyglet.sprite.vertex_source, "vertex")
frag_shader = pyglet.graphics.shader.Shader(fragment_source, "fragment")
depth_shader_program = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

class DepthSpriteGroup(pyglet.sprite.SpriteGroup):
    def __init__(
        self,
        texture,
        blend_src,
        blend_dest,
        program,
        parent = None,
        samplers_2d: Dict[str, pyglet.image.TextureRegion] = {}
    ):
        super().__init__(texture, blend_src, blend_dest, program, parent)
        self.texture = texture
        self.blend_src = blend_src
        self.blend_dest = blend_dest
        self.program = program
        self.samplers_2d = samplers_2d

    def set_state(self):
        self.program.use()

        for uniform_name in self.program.uniforms:
            # Fetch current uniform.
            uniform = self.program.uniforms[uniform_name]

            # Only check for sampler2D uniforms.
            if uniform.type == gl.GL_SAMPLER_2D and uniform.name in self.samplers_2d.keys():
                gl.glActiveTexture(gl.GL_TEXTURE0 + uniform.location)
                if uniform.name == "palette":
                    print(self.samplers_2d[uniform.name])
                gl.glBindTexture(self.samplers_2d[uniform.name].target, self.samplers_2d[uniform.name].id)

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
        blend_src: int = gl.GL_SRC_ALPHA,
        blend_dest: int = gl.GL_ONE_MINUS_SRC_ALPHA,
        batch: Optional[pyglet.graphics.Batch] = None,
        group: Optional[pyglet.graphics.Group] = None,
        subpixel: bool = False,
        program: Optional[pyglet.graphics.shader.ShaderProgram] = None,
        samplers_2d: Dict[str, pyglet.image.TextureRegion] = {}
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

        # Replace group with a new one that has samplers.
        if "palette" in samplers_2d.keys():
            print(samplers_2d)
        self._group = self.group_class(
            texture = self._texture,
            blend_src = blend_src,
            blend_dest = blend_dest,
            program = self.program,
            parent = group,
            samplers_2d = samplers_2d
        )