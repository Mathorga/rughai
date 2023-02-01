class Stats:
    def __init__(
        self,
        max_speed: int = 100,
        acceleration: int = 600
    ):
        self._max_speed = max_speed
        self._accel = acceleration
        self._speed = 0
        self._dir = 0