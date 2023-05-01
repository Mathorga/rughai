from typing import Dict, List
from engine.collision.collision_node import CollisionNode, CollisionType

class CollisionManager:
    def __init__(self) -> None:
        # self.__colliders: List[SensorNode] = []
        self.__colliders: Dict[CollisionType, List[CollisionNode]] = {}

    def add_collider(
        self,
        collider: CollisionNode
    ):
        if collider.type in self.__colliders.keys():
            self.__colliders[collider.type].append(collider)
        else:
            self.__colliders[collider.type] = [collider]

    def __check_collisions(self):
        # Only check collision from dynamic to static, since dynamic/dynamic collisions are not needed for now.
        if CollisionType.DYNAMIC in self.__colliders.keys():
            for collider in self.__colliders[CollisionType.DYNAMIC]:
                for other in self.__colliders[CollisionType.STATIC]:
                    if collider != other:
                        collider.collide(other)

    def update(self, dt):
        self.__check_collisions()

    def clear(self):
        self.__colliders.clear()
