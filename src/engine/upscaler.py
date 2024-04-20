#!/usr/bin/env python
# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# Copyright (c) 2008-2022 pyglet contributors
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
"""
Demonstrates one way of fixing the display resolution to a certain
size, but rendering to the full screen.

The method used in this example is:

1. Create a Framebuffer object, and a Texture of the desired resolution
2. Attach the Texture to the Framebuffer.
2. Bind the Framebuffer as the current render target.
3. Render the scene using any OpenGL functions (here, just a shape).
4. Unbind the Framebuffer, and blit the Texture scaled to fill the screen.
"""

from ctypes import byref
import pyglet
import pyglet.gl as gl

from engine.settings import GLOBALS, Keys
from engine.utils.utils import set_texture_filter

class Upscaler:
    def __init__(
        self,
        window: pyglet.window.Window,
        width: int,
        height: int
    ):
        self.window: pyglet.window.Window = window
        self.width: int = width
        self.height: int = height

        # On retina Macs everything is rendered 4x-zoomed for some reason. compensate for this using a platform scaling.
        self.platform_scaling: float = 0.25 if "macOS" in GLOBALS[Keys.PLATFORM] else 1.0

        self._target_area = (0, 0, 0, 0, 0)
        self._aspect = (0, 0)

        self.window.push_handlers(self)

    def on_resize(self, _width, _height):
        self._aspect = self.__calculate_aspect(*self.window.get_framebuffer_size())
        self._target_area = self.__calculate_area(*self.window.get_framebuffer_size())

    def __calculate_aspect(self, new_screen_width, new_screen_height):
        aspect_ratio = self.width / self.height
        aspect_width = new_screen_width
        aspect_height = (aspect_width / aspect_ratio) + 0.5

        if aspect_height > new_screen_height:
            aspect_height = new_screen_height
            aspect_width = (aspect_height * aspect_ratio) + 0.5

        return (aspect_width, aspect_height)

    def __calculate_area(self, new_screen_width, new_screen_height):
        return (
            # X.
            int((new_screen_width / 2) - (self._aspect[0] / 2)),
            # Y.
            int((new_screen_height / 2) - (self._aspect[1] / 2)),
            # Width.
            int(self._aspect[0]),
            # Height.
            int(self._aspect[1])
        )

    def __enter__(self):
        framebuffer_size = self.window.get_framebuffer_size()
        self.window.view = pyglet.math.Mat4.from_scale(pyglet.math.Vec3(
            framebuffer_size[0] / self.width * self.platform_scaling,
            framebuffer_size[1] / self.height * self.platform_scaling,
            1.0
        ))
        self.window.viewport = self._target_area

    def __exit__(self, *params):
        pass

    def begin(self):
        self.__enter__()

    def end(self):
        self.__exit__()

class TrueUpscaler:
    def __init__(
        self,
        window: pyglet.window.Window,
        width: int,
        height: int
    ) -> None:
        self.window: pyglet.window.Window = window
        self.width: int = width
        self.height: int = height

        # # Generate a texture to render to.
        # image: pyglet.image.ImageData = pyglet.image.create(width = width, height = height)
        # self.texture: pyglet.image.Texture = image.get_texture()

        # Generate a framebuffer to render to.
        self.framebuffer_id = gl.GLuint()
        gl.glGenFramebuffers(1, byref(self.framebuffer_id))
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.framebuffer_id)

        # Generate a texture to attach to the framebuffer.
        # self.texture_id = gl.GLuint()
        self.texture = pyglet.image.create(width = width, height = height).get_texture()
        # gl.glGenTextures(1, byref(self.texture.id))
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture.id)
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,
            0,
            gl.GL_RGB,
            window.width,
            window.height,
            0,
            gl.GL_RGB,
            gl.GL_UNSIGNED_BYTE,
            None
        )

        # Bind the framebuffer to the destination texture.
        # gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture.id)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, self.texture.id, 0)
        # set_texture_filter(texture = self.texture, filter = gl.GL_NEAREST)

        if gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE:
            print("ERROR: framebuffer is not complete")
            exit(1)

        # Setup the depth buffer.
        self.depthbuffer_id = gl.GLuint()
        gl.glGenRenderbuffers(1, byref(self.depthbuffer_id))
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.depthbuffer_id)
        gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH_COMPONENT, window.width, window.height)

        # Bind the generated depthbuffer to the framebuffer.
        gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT, gl.GL_RENDERBUFFER, self.depthbuffer_id)

        # self.vertices = [
        #     0, 0,
        #     window.width, 0,
        #     window.width, window.height,
        #     0, window.height
        # ]
        # self.tex_coords = [0, 0, 1, 0, 1, 1, 0, 1]
        # self.indices = [0, 1, 2, 0, 2, 3]
        # self.vertex_list = pyglet.graphics.()

    def __enter__(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.framebuffer_id)
        gl.glEnable(gl.GL_DEPTH_TEST)

        # Clear the framebuffer from depth data.
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    def __exit__(self, *params):
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        # self.window.clear()
        self.texture.blit(
            x = 0,
            y = 0,
            width = self.window.width,
            height = self.window.height
        )

    # def render(self) -> None:
    #     gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture.id)
    #     gl.glEnable(gl.GL_TEXTURE_2D)

    #     gl.glEnableCl