from typing import Optional, Tuple
import math
import pyglet
import pyglet.math as pm

def animation_set_anchor(
    animation: pyglet.image.animation.Animation,
    x: float,
    y: float
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

def rect_rect_collide(x1, y1, w1, h1, x2, y2, w2, h2) -> bool:
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and h1 + y1 > y2

def collision_ray_rect(
    ray_origin_x,
    ray_origin_y,
    ray_end_x,
    ray_end_y,
    rect_x,
    rect_y,
    rect_w,
    rect_h
) -> Optional[Tuple[float, float, float, float, float]]:
        # calculate the direction ray
        ray_direction_x = ray_end_x - ray_origin_x
        ray_direction_y = ray_end_y - ray_origin_y

        # calculate the near and far t values for x and y
        # ADD FIX FOR PARALLEL VECTORS (DIVISION BY 0)
        if ray_direction_x == 0:
            ray_direction_x = 0.01

        if ray_direction_y == 0:
            ray_direction_y = 0.01

        # calculate the near and far collision "times" on the x and y axis
        near_x_t = (rect_x - ray_origin_x) / ray_direction_x
        far_x_t = (rect_x + rect_w - ray_origin_x) / ray_direction_x

        near_y_t = (rect_y + rect_h- ray_origin_y) / ray_direction_y
        far_y_t = (rect_y - ray_origin_y) / ray_direction_y

        # swap the near and far values in case they don't make sense
        if near_x_t > far_x_t:
            tmp = near_x_t
            near_x_t = far_x_t
            far_x_t = tmp

        if near_y_t > far_y_t:
            tmp = near_y_t
            near_y_t = far_y_t
            far_y_t = tmp

        # condition for the ray to not collide with the rectangle
        if near_x_t > far_y_t or near_y_t > far_x_t:
            return None

        # calculating the near and far hit t
        hit_near_t = max(near_x_t, near_y_t)
        hit_far_t = min(far_x_t, far_y_t)

        # case in which the collision happens behind the vector and past the vector
        if hit_far_t < 0 or hit_near_t > 1 or hit_near_t < 0:
            return None

        # collision detected

        # calculate the contact point
        contact_point_x = ray_origin_x + ray_direction_x * hit_near_t
        contact_point_y = ray_origin_y + ray_direction_y * hit_near_t

        contact_normal_x = 0
        contact_normal_y = 0

        # calculate the normal vector of the contact
        if near_x_t > near_y_t:
            if ray_direction_x < 0:
                contact_normal_x = 1
                contact_normal_y = 0
            else:
                contact_normal_x = -1
                contact_normal_y = 0
        elif near_x_t < near_y_t:
            if ray_direction_y < 0:
                contact_normal_x = 0
                contact_normal_y = 1
            else:
                contact_normal_x = 0
                contact_normal_y = -1

        return (contact_point_x, contact_point_y, contact_normal_x, contact_normal_y, hit_near_t)

def collision_dynamic_rect_rect(
    x1: float,
    y1: float,
    w1: float,
    h1: float,
    velocity_x: float,
    velocity_y: float,
    x2: float,
    y2: float,
    w2: float,
    h2: float
) -> Optional[Tuple[float, float, float, float, float]]:
        # if the dynamic rectangle is not moving, there is no collision
        if velocity_x == 0.0 and velocity_y == 0.0:
            return None

        # expand the target rectangle to make the borders of the dynamic rectangle match with the borders of the stationary rectangle
        expanded_target_x = x2 - w1 / 2
        expanded_target_y = y2 - h1 / 2

        expanded_target_w = w2 + w1
        expanded_target_h = h2 + h1

        # calculate the collision of the ray that goes from the center of the dynamic rectangle with the direction and module of the rectangle speed and the stationary rectangle
        collision_result = collision_ray_rect(
            x1 + w1 / 2,
            y1 + h1 / 2,
            x1 + w1 / 2 + velocity_x,
            y1 + h1 / 2 + velocity_y,
            expanded_target_x,
            expanded_target_y,
            expanded_target_w,
            expanded_target_h
        )

        # if there was a collision
        if collision_result is not None:
            # return it
            return collision_result

def rect_rect_min_dist(
    x1: float,
    y1: float,
    w1: float,
    h1: float,
    x2: float,
    y2: float,
    w2: float,
    h2: float
) -> float:
    """
    Computes the minimum distance between two AABBs.
    """
    rect_outer = (
        min(x1, x2),
        min(y1, y2),
        max(x1 + w1, x2 + w2),
        max(y1 + h1, y2 + h2)
    )
    inner_width = rect_outer[2] - rect_outer[0] - w1 - w2
    inner_height = rect_outer[3] - rect_outer[1] - h1 - h2

    return math.sqrt(inner_width ** 2 + inner_height ** 2)

def clamp(src, min, max):
    if src < min:
        return min
    elif src > max:
        return max
    else:
        return src

def rect_rect_check(
    x1: float,
    y1: float,
    w1: float,
    h1: float,
    x2: float,
    y2: float,
    w2: float,
    h2: float
) -> bool:
    """
    Checks whether two AABBs are overlapping or not.
    """

    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and h1 + y1 > y2

def circle_circle_check(
    x1: float,
    y1: float,
    r1: float,
    x2: float,
    y2: float,
    r2: float
) -> bool:
    """
    Checks whether two circles are overlapping or not.
    """

    # Compare the square distance with the sum of the radii.
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) < (r1 + r2) ** 2

