from enum import Enum
from typing import List, Optional, Tuple
import pyglet
import pyglet.math as pm
from constants import collision_tags, scenes
from engine import controllers

from engine.animation import Animation
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionRect
from engine.node import PositionNode
from engine.scene_node import Bounds
from engine.settings import SETTINGS, Builtins
from engine.sprite_node import SpriteNode
from engine.state_machine import State, StateMachine

class ArrowStates(str, Enum):
    FLY = "fly"
    HIT = "hit"
    OUT = "out"

class ArrowNode(PositionNode):
    """
    Arrow projectile class.
    """

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        direction: float = 0.0,
        speed: float = 0.0,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        self.batch: Optional[pyglet.graphics.Batch] = batch

        self.direction: float = direction
        self.speed: float = speed

        # Sprite distance, defines the distance at which the sprite floats.
        self.sprite_distance: float = 1.0

        # Animation handlers.
        self.animations: List[Animation] = [
            Animation(source = "sprites/scope/scope_load_0.json"),
            Animation(source = "sprites/scope/scope_load_0.json"),
            Animation(source = "sprites/scope/scope_load_1.json"),
            Animation(source = "sprites/scope/scope_load_2.json"),
            Animation(source = "sprites/scope/scope_load_3.json"),
            Animation(source = "sprites/scope/scope_load_4.json")
        ]

        # Distance between each sprite.
        self.sprites_delta: float = 1.5

        # Create sprites.
        self.sprites: List[SpriteNode] = []
        for animation in self.animations:
            self.sprites.append(
                SpriteNode(
                    resource = animation.content,
                    x = x,
                    y = y,
                    batch = batch
                )
            )

        # Collider.
        self.__collider = CollisionNode(
            x = x,
            y = y,
            sensor = True,
            collision_type = CollisionType.DYNAMIC,
            active_tags = [
                collision_tags.PLAYER_COLLISION,
                collision_tags.DAMAGE
            ],
            on_triggered = self.on_collision,
            shapes = [
                CollisionRect(
                    x = x,
                    y = y,
                    anchor_x = 3,
                    anchor_y = 3,
                    width = 6,
                    height = 6,
                    batch = batch
                )
            ]
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__collider)

        # State machine.
        self.__state_machine = StateMachine(
            states = {
                ArrowStates.FLY: ArrowFlyState(actor = self),
                ArrowStates.HIT: ArrowHitState(actor = self),
                ArrowStates.OUT: ArrowOutState(actor = self)
            }
        )

    def update(self, dt: float) -> None:
        super().update(dt)

        self.__state_machine.update(dt = dt)

        collider_position: Tuple[float, float] = self.__collider.get_position()

        self.set_position(collider_position)

    def set_velocity(self, velocity: Tuple[float, float]) -> None:
        self.__collider.set_velocity(velocity = velocity)

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        super().set_position(position = position, z = z)

        aim_vec: pyglet.math.Vec2 = pyglet.math.Vec2.from_polar(self.sprite_distance, self.direction)
        # Since sprites may be deleted before set_position is called, the whole section is trapped.
        # TODO This only happens for ArrowOutState, so needs a little check (it should happen for ArrowHitState as well).
        # May this have to do with frustum culling?
        try:
            for index, sprite in enumerate(self.sprites):
                    sprite.set_position(
                        position = (
                            position[0] + aim_vec.x + aim_vec.x * self.sprites_delta * (index + 1),
                            position[1] + aim_vec.y + aim_vec.y * self.sprites_delta * (index + 1)
                        ),
                        z = position[1] + SETTINGS[Builtins.LAYERS_Z_SPACING] * 0.5
                    )
        except Exception:
            print("ERROR")

    def on_collision(self, tags: List[str], enter: bool) -> None:
        self.__state_machine.on_collision(tags = tags, enter = enter)

    def delete(self) -> None:
        controllers.COLLISION_CONTROLLER.remove_collider(self.__collider)

        self.__collider.delete()

        for sprite in self.sprites:
            sprite.delete()

class ArrowState(State):
    def __init__(
        self,
        actor: ArrowNode
    ) -> None:
        super().__init__()

        self.actor: ArrowNode = actor

class ArrowFlyState(ArrowState):
    def update(self, dt: float) -> Optional[str]:
        # Define a vector from speed and direction.
        movement: pm.Vec2 = pm.Vec2.from_polar(self.actor.speed * dt, self.actor.direction)

        self.actor.set_velocity((movement.x, movement.y))

        scene_bounds: Bounds = scenes.ACTIVE_SCENE.get_cam_bounds()
        position: Tuple[float, float] = self.actor.get_position()
        if position[0] < scene_bounds.left or position[0] > scene_bounds.right or position[1] < scene_bounds.bottom or position[1] > scene_bounds.top:
            return ArrowStates.OUT

    def on_collision(self, tags: List[str], enter: bool) -> Optional[str]:
        if collision_tags.PLAYER_COLLISION in tags and enter:
            return ArrowStates.HIT

class ArrowHitState(ArrowState):
    def start(self) -> None:
        if scenes.ACTIVE_SCENE is not None:
            scenes.ACTIVE_SCENE.remove_child(self.actor)
        self.actor.delete()

class ArrowOutState(ArrowState):
    def start(self) -> None:
        if scenes.ACTIVE_SCENE is not None:
            scenes.ACTIVE_SCENE.remove_child(self.actor)
        self.actor.delete()