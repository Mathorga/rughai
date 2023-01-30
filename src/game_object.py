from input_controller import InputController

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
        y: int = 0,
        input_controller: InputController = None
    ):
        """
        Creates a new game object.

        Parameters
        ----------
        x: int
            X position of the object
        y: int
            Y position of the object
        input_controller: InputController
            Input handler for providing inputs to the object.
        """

        self.x = x
        self.y = y
        self._input_controller = input_controller
        pass

    def update(self, dt):
        """
        Updates the whole object.
        All logic goes here, including movement.

        Parameters
        ----------
        dt: int
            Time (in ms) since the last frame was calculated.
        """

        pass

    def draw(self):
        """Draws the object."""

        pass