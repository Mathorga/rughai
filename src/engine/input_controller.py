import pyglet

class InputController:
    def __init__(
        self,
        window: pyglet.window.Window
    ):
        self.__window = window

        # Keyboard.
        self.keys = {}
        self.key_presses = {}
        self.key_releases = {}

        self.buttons = {}
        self.button_presses = {}
        self.button_releases = {}

        self.__window.push_handlers(self)

        # Get controllers.
        controller_manager = pyglet.input.ControllerManager()
        devs = pyglet.input.get_devices()
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

    def on_disconnect(self, controller):
        print("controller_disconnected:", controller)

    def on_button_press(self, controller, button_name):
        print("button_press:", button_name)
        self.buttons[button_name] = True

        # Only save key press if the key has been released first.
        self.button_presses[button_name] = self.key_releases.get(button_name, True)
        self.button_releases[button_name] = False

    def on_button_release(self, controller, button_name):
        self.buttons[button_name] = False
        self.button_presses[button_name] = False
        self.button_releases[button_name] = True

    def on_dpad_motion(self, controller, dpleft, dpright, dpup, dpdown):
        print("dpad_motion:", dpleft, dpright, dpup, dpdown)

    def on_stick_motion(self, controller, stick, xvalue, yvalue):
        print("stick_motion:", stick, xvalue, yvalue)

    def on_trigger_motion(self, controller, trigger, value):
        print("trigger_motion:", trigger, value)

    def __getitem__(self, key):
        return self.keys.get(key, False)

    def __enter__(self):
        pass

    def __exit__(self, exception_type, exception_value, traceback):
        self.key_presses.clear()
        pass