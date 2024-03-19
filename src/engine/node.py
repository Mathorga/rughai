from typing import List, Optional, Tuple


class Node:
    __slots__ = ()

    def __init__(self) -> None:
        pass

    def draw(self) -> None:
        """Renders the object."""

        pass

    def update(
            self,
            dt: float
        ) -> None:
        """
        Updates the whole object.
        All logic goes here, including movement.

        Parameters
        ----------
        dt: float
            Time (in s) since the last frame was calculated.
        """

        pass

    def delete(self) -> None:
        pass

class PositionNode(Node):
    __slots__ = (
        "x",
        "y",
        "z"
    )

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

class GroupNode(PositionNode):
    """
    Represents a node container, which displaces its children keeping their relative positions.
    """

    __slots__ = {
        "children"
    }

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        children: Optional[List[PositionNode]] = None
    ) -> None:
        super().__init__(x, y, z)

        self.children: List[PositionNode] = children if children is not None else []

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ):
        # Compute position delta.
        dp: Tuple[float, float] = (position[0] - self.x, position[1] - self.y)
        dz: float = z - self.z if z is not None else 0.0

        # Set the given position.
        self.x += dp[0]
        self.y += dp[1]
        self.z += dz

        # Move all children accordingly.
        for child in self.children:
            current_child_position: Tuple[int, int] = child.get_position()
            child.set_position(position = (current_child_position[0] + dp[0], current_child_position[1] + dp[1]), z = child.z + dz)

    def update(self, dt: float) -> None:
        super().update(dt)

        # Update all children.
        for child in self.children:
            child.update(dt = dt)

    def delete(self) -> None:
        for child in self.children:
            child.delete()

        self.children.clear()

        super().delete()