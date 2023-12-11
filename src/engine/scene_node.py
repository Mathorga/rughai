from typing import Callable, Optional, Sequence, Tuple, Union
import pyglet
import pyglet.math as pm

from engine.settings import GLOBALS, SETTINGS, Builtins
from engine.camera import Camera
from engine.node import Node, PositionNode
from engine.shapes.rect_node import RectNode
from engine.text_node import TextNode

# Defines at which point the scene should be considered started while the curtain is opening.
SCENE_START_THRESHOLD = 0x80

class Bounds:
    def __init__(
        self,
        top: Optional[int] = None,
        bottom: Optional[int] = None,
        left: Optional[int] = None,
        right: Optional[int] = None
    ) -> None:
        self.top = top if top is not None else None
        self.bottom = bottom if bottom is not None else None
        self.left = left if left is not None else None
        self.right = right if right is not None else None

    def get_width(self) -> int:
        assert self.right is not None and self.left is not None

        return self.right - self.left

    def get_height(self) -> int:
        assert self.top is not None and self.bottom is not None

        return self.top - self.bottom

    def get_bounding_box(self) -> Tuple[int, int, int, int]:
        assert self.top is not None and self.bottom is not None
        assert self.right is not None and self.left is not None

        return (
            self.left,
            self.bottom,
            self.right - self.left,
            self.top - self.bottom
        )

