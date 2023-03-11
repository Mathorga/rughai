from engine.sensor_node import SensorNode

class CollisionManager:
    def __init__(self) -> None:
        self.__colliders = []

    def add_collider(
        self,
        collider: SensorNode
    ):
        self.__colliders.append(collider)

    def __check_collisions(self):
        for child in self.__colliders:
            for other in self.__colliders:
                if child != other:
                    child.overlap(other)

    def update(self, dt):
        self.__check_collisions()