import math
from typing import Callable

c1: float = 1.70158
c2: float = c1 * 1.525
c3: float = c1 + 1
c4: float = (2 * math.pi) / 3
c5: float = (2 * math.pi) / 4.5

class Tween:
    """
    Class representing a tween transformation between 0 and 1.
    Exposes a [compute] method which returns the provided value mapped using the provided function.

    Exposes the following list of transformation functions:
     - linear
     - sineIn
     - sineOut
     - sineInOut
     - quadIn
     - quadOut
     - quadInOut
     - cubeIn
     - cubeOut
     - cubeInOut
     - expIn
     - expOut
     - expInOut
     - backIn
     - backOut
     - backInOut

    https://easings.net/
    https://github.com/ai/easings.net/blob/master/src/easings/easingsFunctions.ts
    """
    @staticmethod
    def linear(x: float) -> float:
        """
        Linear mapping.
        """

        return x

    @staticmethod
    def sineIn(x: float) -> float:
        return 1.0 - math.cos((x * math.pi) / 2.0)

    @staticmethod
    def sineOut(x: float) -> float:
        return math.sin((x * math.pi) / 2.0)

    @staticmethod
    def sineInOut(x: float) -> float:
        return -(math.cos(math.pi * x) - 1.0) / 2.0

    @staticmethod
    def quadIn(x: float) -> float:
        return x ** 2.0

    @staticmethod
    def quadOut(x: float) -> float:
        return 1.0 - ((1.0 - x) ** 2.0)

    @staticmethod
    def quadInOut(x: float) -> float:
        return 2.0 * x * x if x < 0.5 else 1.0 - ((-2.0 * x + 2.0) ** 2.0) / 2.0

    @staticmethod
    def cubeIn(x: float) -> float:
        return x ** 3.0

    @staticmethod
    def cubeOut(x: float) -> float:
        return 1.0 - (1 - x) ** 3.0

    @staticmethod
    def cubeInOut(x: float) -> float:
        return 4.0 * (x ** 3.0) if x < 0.5 else 1.0 - ((-2.0 * x + 2.0) ** 3.0) / 2.0

    @staticmethod
    def expIn(x: float) -> float:
        return 0.0 if x == 0.0 else (2.0 ** (10.0 * x - 10.0))

    @staticmethod
    def expOut(x: float) -> float:
        return 1.0 if x == 1.0 else 1.0 - (2.0 ** (-10.0 * x))

    @staticmethod
    def expInOut(x: float) -> float:
        return 0.0 if x == 0.0 else 1.0 if x == 1.0 else (2.0 ** (20.0 * x - 10.0)) / 2.0 if x < 0.5 else (2.0 - (2.0 ** (-20.0 * x + 10.0))) / 2.0

    @staticmethod
    def backIn(x: float) -> float:
        return c3 * x * x * x - c1 * x * x

    @staticmethod
    def backOut(x: float) -> float:
        return 1 + c3 * ((x - 1) ** 3) + c1 * ((x - 1) ** 2)

    @staticmethod
    def backInOut(x: float) -> float:
        return (((2 * x) ** 2) * ((c2 + 1) * 2 * x - c2)) / 2 if x < 0.5 else (((2 * x - 2) ** 2) * ((c2 + 1) * (x * 2 - 2) + c2) + 2) / 2

    @staticmethod
    def compute(fill: float, function: Callable[[float], float]) -> float:
        """
        Maps the provided fill value using the provided function.

        Parameters:
        fill (float): The value to map. Must be between 0.0 and 1.0

        Returns:
        float: The computed value

        """
        # Make sure the provided value is in range.
        assert fill >= 0.0 and fill <= 1.0, "Value should be between 0.0 and 1.0"

        return function(fill)