class SceneNode(Node):
    def __init__(
        self,
        window: pyglet.window.Window,
        view_width: int,
        view_height: int,
        title: Optional[str] = None,
        on_scene_start: Optional[Callable[[], None]] = None,
        on_scene_end: Optional[Callable[[], None]] = None,
        cam_speed: float = 10.0,
        curtain_speed: int = 200,
        cam_bounds: Optional[Bounds] = None
    ):
        self.__view_width = view_width
        self.__view_height = view_height

        self.__on_scene_end = on_scene_end
        self.__on_scene_start = on_scene_start
        self.world_batch = pyglet.graphics.Batch()
        self.ui_batch = pyglet.graphics.Batch()

        # Create a new camera.
        self.__camera = Camera(
            window = window
        )
        self.__cam_speed = cam_speed
        self.__cam_target = None
        self.__cam_bounds = cam_bounds

        # List of all children.
        self.__children = []

        # Scene title.
        if title is not None and SETTINGS[Builtins.DEBUG]:
            label = TextNode(
                x = view_width // 2,
                y = view_height - 5,
                width = view_width,
                color = (0xFF, 0xFF, 0xFF, 0xFF),
                font_name = SETTINGS[Builtins.FONT_NAME],
                text = title,
                batch = self.ui_batch
            )
            self.add_child(label)

        self.__curtain = RectNode(
            x = 0.0,
            y = 0.0,
            width = view_width,
            height = view_height
        )
        self.__curtain_opacity = 0xFF
        self.__curtain_speed = curtain_speed
        self.__curtain_opening = True
        self.__curtain_closing = False
        self.__curtain.set_opacity(self.__curtain_opacity)

    def get_scaled_view_size(self):
        return (
            self.__view_width * GLOBALS[Builtins.SCALING],
            self.__view_height * GLOBALS[Builtins.SCALING]
        )

    def draw(self):
        if self.__camera is not None:
            with self.__camera:
                self.world_batch.draw()

        # Draw UI elements.
        self.ui_batch.draw()

        # Draw curtain as last element.
        if self.__curtain is not None and self.__curtain_opacity >= 0x00:
            self.__curtain.draw()

    def __update_curtain(self, dt):
        if self.__curtain_opening:
            self.__curtain_opacity -= self.__curtain_speed * 0.5 * dt

            if self.__curtain_opacity <= SCENE_START_THRESHOLD:
                # The curtain is fully opened, so call parent to notify.
                if self.__on_scene_start is not None:
                    self.__on_scene_start()

            if self.__curtain_opacity <= 0x00:
                self.__curtain_opening = False
                self.__curtain_opacity = 0x00

            if self.__curtain is not None:
                self.__curtain.set_opacity(int(self.__curtain_opacity))

        if self.__curtain_closing:
            self.__curtain_opacity += self.__curtain_speed * 2 * dt

            if self.__curtain_opacity >= 0xFF:
                self.__curtain_closing = False
                self.__curtain_opacity = 0xFF

                if self.__on_scene_end:
                    self.__on_scene_end()

            if self.__curtain is not None:
                self.__curtain.set_opacity(int(self.__curtain_opacity))

    def __update_camera(self, dt):
        if self.__camera is not None and self.__cam_target is not None:
            scaled_view_size = self.get_scaled_view_size()

            # Compute camera movement from camera target.
            camera_movement = pm.Vec2(
                (self.__cam_target.x * GLOBALS[Builtins.SCALING] - scaled_view_size[0] / 2 - self.__camera.position[0]) * self.__cam_speed * dt,
                (self.__cam_target.y * GLOBALS[Builtins.SCALING] - scaled_view_size[1] / 2 - self.__camera.position[1]) * self.__cam_speed * dt
            )

            updated_x = self.__camera.position[0] + camera_movement.x
            updated_y = self.__camera.position[1] + camera_movement.y

            if self.__cam_bounds is not None and not SETTINGS[Builtins.FREE_CAM_BOUNDS]:
                # Apply bounds to camera movement by limiting updated position.
                if self.__cam_bounds.top is not None and self.__cam_bounds.top * GLOBALS[Builtins.SCALING] < updated_y + self.__view_height * GLOBALS[Builtins.SCALING]:
                    updated_y = self.__cam_bounds.top * GLOBALS[Builtins.SCALING] - self.__view_height * GLOBALS[Builtins.SCALING]
                if self.__cam_bounds.bottom is not None and self.__cam_bounds.bottom * GLOBALS[Builtins.SCALING] > updated_y:
                    updated_y = self.__cam_bounds.bottom * GLOBALS[Builtins.SCALING]
                if self.__cam_bounds.left is not None and self.__cam_bounds.left * GLOBALS[Builtins.SCALING] > updated_x:
                    updated_x = self.__cam_bounds.left * GLOBALS[Builtins.SCALING]
                if self.__cam_bounds.right is not None and self.__cam_bounds.right * GLOBALS[Builtins.SCALING] < updated_x + self.__view_width * GLOBALS[Builtins.SCALING]:
                    updated_x = self.__cam_bounds.right * GLOBALS[Builtins.SCALING] - self.__view_width * GLOBALS[Builtins.SCALING]

            # Actually update camera position.
            # Values are rounded in order not to cause subpixel movements and therefore texture bleeding.
            self.__camera.position = (
                updated_x,
                updated_y
                # round(updated_x),
                # round(updated_y)
            )

    def update(self, dt):
        # Update curtain.
        self.__update_curtain(dt)

        # Update all fixed children.
        for child in self.__children:
            child.update(dt)

        # Update camera.
        self.__update_camera(dt)

    def add_child(
        self,
        child: Union[Node, PositionNode],
        cam_target: bool = False
    ):
        """
        Adds the provided child to the scene.
        if cam_target is True, then the child has to be a PositionNode.
        """
        if cam_target:
            # Make sure the given child is actually a position node, otherwise it can't be a cam_target.
            assert isinstance(child, PositionNode)

            self.__cam_target = child
            if self.__camera is not None:
                self.__camera.position = (
                    self.__cam_target.x * GLOBALS[Builtins.SCALING] - self.get_scaled_view_size()[0] / 2,
                    self.__cam_target.y * GLOBALS[Builtins.SCALING] - self.get_scaled_view_size()[1] / 2,
                )

        self.__children.append(child)

    def remove_child(self, child: Union[Node, PositionNode]):
        """
        Removes the provided child from the scene.
        """

        self.__children.remove(child)

    def add_children(
        self,
        children: Sequence[Union[Node, PositionNode]],
    ):
        for child in children:
            self.add_child(
                child = child
            )

    def delete(self):
        for child in self.__children:
            child.delete()

        self.__children.clear()

        if self.__curtain is not None:
            self.__curtain.delete()

        self.__curtain = None
        self.__camera = None

    def get_cam_bounds(self) -> Bounds:
        return self.__cam_bounds

    def set_cam_bounds(
        self,
        bounds: Bounds
    ) -> None:
        self.__cam_bounds = bounds

    def end(self):
        self.__curtain_opening = False
        self.__curtain_closing = True