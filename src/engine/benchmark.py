import time
from collections import deque
from statistics import mean
import pyglet

class Benchmark:
    def __init__(
        self,
        window: pyglet.window.Window,
        x = None,
        y = None,
        text: str = "FPS: ",
        samples: int = 240,
        update_period: float = 0.25
    ) -> None:
        self._window = window

        self._text = text

        self._label = pyglet.text.Label(
            text = text,
            anchor_x = "left",
            anchor_y = "top",
            x = x if x != None else 10,
            y = y if y != None else window.height - 10,
            bold = True
        )

        self._update_period = update_period
        self._elapsed = 0.0
        self._delta_times = deque(maxlen = samples)

        self._start_time = 0.0

        self._last_time = 0.0

    def __enter__(self) -> None:
        self._start_time = time.time()

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        end_time = time.time()
        dt = end_time - self._start_time
        self._elapsed += end_time - self._last_time
        self._last_time = end_time
        self._delta_times.append(dt)

        if self._elapsed >= self._update_period:
            self._elapsed = 0.0
            self._label.text = f"{self._text}{mean(self._delta_times) * 1000:.3f}ms"

    def draw(self) -> None:
        self._label.draw()