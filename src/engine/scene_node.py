import pyglet
import pyglet.math as pm

from engine.camera import Camera
from engine.node import Node, PositionNode
from engine.rect_node import RectNode
from engine.sensor_node import SensorNode
from engine.utils import *

class SceneNode(Node):
    def __init__(
        self,
        window: pyglet.window.Window,
        view_width: int,
        view_height: int,
        on_scene_end = None,
        scaling: int = 1,
        cam_speed: float = 10.0,
        curtain_speed: int = 100,
        upper_cam_bound = None,
        lower_cam_bound = None,
        left_cam_bound = None,
        right_cam_bound = None
    ):
        self.__window = window
        self.__view_width = view_width
        self.__view_height = view_height
        self.__scaling = scaling

        self.__on_scene_end = on_scene_end

        # Create a new camera.
        self.__camera = Camera(
            window = self.__window
        )
        self.__cam_speed = cam_speed
        self.__cam_target = None
        self.__cam_bounds = (
            upper_cam_bound * scaling if upper_cam_bound != None else None,
            lower_cam_bound * scaling if lower_cam_bound != None else None,
            left_cam_bound * scaling if left_cam_bound != None else None,
            right_cam_bound * scaling if right_cam_bound != None else None
        )

        # Lists of all children.
        self.__fixed_children = []
        self.__sorted_children = []

        # Lists of visible children.
        self.__visible_fixed_children = []
        self.__visible_sorted_children = []
        self.__ui_children = []

        self.__curtain = RectNode(
            x = 0,
            y = 0,
            width = view_width,
            height = view_height,
            scaling = scaling
        )
        self.__curtain_opacity = 0xFF
        self.__curtain_speed = curtain_speed
        self.__curtain_opening = True
        self.__curtain_closing = False
        self.__curtain.set_opacity(self.__curtain_opacity)

    def get_scaled_view_size(self):
        return (
            self.__view_width * self.__scaling,
            self.__view_height * self.__scaling
        )

    def draw(self):
        with self.__camera:
            # Draw fixed objects.
            for child in self.__visible_fixed_children:
                child.draw()

            # Draw sorted objects.
            for child in self.__visible_sorted_children:
                child.draw()

        # Draw UI elements.
        for child in self.__ui_children:
            child.draw()

        # Draw curtain as last element.
        if self.__curtain_opacity >= 0x00:
            self.__curtain.draw()

    def __update_curtain(self, dt):
        if self.__curtain_opening:
            self.__curtain_opacity -= self.__curtain_speed * dt

            if self.__curtain_opacity <= 0x00:
                self.__curtain_opening = False
                self.__curtain_opacity = 0x00

            self.__curtain.set_opacity(int(self.__curtain_opacity))

        if self.__curtain_closing:
            self.__curtain_opacity += self.__curtain_speed * dt

            if self.__curtain_opacity >= 0xFF:
                self.__curtain_closing = False
                self.__curtain_opacity = 0xFF

                if self.__on_scene_end:
                    self.__on_scene_end()

            self.__curtain.set_opacity(int(self.__curtain_opacity))

    def __update_camera(self, dt):
        if self.__cam_target != None:
            camera_movement = pm.Vec2(
                (self.__cam_target.x * self.__scaling - self.get_scaled_view_size()[0] / 2 - self.__camera.position[0]) * self.__cam_speed * dt,
                (self.__cam_target.y * self.__scaling - self.get_scaled_view_size()[1] / 2 - self.__camera.position[1]) * self.__cam_speed * dt
            )

            updated_x = self.__camera.position[0] + camera_movement.x
            updated_y = self.__camera.position[1] + camera_movement.y

            if self.__cam_bounds[0] != None and self.__cam_bounds[0] < updated_y + self.__view_height * self.__scaling:
                updated_y = self.__cam_bounds[0] - self.__view_height * self.__scaling

            if self.__cam_bounds[1] != None and self.__cam_bounds[1] > updated_y:
                updated_y = self.__cam_bounds[1]

            if self.__cam_bounds[2] != None and self.__cam_bounds[2] > updated_x:
                updated_x = self.__cam_bounds[2]

            if self.__cam_bounds[3] != None and self.__cam_bounds[3] < updated_x + self.__view_width * self.__scaling:
                updated_x = self.__cam_bounds[3] - self.__view_width * self.__scaling


            self.__camera.position = (
                updated_x,
                updated_y
            )


            # for child in self.__fixed_children:
            #     # Only check distance to camera bounds children.
            #     if (isinstance(child, SensorNode) and child.tag == "camera"):
            #         # overlap(
            #         #     child.x * self.__scaling - child.anchor_x * self.__scaling,
            #         #     child.y * self.__scaling - child.anchor_y * self.__scaling,
            #         #     child.width * self.__scaling,
            #         #     child.height * self.__scaling,
            #         #     self.__camera.position[0] + camera_movement.x,
            #         #     self.__camera.position[1] + camera_movement.y,
            #         #     self.__view_width * self.__scaling,
            #         #     self.__view_height * self.__scaling
            #         # )

            #         # Compute distance to the child.
            #         dist = distance(
            #             ((child.x - child.anchor_x) + child.width / 2) * self.__scaling,
            #             ((child.y - child.anchor_y) + child.height / 2)* self.__scaling,
            #             child.width * self.__scaling,
            #             child.height * self.__scaling,
            #             updated_position[0] + ((self.__view_width / 2) * self.__scaling),
            #             updated_position[1] + ((self.__view_height / 2) * self.__scaling),
            #             self.__view_width * self.__scaling,
            #             self.__view_height * self.__scaling
            #         )
            #         # Compute horizontal movement.
            #         if abs(dist[0]) < abs(camera_movement.x):
            #             camera_movement.x = dist[0]
            #         # camera_movement.x = min(abs(dist[0]), abs(camera_movement.x))

            #         # # Compute vertical movement.
            #         if abs(dist[1]) < abs(camera_movement.y):
            #             camera_movement.y = dist[1]
            #         # camera_movement.y = min(abs(dist[1]), abs(camera_movement.y))


    def update(self, dt):
        # Update curtain.
        self.__update_curtain(dt)

        # Update all fixed children.
        for object in self.__fixed_children:
            object.update(dt)

        # Update all sorted children.
        for object in self.__sorted_children:
            object.update(dt)

        # Update camera.
        self.__update_camera(dt)

        # TODO Cull away children outside of the map.
        # self.__visible_fixed_children = list(
        #     filter(
        #         lambda child : isinstance(child, PositionNode) and overlap(
        #             *self.__get_cam_bounding_box(),
        #             *child.get_bounding_box()
        #         ),
        #         self.__fixed_children
        #     )
        # )
        # self.__visible_sorted_children = list(
        #     filter(
        #         lambda child : isinstance(child, PositionNode) and overlap(
        #             *self.__get_cam_bounding_box(),
        #             *child.get_bounding_box()
        #         ),
        #         self.__sorted_children
        #     )
        # )
        self.__visible_fixed_children = self.__fixed_children
        self.__visible_sorted_children = self.__sorted_children

        # Sort objects by y coord in order to get depth.
        self.__visible_sorted_children.sort(key = lambda child : -child.y)

    def __get_cam_bounding_box(self):
        return (
            self.__camera.position[0],
            self.__camera.position[1],
            self.__view_width * self.__scaling,
            self.__view_height * self.__scaling,
        )

    def add_child(
        self,
        child: PositionNode,
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
                    self.__cam_target.x * self.__scaling - self.get_scaled_view_size()[0] / 2,
                    self.__cam_target.y * self.__scaling - self.get_scaled_view_size()[1] / 2,
                )

            if sorted:
                self.__sorted_children.append(child)
            else:
                self.__fixed_children.append(child)

    def end(self):
        self.__curtain_opening = False
        self.__curtain_closing = True