import pyglet

def animation_set_anchor(
    animation: pyglet.image.animation.Animation,
    x: int,
    y: int
):
    for frame in animation.frames:
        frame.image.anchor_x = x
        frame.image.anchor_y = y

def center_anim(anim: pyglet.image.animation.Animation):
    for frame in anim.frames:
        frame.image.anchor_x = anim.get_max_width() / 2
        frame.image.anchor_y = 0

def scale_anim(anim: pyglet.image.animation.Animation, scale: float):
    for frame in anim.frames:
        frame.image.scale = scale

def set_anim_duration(anim: pyglet.image.animation.Animation, duration: float):
    for frame in anim.frames:
        frame.duration = duration

def remap(x, x_min, x_max, y_min, y_max):
    return y_min + ((x- x_min) * (y_max-y_min))/ (x_max-x_min)

def overlap(x1, y1, w1, h1, x2, y2, w2, h2):
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and h1 + y1 > y2

def distance(x1, y1, w1, h1, x2, y2, w2, h2):
    return (
        abs(x1 - x2) - ((w1 + w2) / 2),
        abs(y1 - y2) - ((h1 + h2) / 2)
    )
