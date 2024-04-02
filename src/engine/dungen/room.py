from random import Random


class Room:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> None:
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height

class BinaryRoom(Room):
    """
    https://medium.com/@guribemontero/dungeon-generation-using-binary-space-trees-47d4a668e2d0
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> None:
        super().__init__(x, y, width, height)

        self.min_width: int = 3
        self.min_height: int = 3
        self.max_width: int = 10
        self.max_height: int = 10

        self.children: list[BinaryRoom] = []

    def split(self) -> None:
        """
        Splits the room into two if possible, either vertically or horizontally.
        """

        choice: bool = Random.random() < 0.5

        if choice:
            if self.width >= 2 * self.min_width:
                self.v_split()
            elif self.height >= 2 * self.min_height:
                self.h_split()

        # Force a split if the room is too wide.
        if self.width > self.max_width:
            self.v_split()

        # Force a split if the room is too wide.
        if self.height > self.max_height:
            self.h_split()

    def v_split(self) -> None:
        # Split the room vertically by defining a random x position within 0 and width and create two children with the resulting sizes.
        # Make sure the resulting rooms are higher than min_height.
        # TODO
        pass

    def h_split(self) -> None:
        # Split the room horizontally by defining a random x position within 0 and height and create two children with the resulting sizes.
        # Make sure the resulting rooms are higher than min_height.
        # TODO
        pass