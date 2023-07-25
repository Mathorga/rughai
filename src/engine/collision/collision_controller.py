import functools
from typing import Dict, List, Optional
import pyglet

from engine.utils import CollisionSweep
from engine.collision.collision_node import CollisionType, CollisionNode

class CollisionController:
    # TODO Swept collisions.
    def __init__(self) -> None:
        self.__colliders: Dict[CollisionType, List[CollisionNode]] = {}

    def add_collider(
        self,
        collider: CollisionNode
    ) -> None:
        if collider.type in self.__colliders:
            self.__colliders[collider.type].append(collider)
        else:
            self.__colliders[collider.type] = [collider]

    def __solve_collision(
        self,
        actor: CollisionNode
    ) -> None:
        # Save the resulting collisions for the given actor.
        collisions: List[CollisionSweep] = []
        nearest_collision: Optional[CollisionSweep] = None
        for other in self.__colliders[CollisionType.STATIC]:
            if actor != other:
                # Compute collision between colliders.
                collision_sweep = actor.collide(other)

                # Only save collision if it actually happened.
                if collision_sweep.hit is not None and collision_sweep.time < 1.0:
                    if nearest_collision is None:
                        nearest_collision = collision_sweep
                    else:
                        if collision_sweep.hit.time < nearest_collision.hit.time:
                            nearest_collision = collision_sweep
                    collisions.append(collision_sweep)

        # Sort collision by hit time, in order to process them correctly.
        # collisions.sort(key = lambda element: element.hit.time)

        # if len(collisions) > 0:
        #     # TODO Compute collision reaction.
        #     deltas = list(map(lambda element: element.hit.delta, collisions))
        #     reaction = functools.reduce(lambda result, current: result + current, deltas)

        #     actor_velocity = actor.get_velocity()
        #     actor.set_velocity((actor_velocity[0] + reaction.x, actor_velocity[1] + reaction.y))

        #     # TODO Compute sliding reaction (???).

        # Handling collider movement here allows us to check for all collisions before actually moving.
        # for nearest_collision in collisions:
        if nearest_collision is not None:
            # Move to the collision point.
            actor.set_position((actor.get_position()[0] + actor.velocity_x * nearest_collision.hit.time, actor.get_position()[1] + actor.velocity_y * nearest_collision.hit.time))

            # Compute sliding reaction.
            x_result = (actor.velocity_x * abs(nearest_collision.hit.normal.y)) * (1.0 - nearest_collision.hit.time)
            y_result = (actor.velocity_y * abs(nearest_collision.hit.normal.x)) * (1.0 - nearest_collision.hit.time)
            actor.set_velocity((x_result, y_result))

        else:
            actor.set_position((actor.get_position()[0] + actor.velocity_x, actor.get_position()[1] + actor.velocity_y))
            actor.set_velocity((0.0, 0.0))

    def __check_collisions(self) -> None:
        # Only check collision from dynamic to static, since dynamic/dynamic collisions are not needed for now.
        if CollisionType.DYNAMIC in self.__colliders and CollisionType.STATIC in self.__colliders:
            for actor in self.__colliders[CollisionType.DYNAMIC]:
                # TODO Add a broad phase to enhance performance.

                # Fetch actor velocity in order to solve for x first and then for y.
                actor_velocity = actor.get_velocity()
                actor.set_velocity((actor_velocity[0], 0.0))
                self.__solve_collision(actor)

                actor.set_velocity((0.0, actor_velocity[1]))
                self.__solve_collision(actor)

    def update(self, _dt) -> None:
        self.__check_collisions()

    def clear(self) -> None:
        self.__colliders.clear()

    def remove_collider(self, collider: CollisionNode):
        """
        Removes the given collider from the list, effectively preventing it from triggering collisions.
        """
        self.__colliders[collider.type].remove(collider)
