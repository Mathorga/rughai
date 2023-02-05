import pyglet
import pyglet.math as pm

from engine.game_object import GameObject
from engine.stats import Stats

class Mover(GameObject):
    """
    Defines a moving entity, has a sprite and exposes a <move> method.
    """

    def __init__(
        self,
        stats: Stats,
        x: int = 0,
        y: int = 0,
        scaling: int = 1,
    ):
        super().__init__(
            x = x,
            y = y,
            scaling = scaling
        )

        self._stats = stats
        self._movement = pyglet.math.Vec2()

    def update_stats():
        pass

    def compute_movement(self, dt):
        # Define a vector direction.
        movement_base = pm.Vec2.from_polar(1.0, self._stats._dir)
        self._movement = movement_base.from_magnitude(self._stats._speed * self._scaling * dt)

    def move(self, dt):
        # Compute movement.
        self.compute_movement(dt)

        # Apply movement.
        self.x += self._movement.x
        self.y += self._movement.y