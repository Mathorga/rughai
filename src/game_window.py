import pyglet

class GameWindow(pyglet.window.Window):
    def __init__(
        self,
        view_width: int,
        view_height: int,
        title: str,
        fullscreen: bool,
        resizable: bool,
    ):
        super(GameWindow, self).__init__(
            view_width,
            view_height,
            title,
            fullscreen=fullscreen,
            resizable=resizable
        )
        self.__main_batch = pyglet.graphics.Batch()
        pass

    def on_draw(self):
        self.clear()
