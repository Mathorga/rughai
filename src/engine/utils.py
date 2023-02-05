def center_anim(anim):
    for frame in anim.frames:
        frame.image.anchor_x = anim.get_max_width() / 2
        frame.image.anchor_y = 0

def scale_anim(anim, scale: float):
    for frame in anim.frames:
        frame.image.scale = scale

def set_anim_duration(anim, duration: float):
    for frame in anim.frames:
        frame.duration = duration