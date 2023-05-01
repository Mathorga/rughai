from typing import Dict, List
from engine.collision.collision_node import CollisionNode

COLLISION_STATIC = 0
COLLISION_DYNAMIC = 1

class CollisionManager:
    def __init__(self) -> None:
        # self.__colliders: List[SensorNode] = []
        self.__colliders: Dict[int, List[CollisionNode]] = {}

    def add_collider(
        self,
        collider: CollisionNode,
        collider_type: int,
    ):
        self.__colliders[collider_type].append(collider)

    def __check_collisions(self):
        # Only check collision from dynamic to static, since dynamic/dynamic collisions are not needed for now.
        for collider in self.__colliders[COLLISION_DYNAMIC]:
            for other in self.__colliders[COLLISION_STATIC]:
                if collider != other:
                    collider.overlap(other)

    def update(self, dt):
        self.__check_collisions()

    def clear(self):
        self.__colliders.clear()
