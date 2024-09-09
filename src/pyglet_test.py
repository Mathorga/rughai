import pyglet
from pyglet.window import key
from pyglet.graphics.shader import Shader, ShaderProgram
import pyglet.gl as gl
import pyglet.math as pm

import old_settings
from amonite.camera import Camera
from amonite.upscaler import UpscalerOld

pyglet.resource.path = ["../assets"]
pyglet.resource.reindex()

config = gl.Config()

# Create a new window.
window = pyglet.window.Window(
    old_settings.VIEW_WIDTH * 3 if not old_settings.FULLSCREEN else None,
    old_settings.VIEW_HEIGHT * 3 if not old_settings.FULLSCREEN else None,
    old_settings.TITLE,
    fullscreen = old_settings.FULLSCREEN,
    resizable = True
)
window.set_minimum_size(old_settings.VIEW_WIDTH, old_settings.VIEW_HEIGHT)

fr = UpscalerOld(
    window,
    width = old_settings.VIEW_WIDTH,
    height = old_settings.VIEW_HEIGHT
)

fps_display = pyglet.window.FPSDisplay(window)

world_camera = Camera(
    window = window
)

# Create a test label.
# font_size = 12
# title = pyglet.text.Label(
#     settings.TITLE,
#     # font_name = "Comic Sans MS",
#     font_size = font_size,
#     x = 0,
#     y = settings.VIEW_HEIGHT + font_size // 2,
#     anchor_x = "left",
#     anchor_y = "top"
# )

# background = pyglet.shapes.Rectangle(
#     x = 0,
#     y = 0,
#     width = settings.VIEW_WIDTH,
#     height = settings.VIEW_HEIGHT,
#     color = (60, 60, 60)
# )

# circle_1 = pyglet.shapes.Circle(
#     x = 100,
#     y = 150,
#     radius = 100,
#     color = (50, 225, 30)
# )
# circle_1.opacity = 120
# circle_1.anchor_x = 10
# circle_1.anchor_y = 10

# circle_2 = pyglet.shapes.Circle(
#     x = -50,
#     y = 100,
#     radius = 100,
#     color = (225, 50, 30)
# )
# circle_2.opacity = 120
# circle_2.anchor_x = 10
# circle_2.anchor_y = 10

# cam_line = pyglet.shapes.Line(
#     x = 0,
#     y = 0,
#     x2 = 0,
#     y2 = 0,
#     width = 1
# )
# cam_line.opacity = 100

# speed_line = pyglet.shapes.Line(
#     x = 0,
#     y = 0,
#     x2 = 0,
#     y2 = 0,
#     width = 1,
#     color = (200, 100, 80)
# )
# speed_line.opacity = 100

vertex_source = """#version 150 core
    in vec3 translate;
    in vec4 colors;
    in vec3 tex_coords;
    in vec2 scale;
    in vec3 position;
    in float rotation;

    out vec4 vertex_colors;
    out vec3 texture_coords;

    uniform WindowBlock
    {
        mat4 projection;
        mat4 view;
    } window;

    mat4 m_scale = mat4(1.0);
    mat4 m_rotation = mat4(1.0);
    mat4 m_translate = mat4(1.0);

    void main()
    {
        m_scale[0][0] = scale.x;
        m_scale[1][1] = scale.y;
        m_translate[3][0] = translate.x;
        m_translate[3][1] = translate.y;
        m_translate[3][2] = translate.z;
        m_rotation[0][0] =  cos(-radians(rotation)); 
        m_rotation[0][1] =  sin(-radians(rotation));
        m_rotation[1][0] = -sin(-radians(rotation));
        m_rotation[1][1] =  cos(-radians(rotation));

        gl_Position = window.projection * window.view * m_translate * m_rotation * m_scale * vec4(position, 1.0);

        vertex_colors = colors;
        texture_coords = tex_coords;
    }
"""

fragment_source = """#version 150 core
    in vec4 vertex_colors;
    in vec3 texture_coords;
    out vec4 final_colors;

    uniform sampler2D sprite_texture;

    void main()
    {
        final_colors = texture(sprite_texture, texture_coords.xy) * vertex_colors * 0.4;
    }
"""

vert_shader = Shader(vertex_source, 'vertex')
frag_shader = Shader(fragment_source, 'fragment')
program = ShaderProgram(vert_shader, frag_shader)

anim = pyglet.resource.image("sprites/iryo/iryo.png")
# for frame in anim.frames:
#     frame.image.anchor_x = anim.get_max_width() / 2
#     frame.image.anchor_y = 0

batch = pyglet.graphics.Batch()
group = pyglet.graphics.Group()

sprite = pyglet.sprite.AdvancedSprite(
    img = anim,
    # z = 10,
    # batch = batch,
    # group = group,
    program = program
)

# sprite.program = program

sprite2 = pyglet.sprite.Sprite(
    img = anim,
    # z = 10,
    # batch = batch,
    # group = group
)
max_speed = 100
speed = 0
accel = 10
dir = 0

world_camera.position = (
    sprite.x - old_settings.VIEW_WIDTH / 2,
    sprite.y - old_settings.VIEW_HEIGHT / 2
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
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    with fr:
        # background.draw()
        with world_camera:
            # batch.draw()
            anim.blit(sprite.x + 20, sprite.y + 20, sprite.z)
            sprite.draw()
            sprite2.draw()
            # circle_1.draw()
            # circle_2.draw()
            # cam_line.draw()
            # speed_line.draw()

        # title.draw()

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
    sprite.update(x = sprite.x + movement.x, y = sprite.y + movement.y, z = 0.1)
    # sprite2.update(x = sprite2.x, y = sprite2.y, z = 0.5)
    sprite.image.z = 0.5
    sprite2.image.z = 0.8
    print(sprite.z, sprite2.z)
    # sprite.x += movement.x
    # sprite.y += movement.y

    camera_movement = pm.Vec2(
        (sprite.x - old_settings.VIEW_WIDTH / 2 - world_camera.position[0]) * cam_speed * dt,
        (sprite.y - old_settings.VIEW_HEIGHT / 2 - world_camera.position[1]) * cam_speed * dt
    )
    world_camera.position = (
        world_camera.position[0] + camera_movement.x,
        world_camera.position[1] + camera_movement.y
    )
    # cam_line.x = world_camera.position[0] + settings.VIEW_WIDTH / 2
    # cam_line.y = world_camera.position[1] + settings.VIEW_HEIGHT / 2
    # cam_line.x2 = sprite.x
    # cam_line.y2 = sprite.y

    # speed_line.x = sprite.x
    # speed_line.y = sprite.y
    # speed_line.x2 = sprite.x + movement.x * 10
    # speed_line.y2 = sprite.y + movement.y * 10

@window.event
def on_key_press(symbol, modifiers):
    keys[symbol] = True

@window.event
def on_key_release(symbol, modifiers):
    keys[symbol] = False

if __name__ == '__main__':
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LESS)
    # gl.glEnable(gl.GL_BLEND)
    # gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    # Scale textures using nearest neighbor filtering.
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

    pyglet.clock.schedule_interval(update, 1.0 / old_settings.TARGET_FPS)
    pyglet.app.run()