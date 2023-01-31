import pyglet
import pyglet.math as pm

from fixed_resolution import FixedResolution
from engine.camera import Camera
from engine.game_object import GameObject

class Scene:
    def __init__(
        self,
        window: pyglet.window.Window,
        view_width: int,
        view_height: int
    ):
        self._window = window
        self._view_width = view_width
        self._view_height = view_height
        self._fr = FixedResolution(
            window = self._window,
            width = self._view_width,
            height = self._view_height
        )

        # Create a new camera.
        self._camera = Camera(
            window = self._window
        )
        self._camera_speed = 10

        self._objects = []
        self._cam_target = None

    def draw(self):
        with self._fr:
            with self._camera:
                for obj in self._objects:
                    obj.draw()

    def update(self, dt):
        for object in self._objects:
            object.update(dt)

        # Update camera.
        if self._cam_target != None:
            camera_movement = pm.Vec2(
                (self._cam_target.x - self._view_width / 2 - self._camera.position[0]) * self._camera_speed * dt,
                (self._cam_target.y - self._view_height / 2 - self._camera.position[1]) * self._camera_speed * dt
            )
            self._camera.position = (
                self._camera.position[0] + camera_movement.x,
                self._camera.position[1] + camera_movement.y
            )

    def add_object(
        self,
        game_object: GameObject,
        cam_target: bool = False
    ):
        if cam_target:
            self._cam_target = game_object
            self._camera.position = (
                self._cam_target.x - self._view_width / 2,
                self._cam_target.y - self._view_height / 2,
            )

        self._objects.append(game_object)