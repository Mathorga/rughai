from typing import Tuple
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

def clamp(src, min_value, max_value):
    if src < min_value:
        return min_value
    elif src > max_value:
        return max_value
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

def swept_rect_rect(
    x1: float,
    y1: float,
    w1: float,
    h1: float,
    x2: float,
    y2: float,
    w2: float,
    h2: float,
    vx1: float,
    vy1: float,
    vx2: float,
    vy2: float
) -> float:
    # TODO https://www.gamedev.net/tutorials/programming/general-and-gameplay-programming/swept-aabb-collision-detection-and-response-r3084/
    xInvEntry: float
    yInvEntry: float
    xInvExit: float
    yInvExit: float

    # Find the distance between the objects on the near and far sides for both x and y.
    if vx1 > 0.0:
        xInvEntry = x2 - (x1 + w1)
        xInvExit = (x2 + w2) - x1
    else:
        xInvEntry = (x2 + w2) - x1
        xInvExit = x2 - (x1 + w1)

    if vy1 > 0.0:
        yInvEntry = y2 - (y1 + h1)
        yInvExit = (y2 + h2) - y1
    else:
        yInvEntry = (y2 + h2) - y1
        yInvExit = y2 - (y1 + h1)

    # Ffind time of collision and time of leaving for each axis (if statement is to prevent divide by zero).
    xEntry: float
    yEntry: float
    xExit: float
    yExit: float

    if vx1 == 0.0:
        xEntry = -(float("inf"))
        xExit = (float("inf"))
    else:
        xEntry = xInvEntry / vx1
        xExit = xInvExit / vx1

    if vy1 == 0.0:
        yEntry = -(float("inf"))
        yExit = (float("inf"))
    else:
        yEntry = yInvEntry / vy1
        yExit = yInvExit / vy1

    # Find the earliest/latest times of collision.
    entryTime = max(xEntry, yEntry)
    exitTime = min(xExit, yExit)

    if entryTime > exitTime or xEntry < 0.0 and yEntry < 0.0 or xEntry > 1.0 or yEntry > 1.0:
        # If there was no collision.
        normalx = 0.0
        normaly = 0.0
        return 1.0

    else:
        # If there was a collision.
        # Calculate normal of collided surface and return the time of collision.
        if xEntry > yEntry:
            if xInvEntry < 0.0:
                normalx = 1.0
                normaly = 0.0
            else:
                normalx = -1.0
                normaly = 0.0
        else:
            if yInvEntry < 0.0:
                normalx = 0.0
                normaly = 1.0
            else:
                normalx = 0.0
                normaly = -1.0

        return entryTime

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