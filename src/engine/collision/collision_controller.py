from typing import Dict, List

from engine.collision.collision_node import CollisionType, CollisionNode

class CollisionController:
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

    def __check_collisions(self) -> None:
        # Only check collision from dynamic to static, since dynamic/dynamic collisions are not needed for now.
        if CollisionType.DYNAMIC in self.__colliders and CollisionType.STATIC in self.__colliders:
            for collider in self.__colliders[CollisionType.DYNAMIC]:
                for other in self.__colliders[CollisionType.STATIC]:
                    if collider != other:
                        collider.collide(other)

    def update(self, dt) -> None:
        self.__check_collisions()

    def clear(self) -> None:
        self.__colliders.clear()

    def remove_collider(self, collider: CollisionNode):
        """
        Removes the given collider from the list, effectively preventing it from triggering collisions.
        """
        self.__colliders[collider.type].remove(collider)
