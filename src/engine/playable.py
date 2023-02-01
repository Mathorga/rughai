import math

import pyglet
import pyglet.math as pm
from pyglet.window import key

from engine.game_object import GameObject
from engine.input_controller import InputController
from engine.stats import Stats

class Playable(GameObject):
    def __init__(
        self,
        input_controller: InputController,
        stats: Stats,
        idle_animation,
        walk_animation,
        run_animation,
        x: int = 0,
        y: int = 0,
        run_threshold: float = 0.9
    ):
        super().__init__(
            x = x,
            y = y
        )

        # Setup input handling.
        self._input = input_controller
        self._init_input()
        self._move_input = pyglet.math.Vec2()

        self._stats = stats
        self._movement = pyglet.math.Vec2()
        self._run_threshold = run_threshold

        self._idle_animation = idle_animation
        self._walk_animation = walk_animation
        self._run_animation = run_animation

        self._sprite = pyglet.sprite.Sprite(
            img = self._idle_animation,
            x = self.x,
            y = self.y
        )
        self._hor_facing = 1

    def input(self):
        keys = self._input.keys
        self._move_input = pyglet.math.Vec2(keys[key.D] - keys[key.A], keys[key.W] - keys[key.S]).normalize()

    def update_stats(self, dt):
        # Only update facing if there's any horizontal movement.
        if self._move_input.x != 0.0:
            self._hor_facing = 1 if self._move_input.x > 0 else -1

        if self._move_input.mag > 0.5:
            self._stats._dir = self._move_input.heading
            self._stats._speed += self._stats._accel * dt
        else:
            self._stats._speed -= self._stats._accel * dt

        # Clamp speed between 0 and max speed.
        self._stats._speed = pm.clamp(self._stats._speed, 0.0, self._stats._max_speed)

    def move(self, dt):
        movement_base = pm.Vec2.from_polar(1.0, self._stats._dir)
        self._movement = movement_base.from_magnitude(self._stats._speed * dt)

    def update_sprite(self):
        # Update sprite position.
        self._sprite.x = self.x
        self._sprite.y = self.y

        # Flip sprite if moving to the left.
        self._sprite.scale_x = self._hor_facing

        # Update sprite image based on current speed.
        image_to_show = None
        if self._stats._speed <= 0:
            image_to_show = self._idle_animation
        elif self._stats._speed < self._stats._max_speed * self._run_threshold:
            image_to_show = self._walk_animation
        else:
            image_to_show = self._run_animation
        
        if image_to_show != None and self._sprite.image != image_to_show:
            self._sprite.image = image_to_show

    def update(self, dt):
        super().update(dt)

        # Fetch input.
        self.input()

        # Update stats based on input.
        self.update_stats(dt)

        # Compute speed.
        self.move(dt)

        # Apply movement.
        self.x += self._movement.x
        self.y += self._movement.y

        # Update sprite accordingly.
        self.update_sprite()

    def draw(self):
        self._sprite.draw()

    def set_input(self, input_controller: InputController):
        self._input = input_controller
        self._init_input()

    def _init_input(self):
        # Preset used values, so that later accesses do not need any checks.
        if self._input != None:
            self._input.keys[pyglet.window.key.W] = False
            self._input.keys[pyglet.window.key.A] = False
            self._input.keys[pyglet.window.key.S] = False
            self._input.keys[pyglet.window.key.D] = False