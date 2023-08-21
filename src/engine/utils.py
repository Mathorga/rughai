from typing import Optional, Tuple
import math
import pyglet
import pyglet.math as pm

EPSILON = 1e-8

class Rect:
    def __init__(
        self,
        center: pm.Vec2,
        half_size: pm.Vec2
    ) -> None:
        self.center = center
        self.half_size = half_size

class CollisionHit:
    def __init__(
        self,
        collider: Rect
    ) -> None:
        self.collider = collider

        # Point of contact between colliders.
        self.position = pm.Vec2()

        # Vector describing the overlap between colliders.
        self.delta = pm.Vec2()

        # Surface normal at the point of contact.
        self.normal = pm.Vec2()

        # Time of intersection, only used with segments intersection (and swept rectangles).
        self.time = 0.0

def intersect_point_rect(
    point: pm.Vec2,
    rect: Rect
) -> Optional[CollisionHit]:
    """
    Computes the collision hit between a point and a rectangle.
    """
    dx = point.x - rect.center.x
    px = rect.half_size.x - abs(dx)
    if px <= 0.0:
        return None
    
    dy = point.y - rect.center.y
    py = rect.half_size.y - abs(dy)
    if py <= 0.0:
        return None

    hit = CollisionHit(rect)
    if px < py:
        sx = math.copysign(1.0, dx)
        hit.delta.x = px * sx
        hit.normal.x = sx
        hit.position.x = rect.center.x + (rect.half_size.x * sx)
        hit.position.y = point.y
    else:
        sy = math.copysign(1.0, dy)
        hit.delta.y = py * sy
        hit.normal.y = sy
        hit.position.x = point.x
        hit.position.y = rect.center.y + (rect.half_size.y * sy)

    return hit

def intersect_segment_rect(
    rect: Rect,
    position: pm.Vec2,
    delta: pm.Vec2,
    padding_x: float = 0.0,
    padding_y: float = 0.0
) -> Optional[CollisionHit]:
    """
    Computes the collision hit between a segment and a rectangle.
    A segment A-B is defined by position (A) and delta (B - A).
    Slight adaptation of https://github.com/Joshua-Micheletti/PysicsWorld
    """
    #    |    (A)|
    #    |      \|
    #    |       x -> far_time_x
    #    |       |\
    #    |       | \
    # ---+-------+--x--- -> near_time_y
    #    |       |   \
    #    |       |   (B)
    #    |       |     \
    # ---+-------+------x -> far_time_y
    #    |       |
    #    |       |

    # Prepare a tiny number to account for division by 0.
    division_threshold_x = EPSILON
    division_threshold_y = EPSILON

    if position.x <= rect.center.x:
        division_threshold_x = -division_threshold_x

    if position.y <= rect.center.y:
        division_threshold_y = -division_threshold_y

    if delta.x == 0:
        delta.x = division_threshold_x

    if delta.y == 0:
        delta.y = division_threshold_y

    # Cache division in order not to waste time computing them multiple times.
    scale_x = 1.0 / delta.x
    scale_y = 1.0 / delta.y

    near_time_x = (rect.center.x - (rect.half_size.x + padding_x) - position.x) * scale_x
    far_time_x = (rect.center.x + (rect.half_size.x + padding_x) - position.x) * scale_x

    near_time_y = (rect.center.y - (rect.half_size.y + padding_y) - position.y) * scale_y
    far_time_y = (rect.center.y + (rect.half_size.y + padding_y) - position.y) * scale_y

    # Make sure near_time is less than far_time, otherwise the delta vector may be reversed and the two values should be swapped.
    if near_time_x > far_time_x:
        tmp = near_time_x
        near_time_x = far_time_x
        far_time_x = tmp

    if near_time_y > far_time_y:
        tmp = near_time_y
        near_time_y = far_time_y
        far_time_y = tmp

    if near_time_x > far_time_y or near_time_y > far_time_x:
        return None

    near_time = max(near_time_x, near_time_y)
    far_time = min(far_time_x, far_time_y)

    if near_time >= 1 or far_time <= 0:
        return None

    hit = CollisionHit(rect)
    hit.time = clamp(near_time, 0, 1)

    if near_time_x > near_time_y:
        hit.normal.x = -math.copysign(1.0, delta.x)
        hit.normal.y = 0
    else:
        hit.normal.x = 0
        hit.normal.y = -math.copysign(1.0, delta.y)

    hit.delta.x = (1.0 - hit.time) * -delta.x
    hit.delta.y = (1.0 - hit.time) * -delta.y
    hit.position.x = position.x + delta.x * hit.time
    hit.position.y = position.y + delta.y * hit.time

    return hit

