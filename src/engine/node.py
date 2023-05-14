from typing import Optional, Tuple


class Node:
    def __init__(self) -> None:
        pass

    def draw(self) -> None:
        """Renders the object."""

        pass

    def update(
            self,
            dt: int
        ) -> None:
        """
        Updates the whole object.
        All logic goes here, including movement.

        Parameters
        ----------
        dt: int
            Time (in ms) since the last frame was calculated.
        """

        pass

    def delete(self) -> None:
        pass

class PositionNode(Node):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0
    ) -> None:
        self.x = x
        self.y = y
        self.z = z

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ):
        self.x = position[0]
        self.y = position[1]
        if z is not None:
            self.z = z

    def get_position(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        return (self.x, self.y, 0.0, 0.0)