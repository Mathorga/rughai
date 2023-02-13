class Node:
    def __init__(self) -> None:
        pass

    def render(self) -> None:
        """Renders the object."""

        pass

    def update(self, dt) -> None:
        """
        Updates the whole object.
        All logic goes here, including movement.

        Parameters
        ----------
        dt: int
            Time (in ms) since the last frame was calculated.
        """

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