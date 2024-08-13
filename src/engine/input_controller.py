from functools import reduce
import pyglet

class InputController:
    def __init__(
        self,
        window: pyglet.window.BaseWindow,
        threshold: float = 0.1
    ):
        self.__window = window
        self.__threshold = threshold

        # Keyboard.
        self.keys: dict = {}
        self.key_presses: dict = {}
        self.key_releases: dict = {}

        # Controller.
        self.buttons: dict = {}
        self.button_presses: dict = {}
        self.button_releases: dict = {}
        self.sticks: dict = {}
        self.triggers: dict = {}

        self.__window.push_handlers(self)

        # Get controllers.
        controller_manager = pyglet.input.ControllerManager()
        controllers = controller_manager.get_controllers()
        if controllers:
            controller = controllers[0]
            controller.open()
            controller.push_handlers(self)

        controller_manager.push_handlers(self)

    # ----------------------------------------------------------------------
    # Keyboard events.
    # ----------------------------------------------------------------------
    def on_key_press(
        self,
        symbol: int,
        modifiers
    ):
        self.keys[symbol] = True

        # Only save key press if the key has been released first.
        self.key_presses[symbol] = self.key_releases.get(symbol, True)
        self.key_releases[symbol] = False

    def on_key_release(
        self,
        symbol: int,
        modifiers
    ):
        self.keys[symbol] = False
        self.key_presses[symbol] = False
        self.key_releases[symbol] = True

    # ----------------------------------------------------------------------
    # Controller events.
    # ----------------------------------------------------------------------
    def on_connect(self, controller):
        controller.open()
        controller.push_handlers(self)
        print("controller_connected:", controller)

    def on_disconnect(self, controller):
        self.buttons.clear()
        self.button_presses.clear()
        self.button_releases.clear()
        print("controller_disconnected:", controller)

    def on_button_press(self, controller, button_name):
        self.buttons[button_name] = True

        # Only save key press if the key has been released first.
        self.button_presses[button_name] = self.button_releases.get(button_name, True)
        self.button_releases[button_name] = False

    def on_button_release(self, controller, button_name):
        self.buttons[button_name] = False
        self.button_presses[button_name] = False
        self.button_releases[button_name] = True

    def on_dpad_motion(self, controller, dpleft, dpright, dpup, dpdown):
        pass

    def on_stick_motion(self, controller, stick, xvalue, yvalue):
        self.sticks[stick] = (
            xvalue if xvalue < -self.__threshold or xvalue > self.__threshold else 0.0,
            yvalue if yvalue < -self.__threshold or yvalue > self.__threshold else 0.0
        )

    def on_trigger_motion(self, controller, trigger, value):
        self.triggers[trigger] = value if value > self.__threshold else 0.0

    def __getitem__(self, key):
        return self.keys.get(key, False)

    def __enter__(self):
        pass

    def __exit__(self, exception_type, exception_value, traceback):
        self.key_presses.clear()

    # ----------------------------------------------------------------------
    # Getters.
    # ----------------------------------------------------------------------
    def get_modifier(self) -> bool:
        """
        Returns whether or not the modifier key is being pressed, either on controller or keyboard.
        """

        return self[pyglet.window.key.LSHIFT] or self.buttons.get("leftshoulder", False)

    def get_sprint(self) -> bool:
        """
        Returns whether the sprint button was pressed or not, either on controller or keyboard.
        """

        return self.key_presses.get(pyglet.window.key.SPACE, False) or self.button_presses.get("b", False)

    def get_interaction(self) -> bool:
        """
        Returns whether the interact button was pressed or not, either on controller or keyboard.
        """

        return self.key_presses.get(pyglet.window.key.F, False) or self.key_presses.get(pyglet.window.key.H, False) or self.button_presses.get("a", False)

    def get_main_atk(self) -> bool:
        """
        Returns whether the main attack button was pressed or not, either on controller or keyboard.
        """

        return self.key_presses.get(pyglet.window.key.M, False) or self.button_presses.get("x", False)

    def get_secondary_atk(self) -> bool:
        """
        Returns whether the secondary attack button was pressed or not, either on controller or keyboard.
        """

        return self.key_presses.get(pyglet.window.key.K, False) or self.button_presses.get("y", False)

    def get_fire_aim(self) -> bool:
        """
        Returns whether the range attack aim button was pressed or not.
        """

        return self.triggers.get("lefttrigger", 0.0) > 0.0

    def get_fire_load(self) -> bool:
        """
        Returns whether the range attack load button was pressed or not.
        """

        return self.triggers.get("righttrigger", 0.0) > 0.0

    def get_movement(self) -> bool:
        """
        Returns whether there's any move input or not, regardless its resulting magnitude.
        """

        stick: tuple[float, float] = self.sticks.get("leftstick", (0.0, 0.0))
        stick_vec: pyglet.math.Vec2 = pyglet.math.Vec2(stick[0], stick[1])
        return self[pyglet.window.key.D] or self[pyglet.window.key.A] or self[pyglet.window.key.W] or self[pyglet.window.key.S] or stick_vec.mag > 0.0

    def get_aim(self) -> bool:
        """
        Returns whether there's any aim input or not, regardless its resulting magnitude.
        """

        stick: tuple[float, float] = self.sticks.get("rightstick", (0.0, 0.0))
        stick_vec: pyglet.math.Vec2 = pyglet.math.Vec2(stick[0], stick[1])
        return self[pyglet.window.key.L] or self[pyglet.window.key.J] or self[pyglet.window.key.I] or self[pyglet.window.key.K] or stick_vec.mag > 0.0

    def get_movement_vec(self) -> pyglet.math.Vec2:
        """
        Returns the movement vector from keyboard and controller.
        """

        stick: tuple[float, float] = self.sticks.get("leftstick", (0.0, 0.0))
        stick_vec: pyglet.math.Vec2 = pyglet.math.Vec2(stick[0], stick[1])
        keyboard_vec: pyglet.math.Vec2 = pyglet.math.Vec2(
            self[pyglet.window.key.D] - self[pyglet.window.key.A],
            self[pyglet.window.key.W] - self[pyglet.window.key.S]
        ).from_magnitude(1.0)

        return (stick_vec + keyboard_vec).normalize()

    def get_aim_vec(self) -> pyglet.math.Vec2:
        """
        Returns the camera movement vector from keyboard and controller.
        """

        stick: tuple[float, float] = self.sticks.get("rightstick", (0.0, 0.0))
        stick_vec: pyglet.math.Vec2 = pyglet.math.Vec2(stick[0], stick[1])
        keyboard_vec: pyglet.math.Vec2 = pyglet.math.Vec2(
            self[pyglet.window.key.L] - self[pyglet.window.key.J],
            self[pyglet.window.key.I] - self[pyglet.window.key.K]
        ).from_magnitude(1.0)

        return (stick_vec + keyboard_vec).normalize()

    def get_cursor_movement_press(
        self,
        up_keys: list[int],
        left_keys: list[int],
        down_keys: list[int],
        right_keys: list[int]
    ) -> bool:
        """
        Returns whether the cursor movement is being started or not given the provided keys.
        """

        up: bool = reduce(lambda a, b: a or b, map(lambda element: self.key_presses.get(element, False), up_keys))
        left: bool = reduce(lambda a, b: a or b, map(lambda element: self.key_presses.get(element, False), left_keys))
        down: bool = reduce(lambda a, b: a or b, map(lambda element: self.key_presses.get(element, False), down_keys))
        right: bool = reduce(lambda a, b: a or b, map(lambda element: self.key_presses.get(element, False), right_keys))

        return up or left or down or right

    def get_cursor_movement_release(
        self,
        up_keys: list[int],
        left_keys: list[int],
        down_keys: list[int],
        right_keys: list[int]
    ) -> bool:
        """
        Returns whether the cursor movement is being ended or not.
        """

        up: bool = reduce(lambda a, b: a and b, map(lambda element: not self[element], up_keys))
        left: bool = reduce(lambda a, b: a and b, map(lambda element: not self[element], left_keys))
        down: bool = reduce(lambda a, b: a and b, map(lambda element: not self[element], down_keys))
        right: bool = reduce(lambda a, b: a and b, map(lambda element: not self[element], right_keys))

        return up and left and down and right

    def get_cursor_movement_vec(
        self,
        up_keys: list[int],
        left_keys: list[int],
        down_keys: list[int],
        right_keys: list[int]
    ) -> pyglet.math.Vec2:
        """
        Returns the movement vector from keyboard and controller.
        """

        up: bool = reduce(lambda a, b: a or b, map(lambda element: self[element], up_keys))
        left: bool = reduce(lambda a, b: a or b, map(lambda element: self[element], left_keys))
        down: bool = reduce(lambda a, b: a or b, map(lambda element: self[element], down_keys))
        right: bool = reduce(lambda a, b: a or b, map(lambda element: self[element], right_keys))

        return pyglet.math.Vec2(
            1 if right else 0 - 1 if left else 0,
            1 if up else 0 - 1 if down else 0
        )

    def get_ctrl(self) -> bool:
        return self[pyglet.window.key.LCTRL] or self[pyglet.window.key.LCOMMAND] or self[pyglet.window.key.RCTRL] or self[pyglet.window.key.RCOMMAND]

    def get_shift(self) -> bool:
        return self[pyglet.window.key.LSHIFT] or self[pyglet.window.key.RSHIFT]

    def get_tool_run(self) -> bool:
        return self.key_presses.get(pyglet.window.key.SPACE, False)

    def get_tool_clear(self) -> bool:
        return self.get_shift() and self.get_tool_run()

    def get_tool_alt(self) -> bool:
        """
        Returns whether the tool alternate mode key is being pressed or not.
        """

        return self[pyglet.window.key.RSHIFT]

    def get_start(self) -> bool:
        return self.key_presses.get(pyglet.window.key.ENTER, False)

    def get_undo(self) -> bool:
        return self.key_presses.get(pyglet.window.key.BACKSPACE, False)

    def get_redo(self) -> bool:
        return self.get_shift() and self.get_undo()

    def get_switch(self) -> bool:
        return self.key_presses.get(pyglet.window.key.TAB, False)

    def get_menu_page_left(self) -> bool:
        return self.key_presses.get(pyglet.window.key.Q, False)

    def get_menu_page_right(self) -> bool:
        return self.key_presses.get(pyglet.window.key.E, False)

    def get_draw(self) -> bool:
        """
        Returns whether the draw button was pressed or not, either on controller or keyboard.
        """

        return self[pyglet.window.key.SPACE] or self.triggers.get("righttrigger", 0.0) > 0.0

    def get_inventory_toggle(self) -> bool:
        """
        Returns whether the inventory toggle button was pressed or not.
        """

        return self.key_presses.get(pyglet.window.key.ENTER, False) or self.button_presses.get("start", False)