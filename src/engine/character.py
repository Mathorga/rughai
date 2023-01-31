import pyglet
import pyglet.math as pm
from pyglet.window import key

from engine.game_object import GameObject
from engine.input_controller import InputController
from stats import PlayerStats

class Character(GameObject):
    def __init__(
        self,
        x: int = 0,
        y: int = 0
    ):
        super().__init__(
            x = x,
            y = y
        )

    def update(self, dt):
        pass

    def draw(self):
        pass

class Character(Character):
    def __init__(
        self,
        input_controller: InputController,
        stats: PlayerStats,
        x: int = 0,
        y: int = 0
    ):
        super().__init__(
            x = x,
            y = y
        )

        self._input = input_controller
        self.__init_input()

        self._stats = stats

        self.max_speed = 100
        self.speed = 0
        self.accel = 10
        self.dir = 0

    def update(self, dt):
        keys = self._input.keys
        move_input = pyglet.math.Vec2(keys[key.D] - keys[key.A], keys[key.W] - keys[key.S]).normalize()
        movement_base = pm.Vec2.from_polar(1.0, self.dir)
        if move_input.mag > 0.5:
            self.dir = move_input.heading
            self.speed += self.accel
            if self.speed >= self.max_speed:
                self.speed = self.max_speed
        else:
            self.speed -= self.accel
            if self.speed <= 0:
                self.speed = 0
        movement = movement_base.from_magnitude(self.speed * dt)
        self.x += movement.x
        self.y += movement.y
        self._sprite.x = self.x
        self._sprite.y = self.y

    def set_input(self, input_controller: InputController):
        self._input = input_controller
        self.__init_input()

    def __init_input(self):
        # Preset used values, so that later accesses do not need any checks.
        if self._input != None:
            self._input.keys[pyglet.window.key.W] = False
            self._input.keys[pyglet.window.key.A] = False
            self._input.keys[pyglet.window.key.S] = False
            self._input.keys[pyglet.window.key.D] = False