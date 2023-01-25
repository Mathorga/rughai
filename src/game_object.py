class GameObject:
    def __init__(self):
        pass

    def update(self):
        pass

class GameSprite(GameObject):
    def __init__(
        self,
        resources_dir: str,
        ysort = False,
    ):
        if resources_dir is not None:
            pass

        self._ysort = ysort
        pass