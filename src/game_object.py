import pyglet

class GameObject:
    """
    Generic game object, useful for custom update and draw.

    Methods
    ----------
    update(dt: int)
    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0
    ):
        self.x = x
        self.y = y
        pass

    def update(self, dt):
        """
        Updates the whole object.
        All logic goes here, including movement.

        Parameters
        ----------
        dt : int
            Time (in ms) since the last frame was calculated.
        """

        pass

    def draw(self):
        """Draws the object."""

        pass