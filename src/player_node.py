import pyglet
import pyglet.math as pm
from pyglet.window import key

from engine.node import PositionNode
from engine.input_controller import InputController
from engine.sprite_node import SpriteNode
import engine.utils as utils

from player_stats import PlayerStats

class PlayerNode(PositionNode):
    def __init__(
        self,
        input_controller: InputController,
        x: int = 0,
        y: int = 0,
        run_threshold: float = 0.9,
        scaling: int = 1
    ) -> None:
        super().__init__(
            x = x * scaling,
            y = y * scaling
        )

        self.__scaling = scaling

        # IDLE state animations.
        self.__idle_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_idle.gif")
        self.__walk_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_walk.gif")
        self.__run_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_run.gif")
        self.__roll_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_roll.gif")

        # ATK state animations.
        self.__atk_idle_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_atk_idle.gif")

        # Center animations.
        utils.center_anim(self.__idle_anim)
        utils.center_anim(self.__walk_anim)
        utils.center_anim(self.__run_anim)
        utils.center_anim(self.__roll_anim)
        utils.center_anim(self.__atk_idle_anim)

        utils.set_anim_duration(self.__roll_anim, 0.08)
        self.__roll_anim.frames[-1].duration = None

        self.__movement = pyglet.math.Vec2()

        # Setup input handling.
        self.__input = input_controller
        self.__move_input = pyglet.math.Vec2()

        self.__run_threshold = run_threshold

        self.__stats = PlayerStats(
            vitality = 5,
            resistance = 5,
            odds = 5,
            variation = 0.2
        )

        # Movement flags.
        # Slow walking.
        self.__slow = False
        # Currently rolling.
        self.__rolling = False
        # Rolling started.
        self.__rolled = False

        self.__hor_facing: float = 1.0

        self.__sprite = SpriteNode(
            resource = self.__idle_anim,
            on_animation_end = self.on_sprite_animation_end,
            x = x,
            y = y,
            scaling = scaling
        )

    def render(self):
        self.__sprite.render()

    def update(self, dt) -> None:
        # Fetch input.
        self.input()

        # Update stats based on input.
        self.update_stats(dt)

        # Compute and apply movement to self's x and y coords.
        self.move(dt)

        # Update sprite accordingly.
        self.update_sprite()

    def on_sprite_animation_end(self):
        if self.__rolling:
            self.__rolling = False

    def input(self):
        if not self.__rolling:
            self.__move_input = pyglet.math.Vec2(self.__input[key.D] - self.__input[key.A], self.__input[key.W] - self.__input[key.S]).normalize()
            self.__slow = self.__input[pyglet.window.key.LSHIFT]
            self.__rolling = self.__input.key_presses.get(pyglet.window.key.SPACE, False)

            if (self.__rolling):
                self.__rolled = True

    def update_stats(self, dt):
        # Only update facing if there's any horizontal movement.
        if self.__move_input.x != 0.0:
            self.__hor_facing = 1.0 if self.__move_input.x > 0 else -1.0

        walk_speed = self.__stats._max_speed * 0.5
        roll_speed = self.__stats._max_speed * 2.0
        roll_accel = self.__stats._accel * 0.5

        if self.__rolling:
            if self.__rolled:
                self.__stats._speed = roll_speed
                self.__rolled = False
            else:
                self.__stats._speed -= roll_accel * dt
        else:
            if self.__move_input.mag > 0.5:
                self.__stats._dir = self.__move_input.heading
                self.__stats._speed += self.__stats._accel * dt
            else:
                self.__stats._speed -= self.__stats._accel * dt

        if self.__rolling:
            # Clamp speed between 0 and roll speed.
            self.__stats._speed = pm.clamp(self.__stats._speed, 0.0, roll_speed)
        elif self.__slow:
            # Clamp speed between 0 and walk speed.
            self.__stats._speed = pm.clamp(self.__stats._speed, 0.0, walk_speed)
        else:
            # Clamp speed between 0 and max speed.
            self.__stats._speed = pm.clamp(self.__stats._speed, 0.0, self.__stats._max_speed)

    def compute_movement(self, dt):
        # Define a vector direction.
        movement_base = pm.Vec2.from_polar(1.0, self.__stats._dir)
        self.__movement = movement_base.from_magnitude(self.__stats._speed * self.__scaling * dt)

    def move(self, dt):
        # Compute movement.
        self.compute_movement(dt)

        # Apply movement.
        self.x += self.__movement.x
        self.y += self.__movement.y

    def update_sprite(self):
        # Update sprite position.
        self.__sprite.set_position(self.x, self.y)

        # Flip sprite if moving to the left.
        self.__sprite.set_scale(x_scale = self.__hor_facing)

        # Update sprite image based on current speed.
        image_to_show = None
        if self.__rolling:
            image_to_show = self.__roll_anim
        else:
            if self.__stats._speed <= 0:
                image_to_show = self.__idle_anim
            elif self.__stats._speed < self.__stats._max_speed * self.__run_threshold:
                image_to_show = self.__walk_anim
            else:
                image_to_show = self.__run_anim
        
        if image_to_show != None and (self.__sprite.get_image() != image_to_show):
            self.__sprite.set_image(image_to_show)