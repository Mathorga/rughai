import pyglet
import pyglet.math as pm
from pyglet.window import key

from game_object import GameObject
from input_controller import InputController

class Character(GameObject):
    def __init__(
        self,
        res_folder: str,
        x: int = 0,
        y: int = 0
    ):
        super().__init__(
            x = x,
            y = y
        )

        self._res_folder = res_folder
        self._sprite = pyglet.sprite.Sprite(
            img = pyglet.resource.animation(self._res_folder),
            x = self.x,
            y = self.y
        )

    def update(self, dt):
        pass

    def draw(self):
        self._sprite.draw()
        pass

class Player(Character):
    def __init__(
        self,
        res_folder: str,
        x: int = 0,
        y: int = 0
    ):
        super().__init__(
            res_folder = res_folder,
            x = x,
            y = y
        )
        self.max_speed = 100
        self.speed = 0
        self.accel = 10
        self.dir = 0

    def update(self, dt):
        keys = self._input_controller.keys
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

    def set_input_controller(self, input_controller: InputController):
        super().set_input_controller(input_controller)

        # Preset used values, so that later accesses do not need any checks.
        self._input_controller.keys[pyglet.window.key.W] = False
        self._input_controller.keys[pyglet.window.key.A] = False
        self._input_controller.keys[pyglet.window.key.S] = False
        self._input_controller.keys[pyglet.window.key.D] = False

