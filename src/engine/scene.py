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
        view_height: int,
        scaling: int = 1,
        cam_speed: float = 10.0
    ):
        self._window = window
        self._view_width = view_width
        self._view_height = view_height
        self._scaling = scaling

        self._fr = FixedResolution(
            window = self._window,
            width = self._view_width * self._scaling,
            height = self._view_height * self._scaling
        )

        # Create a new camera.
        self._camera = Camera(
            window = self._window
        )
        self._cam_speed = cam_speed
        self._cam_target = None

        self._fixed_objs = []
        self._sorted_objs = []

    def get_scaled_view_size(self):
        return (
            self._view_width * self._scaling,
            self._view_height * self._scaling
        )

    def draw(self):
        with self._fr:
            with self._camera:
                # Draw fixed objects.
                for obj in self._fixed_objs:
                    obj.draw()

                # Draw sorted objects.
                for obj in self._sorted_objs:
                    obj.draw()

    def update(self, dt):
        # Sort objects by y coord in order to get depth.
        self._sorted_objs.sort(key = lambda obj : -obj.y)

        for object in self._fixed_objs:
            object.update(dt)

        for object in self._sorted_objs:
            object.update(dt)

        # Update camera.
        if self._cam_target != None:
            camera_movement = pm.Vec2(
                (self._cam_target.x - self.get_scaled_view_size()[0] / 2 - self._camera.position[0]) * self._cam_speed * dt,
                (self._cam_target.y - self.get_scaled_view_size()[1] / 2 - self._camera.position[1]) * self._cam_speed * dt
            )
            self._camera.position = (
                self._camera.position[0] + camera_movement.x,
                self._camera.position[1] + camera_movement.y
            )

    def add_object(
        self,
        game_object: GameObject,
        cam_target: bool = False,
        sorted: bool = False
    ):
        if cam_target:
            self._cam_target = game_object
            self._camera.position = (
                self._cam_target.x - self.get_scaled_view_size()[0] / 2,
                self._cam_target.y - self.get_scaled_view_size()[1] / 2,
            )

        if sorted:
            self._sorted_objs.append(game_object)
        else:
            self._fixed_objs.append(game_object)