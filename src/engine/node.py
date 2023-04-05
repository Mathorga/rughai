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
        x: int = 0,
        y: int = 0,
        z: float = 0.0
    ) -> None:
        self.x = x
        self.y = y
        self.z = z

    def get_bounding_box(self):
        return (self.x, self.y, self.x, self.y)