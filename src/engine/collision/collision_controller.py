from typing import Dict, Optional

from engine.collision.collision_node import CollisionType, CollisionNode
from engine.utils.utils import CollisionHit

class CollisionController:
    def __init__(self) -> None:
        self.__colliders: Dict[CollisionType, list[CollisionNode]] = {}

    def add_collider(
        self,
        collider: CollisionNode
    ) -> None:
        if collider.type in self.__colliders:
            self.__colliders[collider.type].append(collider)
        else:
            self.__colliders[collider.type] = [collider]

    def __handle_collisions(self) -> None:
        # Only check collision from dynamic to static, since dynamic/dynamic collisions are not needed for now.
        if CollisionType.DYNAMIC in self.__colliders and CollisionType.STATIC in self.__colliders:
            # Loop through dynamic colliders.
            for actor in self.__colliders[CollisionType.DYNAMIC]:
                # Trigger all collisions from the previous step.
                for other in actor.in_collisions:
                    if actor.on_triggered is not None:
                        actor.on_triggered(other.passive_tags, True)
                    if other.on_triggered is not None:
                        other.on_triggered(actor.active_tags, True)
                for other in actor.out_collisions:
                    if actor.on_triggered is not None:
                        actor.on_triggered(other.passive_tags, False)
                    if other.on_triggered is not None:
                        other.on_triggered(actor.active_tags, False)
                actor.in_collisions.clear()
                actor.out_collisions.clear()

                # Solve collision and iterate until velocity is exhausted.
                while abs(actor.velocity_x) > 0.0 or abs(actor.velocity_y) > 0.0:
                    # Save the resulting collisions for the given actor.
                    nearest_collision: Optional[CollisionHit] = None

                    # Loop through static colliders.
                    for other in self.__colliders[CollisionType.STATIC]:
                        # Avoid calculating self-collision.
                        if actor == other:
                            continue

                        # Compute collision between actors.
                        collision_hit = actor.collide(other)

                        # Only save collision if it actually happened.
                        if not other.sensor and collision_hit is not None and collision_hit.time < 1.0:
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

    def update(self, _dt) -> None:
        self.__handle_collisions()

    def clear(self) -> None:
        self.__colliders.clear()

    def remove_collider(self, collider: CollisionNode):
        """
        Removes the given collider from the list, effectively preventing it from triggering collisions.
        """

        self.__colliders[collider.type].remove(collider)
