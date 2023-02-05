import math
import random

from engine.stats import Stats

DEFAULT_MIN = 5.0
DEFAULT_MAX = 20.0

class PlayerStats(Stats):
    def __init__(
        self,
        vitality: int = 0,
        resistance: int = 0,
        odds: int = 0,
        variation: float = 0.0
    ):
        # Modifiers.
        self._vitality = vitality
        self._resistance = resistance
        self._odds = odds
        self._variation = variation

        # Modifier variations.
        self._vitality_variation = random.random() * self._variation
        self._resistance_variation = random.random() * self._variation
        self._odds_variation = random.random() * self._variation

        # Stats.
        # Resistance.
        self._max_health = self.compute_stat(
            mod = self._resistance,
            max_mod = 25,
            min_value = DEFAULT_MIN,
            max_value = DEFAULT_MAX,
            variation = self._resistance_variation
        )
        self._defense = self.compute_stat(
            mod = self._resistance,
            max_mod = 25,
            min_value = DEFAULT_MIN,
            max_value = DEFAULT_MAX,
            variation = self._resistance_variation
        )
        self._max_energy = self.compute_stat(
            mod = self._resistance,
            max_mod = 25,
            min_value = DEFAULT_MIN,
            max_value = DEFAULT_MAX,
            variation = self._resistance_variation
        )
        # Vitality.
        self._max_speed = self.compute_stat(
            mod = self._vitality,
            max_mod = 25,
            min_value = 60.0,
            max_value = 100.0,
            variation = self._vitality_variation
        )
        self._accel = self.compute_stat(
            mod = self._vitality,
            max_mod = 25,
            min_value = 150.0,
            max_value = 600.0,
            variation = self._vitality_variation
        )
        self._attack = self.compute_stat(
            mod = self._vitality,
            max_mod = 25,
            min_value = DEFAULT_MIN,
            max_value = DEFAULT_MAX,
            variation = self._vitality_variation
        )
        self._crit_damage = self.compute_stat(
            mod = self._vitality,
            max_mod = 25,
            min_value = DEFAULT_MIN,
            max_value = DEFAULT_MAX,
            variation = self._vitality_variation
        )
        self._fail_damage = self.compute_stat(
            mod = self._vitality,
            max_mod = 25,
            min_value = DEFAULT_MIN,
            max_value = DEFAULT_MAX,
            variation = self._vitality_variation
        )
        # Odds.
        self._crit_rate = self.compute_stat(
            mod = self._odds,
            max_mod = 25,
            min_value = DEFAULT_MIN,
            max_value = DEFAULT_MAX,
            variation = self._odds_variation
        )
        self._fail_rate = self.compute_stat(
            mod = self._odds,
            max_mod = 25,
            min_value = DEFAULT_MIN,
            max_value = DEFAULT_MAX,
            variation = self._odds_variation
        )

        # Current values.
        self._health = self._max_health
        self._energy = self._max_energy
        self._speed = 0
        self._dir = 0

    def compute_stat(
        self,
        mod: int,
        max_mod: int,
        min_value: float,
        max_value: float,
        variation: float
    ):
        multiplier = (max_value - min_value) / ((math.log(max_mod + 1) / math.log(10)))
        return min_value + ((math.log(mod + 1) / math.log(10))) * multiplier + variation

    def get_value(self):
        return (self._vitality_variation / self._variation) * (self._resistance_variation / self._variation) * (self._odds_variation / self._variation)