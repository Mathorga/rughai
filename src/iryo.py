import pyglet
import pyglet.math as pm

from engine.playable import Playable
from engine.input_controller import InputController
import engine.utils

from player_stats import PlayerStats

STATE_IDLE = 0x00
STATE_ATK = 0x01

class Iryo(Playable):
    def __init__(
        self,
        input_controller: InputController,
        x: int = 0,
        y: int = 0,
        scaling: int = 1
    ):
        # IDLE state animations.
        self._idle_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_idle.gif")
        self._walk_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_walk.gif")
        self._run_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_run.gif")
        self._roll_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_roll.gif")

        # ATK state animations.
        self._atk_idle_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_atk_idle.gif")

        # Center animations.
        engine.utils.center_anim(self._idle_anim)
        engine.utils.center_anim(self._walk_anim)
        engine.utils.center_anim(self._run_anim)
        engine.utils.center_anim(self._roll_anim)
        engine.utils.center_anim(self._atk_idle_anim)

        engine.utils.set_anim_duration(self._roll_anim, 0.08)
        self._roll_anim.frames[-1].duration = None

        super().__init__(
            input_controller = input_controller,
            stats = PlayerStats(
                vitality = 5,
                resistance = 5,
                odds = 5,
                variation = 0.2
            ),
            animation = self._idle_anim,
            x = x,
            y = y,
            scaling = scaling
        )
        self._sprite.push_handlers(self)

        self._state = STATE_IDLE

        # Movement flags.
        # Slow walking.
        self._slow = False
        # Currently rolling.
        self._rolling = False
        # Rolling started.
        self._rolled = False

    def input(self):
        if not self._rolling:
            super().input()
            self._slow = self._input[pyglet.window.key.LSHIFT]
            self._rolling = self._input.key_presses.get(pyglet.window.key.SPACE, False)

            if (self._rolling):
                self._rolled = True

    def update_stats(self, dt):
        super().update_stats(dt)

        walk_speed = self._stats._max_speed * 0.5
        roll_speed = self._stats._max_speed * 2.0
        roll_accel = self._stats._accel * 0.5

        if self._rolling:
            if self._rolled:
                self._stats._speed = roll_speed
                self._rolled = False
            else:
                self._stats._speed -= roll_accel * dt
        else:
            if self._move_input.mag > 0.5:
                self._stats._dir = self._move_input.heading
                self._stats._speed += self._stats._accel * dt
            else:
                self._stats._speed -= self._stats._accel * dt

        if self._rolling:
            # Clamp speed between 0 and roll speed.
            self._stats._speed = pm.clamp(self._stats._speed, 0.0, roll_speed)
        elif self._slow:
            # Clamp speed between 0 and walk speed.
            self._stats._speed = pm.clamp(self._stats._speed, 0.0, walk_speed)
        else:
            # Clamp speed between 0 and max speed.
            self._stats._speed = pm.clamp(self._stats._speed, 0.0, self._stats._max_speed)

    def update_sprite(self):
        super().update_sprite()

        # Update sprite image based on current speed.
        image_to_show = None
        if self._rolling:
            image_to_show = self._roll_anim
        else:
            if self._stats._speed <= 0:
                image_to_show = self._idle_anim
            elif self._stats._speed < self._stats._max_speed * self._run_threshold:
                image_to_show = self._walk_anim
            else:
                image_to_show = self._run_anim
        
        if image_to_show != None and (self._sprite.image != image_to_show):
            self._sprite.image = image_to_show

    def on_animation_end(self):
        if self._rolling:
            print("ROLL_ANIM_END")
            self._rolling = False

    def update(self, dt):
        super().update(dt)