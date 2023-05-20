from typing import Dict, Optional
import pyglet
import pyglet.gl as gl

FRAGMENT_SOURCE = """
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
frag_shader = pyglet.graphics.shader.Shader(FRAGMENT_SOURCE, "fragment")
depth_shader_program = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

class DepthSpriteGroup(pyglet.sprite.SpriteGroup):
    def __init__(
        self,
        texture,
        blend_src,
        blend_dest,
        program,
        parent = None,
        samplers_2d: Optional[Dict[str, pyglet.image.ImageData]] = None
    ):
        super().__init__(texture, blend_src, blend_dest, program, parent)
        self.texture = texture
        self.blend_src = blend_src
        self.blend_dest = blend_dest
        self.program = program
        self.samplers_2d = samplers_2d

    def set_state(self):
        self.program.use()

        # Set sampler uniforms.
        if self.samplers_2d is not None:
            for uniform_name in self.program.uniforms:
                # Fetch current uniform.
                uniform = self.program.uniforms[uniform_name]

                # Only check for sampler2D uniforms.
                if uniform.type == gl.GL_SAMPLER_2D and uniform.name in self.samplers_2d.keys():
                    # Generate textures.
                    textures = [0] * 1
                    textures_ctype = (gl.GLuint * len(textures))(*textures)
                    gl.glGenTextures(1, textures_ctype)

                    # Prepare the texture to be read by the shader.
                    image = self.samplers_2d[uniform_name]
                    width, height = image.width, image.height
                    image_data = image.get_data('RGB', width * 3)

                    # Pass the generated texture to GPU memory.
                    gl.glActiveTexture(gl.GL_TEXTURE1)
                    gl.glEnable(gl.GL_TEXTURE_2D)
                    gl.glBindTexture(gl.GL_TEXTURE_2D, textures_ctype[0])
                    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width, height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, image_data)

                    # Make sure the texture is properly set up.
                    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
                    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
                    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
                    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
                    self.program["palette"] = 1

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(self.texture.target, self.texture.id)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(self.blend_src, self.blend_dest)

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LESS)

    def unset_state(self):
        # if "palette" in self.program.uniforms:
        #     gl.glActiveTexture(gl.GL_TEXTURE1)
        #     gl.glDisable(gl.GL_TEXTURE_2D)
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
        samplers_2d: Optional[Dict[str, pyglet.image.ImageData]] = None
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

        self.samplers_2d = samplers_2d

        # Replace group with a new one that has samplers.
        self.group = self.group_class(
            texture = self._texture,
            blend_src = blend_src,
            blend_dest = blend_dest,
            program = self.program,
            parent = group,
            samplers_2d = samplers_2d
        )

    def get_frames_num(self) -> int:
        """
        Returns the amount of frames in the current animation.
        Always returns 0 if the sprite image is not an animation.
        """

        return len(self._animation.frames) if self._animation is not None else 0

    def get_frame_index(self) -> int:
        """
        Returns the current animation frame.
        Always returns 0 if the sprite image is not an animation.
        """

        return self.frame_index

    @property
    def group(self):
        """Parent graphics group.

        The sprite can change its rendering group, however this can be an
        expensive operation.

        :type: :py:class:`pyglet.graphics.Group`
        """
        return self._group.parent

    @group.setter
    def group(self, group):
        if self._group.parent == group:
            return
        self._group = self.group_class(
            texture = self._texture,
            blend_src = self._group.blend_src,
            blend_dest = self._group.blend_dest,
            program = self._group.program,
            parent = group,
            samplers_2d = self.samplers_2d
        )
        self._batch.migrate(self._vertex_list, gl.GL_TRIANGLES, self._group, self._batch)

    # This method is overridden because the group needs to have all samplers by the time it draws to screen.
    def _set_texture(self, texture):
        if texture.id is not self._texture.id:
            self._group = self._group.__class__(
                texture = texture,
                blend_src = self._group.blend_src,
                blend_dest = self._group.blend_dest,
                program = self._group.program,
                parent = self._group.parent,
                samplers_2d = self.samplers_2d
            )
            self._vertex_list.delete()
            self._texture = texture
            self._create_vertex_list()
        else:
            self._vertex_list.tex_coords[:] = texture.tex_coords
        self._texture = texture

    @property
    def program(self):
        return self._program

    @program.setter
    def program(self, program):
        if self._program == program:
            return
        self._group = self.group_class(
            texture = self._texture,
            blend_src = self._group.blend_src,
            blend_dest = self._group.blend_dest,
            program = program,
            parent = self._group,
            samplers_2d = self.samplers_2d
        )
        self._batch.migrate(self._vertex_list, gl.GL_TRIANGLES, self._group, self._batch)
        self._program = program