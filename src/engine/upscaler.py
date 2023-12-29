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

import pyglet

from engine.settings import GLOBALS, Keys

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