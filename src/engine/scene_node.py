import pyglet
import pyglet.math as pm

from engine.camera import Camera

from engine.node import Node

class SceneNode(Node):
    def __init__(
        self,
        window: pyglet.window.Window,
        view_width: int,
        view_height: int,
        scaling: int = 1,
        cam_speed: float = 10.0
    ):
        self.__window = window
        self.__view_width = view_width
        self.__view_height = view_height
        self.__scaling = scaling

        # Create a new camera.
        self.__camera = Camera(
            window = self.__window
        )
        self.__cam_speed = cam_speed
        self.__cam_target = None

        self.__fixed_children = []
        self.__sorted_children = []
        self.__ui_children = []

    def get_scaled_view_size(self):
        return (
            self.__view_width * self.__scaling,
            self.__view_height * self.__scaling
        )

    def render(self):
        with self.__camera:
            # Draw fixed objects.
            for child in self.__fixed_children:
                child.render()

            # Draw sorted objects.
            for child in self.__sorted_children:
                child.render()

        for child in self.__ui_children:
            child.render()

    def update(self, dt):
        # Sort objects by y coord in order to get depth.
        self.__sorted_children.sort(key = lambda obj : -obj.y)

        for object in self.__fixed_children:
            object.update(dt)

        for object in self.__sorted_children:
            object.update(dt)

        # Update camera.
        if self.__cam_target != None:
            camera_movement = pm.Vec2(
                (self.__cam_target.x - self.get_scaled_view_size()[0] / 2 - self.__camera.position[0]) * self.__cam_speed * dt,
                (self.__cam_target.y - self.get_scaled_view_size()[1] / 2 - self.__camera.position[1]) * self.__cam_speed * dt
            )
            self.__camera.position = (
                self.__camera.position[0] + camera_movement.x,
                self.__camera.position[1] + camera_movement.y
            )

    def add_child(
        self,
        child: Node,
        cam_target: bool = False,
        sorted: bool = False,
        ui: bool = False
    ):
        if ui:
            self.__ui_children.append(child)
        else:
            if cam_target:
                self.__cam_target = child
                self.__camera.position = (
                    self.__cam_target.x - self.get_scaled_view_size()[0] / 2,
                    self.__cam_target.y - self.get_scaled_view_size()[1] / 2,
                )

            if sorted:
                self.__sorted_children.append(child)
            else:
                self.__fixed_children.append(child)