from typing import Dict, List, Optional

from engine.collision.collision_node import CollisionType, CollisionNode
from engine.utils import CollisionHit

class CollisionController:
    # TODO Swept collisions.
    def __init__(self) -> None:
        self.__colliders: Dict[CollisionType, List[CollisionNode]] = {}
        self.__sensors: Dict[CollisionType, List[CollisionNode]] = {}

    def add_collider(
        self,
        collider: CollisionNode
    ) -> None:
        if collider.sensor:
            if collider.type in self.__sensors:
                self.__sensors[collider.type].append(collider)
            else:
                self.__sensors[collider.type] = [collider]
        else:
            if collider.type in self.__colliders:
                self.__colliders[collider.type].append(collider)
            else:
                self.__colliders[collider.type] = [collider]

    def __solve_collision(
        self,
        actor: CollisionNode
    ) -> None:
        # Save the resulting collisions for the given actor.
        nearest_collision: Optional[CollisionHit] = None
        for other in self.__colliders[CollisionType.STATIC]:
            # TODO Add a broad phase to enhance performance!

            if actor != other:
                # Compute collision between colliders.
                collision_hit = actor.collide(other)

                # Only save collision if it actually happened.
                if collision_hit is not None and collision_hit.time < 1.0:
                    if nearest_collision is None:
                        nearest_collision = collision_hit
                    else:
                        if collision_hit.time < nearest_collision.time:
                            nearest_collision = collision_hit

        actor_position = actor.get_position()

        # Handling collider movement here allows us to check for all collisions before actually moving.
        # for nearest_collision in collisions:
        if nearest_collision is not None:
            # Move to the collision point.
            actor.set_position((
                actor_position[0] + actor.velocity_x * nearest_collision.time,
                actor_position[1] + actor.velocity_y * nearest_collision.time
            ))

            # Compute sliding reaction.
            x_result = (actor.velocity_x * abs(nearest_collision.normal.y)) * (1.0 - nearest_collision.time)
            y_result = (actor.velocity_y * abs(nearest_collision.normal.x)) * (1.0 - nearest_collision.time)

            # Set the resulting velocity for the next iteration.
            actor.set_velocity((x_result, y_result))
        else:
            actor.set_position((actor_position[0] + actor.velocity_x, actor_position[1] + actor.velocity_y))
            actor.set_velocity((0.0, 0.0))

    def __handle_collisions(self) -> None:
        # Only check collision from dynamic to static, since dynamic/dynamic collisions are not needed for now.
        # Deal with colliders first.
        if CollisionType.DYNAMIC in self.__colliders and CollisionType.STATIC in self.__colliders:
            for actor in self.__colliders[CollisionType.DYNAMIC]:
                # Solve collision and iterate until velocity is exhausted.
                while abs(actor.velocity_x) > 0.0 or abs(actor.velocity_y) > 0.0:
                    self.__solve_collision(actor)

        # Then sensors.
        if CollisionType.DYNAMIC in self.__sensors and CollisionType.STATIC in self.__sensors:
            for actor in self.__sensors[CollisionType.DYNAMIC]:
                # Check for intersection.
                for other in self.__sensors[CollisionType.STATIC]:
                    # TODO Add a broad phase to enhance performance.

                    if actor != other:
                        # Compute collision between colliders.
                        actor.collide(other)

                actor.set_velocity((0.0, 0.0))

    def update(self, _dt) -> None:
        self.__handle_collisions()

    def clear(self) -> None:
        self.__colliders.clear()

    def remove_collider(self, collider: CollisionNode):
        """
        Removes the given collider from the list, effectively preventing it from triggering collisions.
        """

        if collider.sensor:
            self.__sensors[collider.type].remove(collider)
        else:
            self.__colliders[collider.type].remove(collider)
