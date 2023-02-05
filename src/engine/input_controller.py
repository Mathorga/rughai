import pyglet

class InputController:
    def __init__(
        self,
        window: pyglet.window.Window
    ):
        self.__window = window
        self.keys = {
            # Movement.
            pyglet.window.key.W: False,
            pyglet.window.key.A: False,
            pyglet.window.key.S: False,
            pyglet.window.key.D: False,
            pyglet.window.key.UP: False,
            pyglet.window.key.LEFT: False,
            pyglet.window.key.DOWN: False,
            pyglet.window.key.RIGHT: False,

            pyglet.window.key.SPACE: False,

            # Modifiers.
            pyglet.window.key.LSHIFT: False
        }

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