def intersect_rect_rect(
    collider: Rect,
    rect: Rect
) -> Optional[CollisionHit]:
    """
    Finds the hit point between a static rectangle (rect) and another (collider).
    """
    dx = collider.center.x - rect.center.x
    px = (collider.half_size.x + rect.half_size.x) - abs(dx)
    if px <= 0:
        return None

    dy = collider.center.y - rect.center.y
    py = (collider.half_size.y + rect.half_size.y) - abs(dy)
    if py <= 0:
        return None

    hit = CollisionHit(rect)
    if px < py:
        sx = math.copysign(1.0, dx)
        hit.delta.x = px * sx
        hit.normal.x = sx
        hit.position.x = rect.center.x + (rect.half_size.x * sx)
        hit.position.y = collider.center.y
    else:
        sy = math.copysign(1.0, dy)
        hit.delta.y = py * sy
        hit.normal.y = sy
        hit.position.x = collider.center.x
        hit.position.y = rect.center.y + (rect.half_size.y * sy)

    return hit

def sweep_rect_rect(
    collider: Rect,
    rect: Rect,
    delta: pm.Vec2
) -> Optional[CollisionHit]:
    """
    Useful links:
    https://github.com/Joshua-Micheletti/PysicsWorld
    https://www.gamedev.net/tutorials/programming/general-and-gameplay-programming/swept-aabb-collision-detection-and-response-r3084/
    https://noonat.github.io/intersect/
    https://blog.hamaluik.ca/posts/simple-aabb-collision-using-minkowski-difference/
    https://www.haroldserrano.com/blog/visualizing-the-gjk-collision-algorithm
    """

    # If the "moving" rectangle isn't actually moving (delta length is 0.0),
    # then just perform a static test.
    if delta.x == 0.0 and delta.y == 0.0:
        return intersect_rect_rect(
            collider = collider,
            rect = rect
        )

    # Otherwise just check for segment intersection, with the segment starting point
    # being the center of the moving rectangle, its delta being the rectangle delta
    # and the padding being the rectangle half size.
    return intersect_segment_rect(
        rect = rect,
        position = collider.center,
        delta = delta,
        padding_x = collider.half_size.x,
        padding_y = collider.half_size.y
    )

def sweep_circle_rect() -> Optional[CollisionHit]:
    """
    A single line-AABB intersection test, and possibly one line-circle test, depending on the outcome of first test.
    As seen in the image below, a single line-test to a larger AABB, expanded with the circle radius from the original AABB, decides whether or not the swept circle can hit at all.
    If it does hit, one needs only to check if the collision point is in any of the corners (colored in the image).
    If that is the case, the real collision point is always the line-circle intersection to that circle, and otherwise it's the collision point from the first test.
    """








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
    """
    Remaps x, which is in range [x_min, x_max], to range [y_min, y_max]
    """
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

    penetration_depth = r1 - dist.mag
    penetration_vector = dist.from_magnitude(penetration_depth)
    return (penetration_vector.x, penetration_vector.y)

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
    distance_between_circles = math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
    distance_to_move = r2 + r1 - distance_between_circles

    return (math.cos(angle) * distance_to_move, math.sin(angle) * distance_to_move)