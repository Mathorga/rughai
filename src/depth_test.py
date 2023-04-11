import os
import pyglet as pg
from pyglet.gl import *

# Set resources path.
pyglet.resource.path = [f"{os.path.dirname(__file__)}/../assets"]
pyglet.resource.reindex()

window = pg.window.Window(width=320, height=320)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
batch = pg.graphics.Batch()

im1 = pg.image.load(
    'assets/sprites/rughai/iryo/iryo.png')
sprite1 = pg.sprite.Sprite(im1, x=100, y=100, z=1, batch=batch)
im2 = pg.image.load(
    'assets/sprites/rughai/iryo/iryo.png')
sprite2 = pg.sprite.Sprite(im2, x=105, y=105, z=0, batch=batch)

@window.event
def on_draw():
    window.clear()
    batch.draw()

pg.app.run()