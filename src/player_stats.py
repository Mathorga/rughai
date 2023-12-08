import math
import random

DEFAULT_MIN = 5.0
DEFAULT_MAX = 20.0
LEVELS = 25

class PlayerStats():
    def __init__(
        self,
        vitality: int = 0,
        resistance: int = 0,
        odds: int = 0,
        variation: float = 0.0
    ):
        # Modifiers.
        self.vitality = vitality
        self.resistance = resistance
        self.odds = odds
        self.variation = variation

        # Modifier variations.
        self.vitality_variation = random.random() * self.variation
        self.resistance_variation = random.random() * self.variation
        self.odds_variation = random.random() * self.variation

        # Stats.
        # Resistance.
        self.max_health = self.compute_stat(
            mod = self.resistance,
            max_mod = LEVELS,
            min_value = DEFAULT_MIN,
            max_value = DEFAULT_MAX,
            variation = self.resistance_variation
        )
        self.defense = self.compute_stat(
            mod = self.resistance,
            max_mod = LEVELS,
            min_value = DEFAULT_MIN,
            max_value = DEFAULT_MAX,
            variation = self.resistance_variation
        )
        self.max_energy = self.compute_stat(
            mod = self.resistance,
            max_mod = LEVELS,
            min_value = DEFAULT_MIN,
            max_value = DEFAULT_MAX,
            variation = self.resistance_variation
        )
        self.min_draw_time = self.compute_stat(
            mod = self.resistance,
            max_mod = LEVELS,
            min_value = 1,
            max_value = 0.1,
            variation = self.resistance_variation
        )
        # Vitality.
        self.max_speed = self.compute_stat(
            mod = self.vitality,
            max_mod = LEVELS,
            min_value = 60.0,
            max_value = 100.0,
            variation = self.vitality_variation
        )
        self.accel = self.compute_stat(
            mod = self.vitality,
            max_mod = LEVELS,
            min_value = 100.0,
            max_value = 400.0,
            variation = self.vitality_variation
        )
        self.attack = self.compute_stat(
            mod = self.vitality,
            max_mod = LEVELS,
            min_value = DEFAULT_MIN,
            max_value = DEFAULT_MAX,
            variation = self.vitality_variation
        )
        self.crit_damage = self.compute_stat(
            mod = self.vitality,
            max_mod = LEVELS,
            min_value = DEFAULT_MIN,
            max_value = DEFAULT_MAX,
            variation = self.vitality_variation
        )
        self.fail_damage = self.compute_stat(
            mod = self.vitality,
            max_mod = LEVELS,
            min_value = DEFAULT_MIN,
            max_value = DEFAULT_MAX,
            variation = self.vitality_variation
        )
        # Odds.
        self._crit_rate = self.compute_stat(
            mod = self.odds,
            max_mod = LEVELS,
            min_value = DEFAULT_MIN,
            max_value = DEFAULT_MAX,
            variation = self.odds_variation
        )
        self._fail_rate = self.compute_stat(
            mod = self.odds,
            max_mod = LEVELS,
            min_value = DEFAULT_MIN,
            max_value = DEFAULT_MAX,
            variation = self.odds_variation
        )

        # Current values.
        self.health = self.max_health
        self.energy = self.max_energy
        self.speed = 0.0
        self.move_dir = 0.0
        self.look_dir = 0.0

    def compute_stat(
        self,
        mod: int,
        max_mod: int,
        min_value: float,
        max_value: float,
        variation: float
    ) -> float:
        multiplier = (max_value - min_value) / math.log(max_mod + 1)
        return min_value + math.log(mod + 1) * multiplier + variation

    def get_value(self) -> float:
        """
        Returns an overall value from all stats.
        """

        return (self.vitality_variation / self.variation) * (self.resistance_variation / self.variation) * (self.odds_variation / self.variation)