def circle_rect_check(
    x1: float,
    y1: float,
    r1: float,
    x2: float,
    y2: float,
    w2: float,
    h2: float
) -> bool:
    nearest_x = clamp(x1, x2, x2 + w2)
    nearest_y = clamp(y1, y2, y2 + h2)

    dx = x1 - nearest_x
    dy = y1 - nearest_y

    return (dx ** 2 + dy ** 2) < r1 ** 2

def rect_rect_solve(
    x1: float,
    y1: float,
    w1: float,
    h1: float,
    x2: float,
    y2: float,
    w2: float,
    h2: float
) -> Tuple[float, float]:
    """
    Computes the reaction vector for collisions between two AABBs.

    This function should be only called when a collision occurs, since it always returns a valid vector,
    even if there's no collision at all
    """

    # X component.
    delta1_x = (x2 + w2) - x1
    delta2_x = x2 - (x1 + w1)
    delta_x = 0
    if abs(delta1_x) <= abs(delta2_x):
        delta_x = delta1_x
    else:
        delta_x = delta2_x

    # Y component.
    delta1_y = (y2 + h2) - y1
    delta2_y = y2 - (y1 + h1)
    delta_y = 0
    if abs(delta1_y) <= abs(delta2_y):
        delta_y = delta1_y
    else:
        delta_y = delta2_y

    if abs(delta_x) <= abs(delta_y):
        return (delta_x, 0)
    else:
        return (0, delta_y)

def circle_rect_solve(
    x1: float,
    y1: float,
    r1: float,
    x2: float,
    y2: float,
    w2: float,
    h2: float
) -> Tuple[float, float]:
    nearest_x = max(x2, min(x1, x2 + w2))
    nearest_y = max(y2, min(y1, y2 + h2))    
    dist = pm.Vec2(x1 - nearest_x, y1 - nearest_y)

    penetrationDepth = r1 - dist.mag
    penetrationVector = dist.from_magnitude(penetrationDepth)
    return (penetrationVector.x, penetrationVector.y)

def center_distance(x1, y1, w1, h1, x2, y2, w2, h2) -> Tuple[float, float]:
    """
    Computes the distance between the centers of the given rectangles.
    """
    return (
        abs(x1 - x2) - ((w1 + w2) / 2),
        abs(y1 - y2) - ((h1 + h2) / 2)
    )

def circle_circle_solve(
    x1: float,
    y1: float,
    r1: float,
    x2: float,
    y2: float,
    r2: float
) -> Tuple[float, float]:
    angle = math.atan2(y1 - y2, x1 - x2)
    distanceBetweenCircles = math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
    distanceToMove = r2 + r1 - distanceBetweenCircles

    return (math.cos(angle) * distanceToMove, math.sin(angle) * distanceToMove)