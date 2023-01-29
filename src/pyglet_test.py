import pyglet
from pyglet.window import key
import pyglet.gl as gl
import pyglet.math as pm

import settings
from camera import Camera
from fixed_resolution import FixedResolution

pyglet.resource.path = ["../assets"]
pyglet.resource.reindex()

config = gl.Config()

# Create a new window.
window = pyglet.window.Window(
    settings.VIEW_WIDTH * 3 if not settings.FULLSCREEN else None,
    settings.VIEW_HEIGHT * 3 if not settings.FULLSCREEN else None,
    settings.TITLE,
    fullscreen = settings.FULLSCREEN,
    resizable = True
)
window.set_minimum_size(settings.VIEW_WIDTH, settings.VIEW_HEIGHT)

fr = FixedResolution(
    window,
    width = settings.VIEW_WIDTH,
    height = settings.VIEW_HEIGHT
)

fps_display = pyglet.window.FPSDisplay(window)

world_camera = Camera(
    window = window
)

# Create a test label.
font_size = 12.0
title = pyglet.text.Label(
    settings.TITLE,
    # font_name = "Comic Sans MS",
    font_size = font_size,
    x = 0,
    y = settings.VIEW_HEIGHT + font_size / 2,
    anchor_x = "left",
    anchor_y = "top"
)

background = pyglet.shapes.Rectangle(
    x = 0,
    y = 0,
    width = settings.VIEW_WIDTH,
    height = settings.VIEW_HEIGHT,
    color = (60, 60, 60)
)

circle_1 = pyglet.shapes.Circle(
    x = 100,
    y = 150,
    radius = 100,
    color = (50, 225, 30)
)
circle_1.opacity = 120
circle_1.anchor_x = 10
circle_1.anchor_y = 10

circle_2 = pyglet.shapes.Circle(
    x = -50,
    y = 100,
    radius = 100,
    color = (225, 50, 30)
)
circle_2.opacity = 120
circle_2.anchor_x = 10
circle_2.anchor_y = 10

cam_line = pyglet.shapes.Line(
    x = 0,
    y = 0,
    x2 = 0,
    y2 = 0,
    width = 1
)
cam_line.opacity = 100

speed_line = pyglet.shapes.Line(
    x = 0,
    y = 0,
    x2 = 0,
    y2 = 0,
    width = 1,
    color = (200, 100, 80)
)
speed_line.opacity = 100

image = pyglet.resource.image("sprites/rughai/iryo/iryo.png")
anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_run.gif")
image.anchor_x = image.width / 2
image.anchor_y = 0
for frame in anim.frames:
    frame.image.anchor_x = anim.get_max_width() / 2
    frame.image.anchor_y = 0

sprite = pyglet.sprite.Sprite(
    img = anim
)
max_speed = 100
speed = 0
accel = 10
dir = 0

world_camera.position = (
    sprite.x - settings.VIEW_WIDTH / 2,
    sprite.y - settings.VIEW_HEIGHT / 2
)
cam_speed = 8

keys = {
    key.W: False,
    key.A: False,
    key.S: False,
    key.D: False,
}

@window.event
def on_draw():
    window.clear()

    with fr:
        background.draw()
        with world_camera:
            sprite.draw()
            circle_1.draw()
            circle_2.draw()
            cam_line.draw()
            speed_line.draw()

        title.draw()

    fps_display.draw()

def update(dt):
    global speed
    global accel
    global dir
    move_input = pyglet.math.Vec2(keys[key.D] - keys[key.A], keys[key.W] - keys[key.S]).normalize()
    movement_base = pm.Vec2.from_polar(1.0, dir)
    if move_input.mag > 0.5:
        dir = move_input.heading
        speed += accel
        if speed >= max_speed:
            speed = max_speed
    else:
        speed -= accel
        if speed <= 0:
            speed = 0
    movement = movement_base.from_magnitude(speed * dt)
    sprite.x += movement.x
    sprite.y += movement.y

    camera_movement = pm.Vec2(
        (sprite.x - settings.VIEW_WIDTH / 2 - world_camera.position[0]) * cam_speed * dt,
        (sprite.y - settings.VIEW_HEIGHT / 2 - world_camera.position[1]) * cam_speed * dt
    )
    world_camera.position = (
        world_camera.position[0] + camera_movement.x,
        world_camera.position[1] + camera_movement.y
    )
    cam_line.x = world_camera.position[0] + settings.VIEW_WIDTH / 2
    cam_line.y = world_camera.position[1] + settings.VIEW_HEIGHT / 2
    cam_line.x2 = sprite.x
    cam_line.y2 = sprite.y

    speed_line.x = sprite.x
    speed_line.y = sprite.y
    speed_line.x2 = sprite.x + movement.x * 10
    speed_line.y2 = sprite.y + movement.y * 10

@window.event
def on_key_press(symbol, modifiers):
    keys[symbol] = True

@window.event
def on_key_release(symbol, modifiers):
    keys[symbol] = False

if __name__ == '__main__':
    # Scale textures using nearest neighbor filtering.
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

    pyglet.clock.schedule_interval(update, 1.0 / settings.TARGET_FPS)
    pyglet.app.run()