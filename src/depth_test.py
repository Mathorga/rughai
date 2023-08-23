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

z_flipped: bool = False

im1 = pg.image.load(
    'assets/sprites/prop/rughai/tree_l.png')
sprite1 = pg.sprite.Sprite(im1, x=100, y=100, z=105, batch=batch)
im2 = pg.image.load(
    'assets/sprites/prop/rughai/tree_l.png')
sprite2 = pg.sprite.Sprite(im2, x=105, y=105, z=100, batch=batch)

@window.event
def on_draw():
    window.clear()
    batch.draw()

@window.event
def on_key_press(symbol, modifiers):
    global z_flipped
    global sprite1
    global sprite2

    if symbol == pyglet.window.key.SPACE:
        z_flipped = not z_flipped
        sprite1.z = 10 if z_flipped else 0
        sprite2.z = 0 if z_flipped else 10

pg.app.run()