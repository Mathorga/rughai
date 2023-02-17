import pyglet

class InputController:
    def __init__(
        self,
        window: pyglet.window.Window
    ):
        self.__window = window

        self.keys = {}
        self.key_presses = {}
        self.key_releases = {}

        self.__window.push_handlers(self)

        # Get controllers.
        controllers = pyglet.input.get_controllers()
        if controllers:
            controller = controllers[0]
            controller.open()
            controller.push_handlers(self)

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
    def on_button_press(controller, button_name):
        if button_name == 'a':
            # start firing
            pass
        elif button_name == 'b':
            # do something else
            pass

    # def on_button_release(controller, button_name):
    #     if button_name == 'a':
    #         # stop firing
    #     elif button_name == 'b':
    #         # do something else

    def __getitem__(self, key):
        return self.keys.get(key, False)

    def __enter__(self):
        pass

    def __exit__(self, exception_type, exception_value, traceback):
        self.key_presses.clear()
        pass