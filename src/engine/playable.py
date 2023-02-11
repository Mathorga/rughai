import pyglet
import pyglet.math as pm
from pyglet.window import key

from engine.mover import Mover
from engine.input_controller import InputController
from engine.stats import Stats

class Playable(Mover):
    def __init__(
        self,
        input_controller: InputController,
        stats: Stats,
        animation,
        x: int = 0,
        y: int = 0,
        scaling: int = 1,
        run_threshold: float = 0.9,
    ):
        super().__init__(
            x = x,
            y = y,
            stats = stats,
            scaling = scaling
        )

        # Setup input handling.
        self._input = input_controller
        self._move_input = pyglet.math.Vec2()

        self._run_threshold = run_threshold

        self._sprite = pyglet.sprite.Sprite(
            img = animation,
            x = self.x,
            y = self.y
        )
        self._sprite.scale = scaling

        self.width = self._sprite.image.get_max_width()
        self.height = self._sprite.image.get_max_height()

        self._hor_facing = 1

    def input(self):
        self._move_input = pyglet.math.Vec2(self._input[key.D] - self._input[key.A], self._input[key.W] - self._input[key.S]).normalize()

    def update_stats(self, dt):
        # Only update facing if there's any horizontal movement.
        if self._move_input.x != 0.0:
            self._hor_facing = 1 if self._move_input.x > 0 else -1

    def update_sprite(self):
        # Update sprite position.
        self._sprite.x = self.x
        self._sprite.y = self.y

        # Flip sprite if moving to the left.
        self._sprite.scale_x = self._hor_facing

    def update(self, dt):
        super().update(dt)

        # Fetch input.
        self.input()

        # Update stats based on input.
        self.update_stats(dt)

        # Compute and apply movement to self's x and y coords.
        self.move(dt)

        # Update sprite accordingly.
        self.update_sprite()

    def draw(self):
        self._sprite.draw()

    def set_input(self, input_controller: InputController):
        self._input = input_controller