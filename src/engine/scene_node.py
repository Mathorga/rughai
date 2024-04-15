import math
import random
import threading
from typing import Callable, Optional, Sequence
import pyglet
import pyglet.math as pm

from engine.settings import GLOBALS, SETTINGS, Keys
from engine.camera import Camera
from engine.node import Node, PositionNode
from engine.shapes.rect_node import RectNode
from engine.text_node import TextNode
from engine.utils.tween import Tween

# Defines at which point the scene should be considered started while the curtain is opening.
SCENE_START_THRESHOLD: float = 0.4

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

    def get_bounding_box(self) -> tuple[int, int, int, int]:
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
        title: str | None = None,
        on_scene_start: Callable[[], None] | None = None,
        on_scene_end: Callable[[], None] | None = None,
        default_cam_speed: float = 10.0,
        curtain_speed: float = 1.0,
        cam_bounds: Bounds | None = None
    ):
        self.__view_width = view_width
        self.__view_height = view_height

        self.__on_scene_end = on_scene_end
        self.__on_scene_start = on_scene_start
        self.world_batch = pyglet.graphics.Batch()
        self.ui_batch = pyglet.graphics.Batch()

        # Tells whether the scene should be updating its children or not.
        self.__frozen: bool = False

        # Create a new camera.
        self.__camera = Camera(
            window = window
        )
        self.__default_cam_speed = default_cam_speed
        self.__cam_speed = default_cam_speed
        self.__cam_target = None
        self.__cam_bounds = cam_bounds
        self.__cam_shake: float = 0.0
        self.__cam_impulse: pyglet.math.Vec2 = pyglet.math.Vec2(0.0, 0.0)
        self.__cam_impulse_damp: float = 1.0

        # list of all children.
        self.__children: list[Node] = []

        # Scene title.
        if title is not None and SETTINGS[Keys.DEBUG]:
            label = TextNode(
                x = view_width // 2,
                y = view_height - 5,
                width = view_width,
                color = (0xFF, 0xFF, 0xFF, 0xFF),
                font_name = SETTINGS[Keys.FONT_NAME],
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
        # self.__curtain_opacity = 0xFF
        self.__curtain_opacity_fill: float = 1.0
        self.__curtain_speed: float = curtain_speed
        self.__curtain_opening: bool = True
        self.__curtain_closing: bool = False
        self.__curtain.set_opacity(int(Tween.compute(self.__curtain_opacity_fill, Tween.expInOut) * 0xFF))

    def get_scaled_view_size(self):
        return (
            self.__view_width * GLOBALS[Keys.SCALING],
            self.__view_height * GLOBALS[Keys.SCALING]
        )

    def draw(self):
        if self.__camera is not None:
            with self.__camera:
                self.world_batch.draw()

        # Draw UI elements.
        self.ui_batch.draw()

        # Draw curtain as last element.
        if self.__curtain is not None and self.__curtain_opacity_fill >= 0.0:
            self.__curtain.draw()

    def __update_curtain(self, dt):
        if self.__curtain_opening:
            self.__curtain_opacity_fill -= self.__curtain_speed * dt

            if self.__curtain_opacity_fill <= SCENE_START_THRESHOLD:
                # The curtain is fully opened, so call parent to notify.
                if self.__on_scene_start is not None:
                    self.__on_scene_start()

            if self.__curtain_opacity_fill <= 0.0:
                self.__curtain_opening = False
                self.__curtain_opacity_fill = 0.0

            if self.__curtain is not None:
                self.__curtain.set_opacity(int(Tween.compute(self.__curtain_opacity_fill, Tween.expInOut) * 0xFF))

        if self.__curtain_closing:
            self.__curtain_opacity_fill += self.__curtain_speed * dt

            if self.__curtain_opacity_fill >= 1.0:
                self.__curtain_closing = False
                self.__curtain_opacity_fill = 1.0

                if self.__on_scene_end:
                    self.__on_scene_end()

            if self.__curtain is not None:
                self.__curtain.set_opacity(int(Tween.compute(self.__curtain_opacity_fill, Tween.expInOut) * 0xFF))

    def __update_camera(self, dt):
        if self.__camera is not None and self.__cam_target is not None:
            scaled_view_size = self.get_scaled_view_size()

            # Compute camera shake.
            camera_shake: pm.Vec2 = pm.Vec2.from_polar(mag = self.__cam_shake * random.random(), angle = math.pi * 2 * random.random())

            # Compute camera movement from camera target.
            camera_movement: pm.Vec2 = pm.Vec2(
                (self.__cam_target.x * GLOBALS[Keys.SCALING] - scaled_view_size[0] / 2 - self.__camera.position[0]) * self.__cam_speed * dt,
                (self.__cam_target.y * GLOBALS[Keys.SCALING] - scaled_view_size[1] / 2 - self.__camera.position[1]) * self.__cam_speed * dt
            ) + camera_shake + self.__cam_impulse

            updated_x: float = self.__camera.position[0] + camera_movement.x
            updated_y: float = self.__camera.position[1] + camera_movement.y

            if self.__cam_bounds is not None and not (SETTINGS[Keys.DEBUG] and SETTINGS[Keys.FREE_CAM_BOUNDS]):
                # Apply bounds to camera movement by limiting updated position.
                if self.__cam_bounds.top is not None and self.__cam_bounds.top * GLOBALS[Keys.SCALING] < updated_y + self.__view_height * GLOBALS[Keys.SCALING]:
                    updated_y = self.__cam_bounds.top * GLOBALS[Keys.SCALING] - self.__view_height * GLOBALS[Keys.SCALING]
                if self.__cam_bounds.bottom is not None and self.__cam_bounds.bottom * GLOBALS[Keys.SCALING] > updated_y:
                    updated_y = self.__cam_bounds.bottom * GLOBALS[Keys.SCALING]
                if self.__cam_bounds.left is not None and self.__cam_bounds.left * GLOBALS[Keys.SCALING] > updated_x:
                    updated_x = self.__cam_bounds.left * GLOBALS[Keys.SCALING]
                if self.__cam_bounds.right is not None and self.__cam_bounds.right * GLOBALS[Keys.SCALING] < updated_x + self.__view_width * GLOBALS[Keys.SCALING]:
                    updated_x = self.__cam_bounds.right * GLOBALS[Keys.SCALING] - self.__view_width * GLOBALS[Keys.SCALING]

            # Damp down impulse.
            if self.__cam_impulse.mag > 0.0:
                self.__cam_impulse = self.__cam_impulse.from_magnitude(magnitude = round(self.__cam_impulse.mag - self.__cam_impulse_damp, GLOBALS[Keys.FLOAT_ROUNDING]))
            if self.__cam_impulse.mag < 0.0:
                self.__cam_impulse = pyglet.math.Vec2(0.0, 0.0)

            # Actually update camera position.
            self.__camera.position = (
                updated_x,
                updated_y
            )

    def freeze(self) -> None:
        """
        Stops all updates to children by setting the scene to frozen state.

        Call [melt] to unset the frozen state.
        """

        self.__frozen = True

    def melt(self) -> None:
        """
        Resumes all updates to children by unsetting the scene's frozen state.

        Call [freeze] to reset the frozen state.
        """

        self.__frozen = False

    def update(self, dt: float):
        # Update curtain.
        self.__update_curtain(dt)

        # Update all children if not frozen.
        if not self.__frozen:
            for child in self.__children:
                child.update(dt)

        # Update camera.
        self.__update_camera(dt)

    def get_cam_bounds(self) -> Bounds | None:
        return self.__cam_bounds

    def get_cam_shake(self) -> float:
        """
        Returns the current max amount of camera shake (in pixels).
        """

        return self.__cam_shake

    def set_cam_bounds(
        self,
        bounds: Bounds
    ) -> None:
        self.__cam_bounds = bounds

    def set_cam_shake(self, magnitude: float) -> None:
        """
        Sets the amount of camera shake.
        [magnitude] defines the maximum amount of displacement (in pixels).
        """

        self.__cam_shake = magnitude

    def set_cam_speed(
        self,
        speed: float
    ) -> None:
        """
        Sets the camera speed to the provided speed value.
        """

        self.__cam_speed = speed

    def apply_cam_impulse(
        self,
        impulse: pyglet.math.Vec2
    ) -> None:
        """
        Applies the provided impulse to the camera, effectively moving it.
        """
        self.__cam_impulse = impulse

    def shake_camera(self, magnitude: float, duration: float) -> None:
        """
        Shakes the camera for [duration] seconds with [magnitude] max amplitude.
        """

        self.set_cam_shake(magnitude = magnitude)

        timer: threading.Timer = threading.Timer(interval = duration, function = self.set_cam_shake, args = [0.0])
        timer.start()

    def add_child(
        self,
        child: Node | PositionNode,
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
                    self.__cam_target.x * GLOBALS[Keys.SCALING] - self.get_scaled_view_size()[0] / 2,
                    self.__cam_target.y * GLOBALS[Keys.SCALING] - self.get_scaled_view_size()[1] / 2,
                )

        self.__children.append(child)

    def remove_child(self, child: Node | PositionNode):
        """
        Removes the provided child from the scene if present.
        """

        if child in self.__children:
            self.__children.remove(child)

    def add_children(
        self,
        children: Sequence[Node | PositionNode],
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

    def end(self):
        self.__curtain_opening = False
        self.__curtain_closing = True