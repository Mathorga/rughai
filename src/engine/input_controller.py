import pyglet

class InputController:
    def __init__(
        self,
        window: pyglet.window.Window
    ):
        self.__window = window
        self.keys = dict()

        self.__window.push_handlers(self)

    def on_key_press(
        self,
        symbol: int,
        modifiers
    ):
        self.keys[symbol] = True

    def on_key_release(
        self,
        symbol: int,
        modifiers
    ):
        self.keys[symbol] = False