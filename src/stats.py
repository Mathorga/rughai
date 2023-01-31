import math
import random

from engine.stats import Stats

class PlayerStats(Stats):
    def __init__(
        self,
        vitality: int,
        resistance: int,
        odds: int,
        variation: float
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
        self._max_health = self.compute_stat(5.0, self._resistance, 2.0) + self._resistance_variation
        self._defense = self.compute_stat(5.0, self._resistance, 2.0) + self._resistance_variation
        self._accel = self.compute_stat(5.0, self._resistance, 2.0) + self._resistance_variation
        # Vitality.
        self._max_speed = self.compute_stat(20.0, self._vitality, 2.0) + self._vitality_variation
        self._max_energy = self.compute_stat(50.0, self._vitality, 1.46) + self._vitality_variation
        self._attack = self.compute_stat(5.0, self._vitality, 2.0) + self._vitality_variation
        self._crit_damage = self.compute_stat(5.0, self._vitality, 2.0) + self._vitality_variation
        self._fail_damage = self.compute_stat(5.0, self._vitality, 2.0) + self._vitality_variation
        # Odds.
        self._crit_rate = self.compute_stat(0.0, self._odds, 2.0) + self._odds_variation
        self._fail_rate = self.compute_stat(0.0, self._odds, 2.0) + self._odds_variation

        # Current values.
        self._health = self._max_health
        self._energy = self._max_energy
        self.speed = 0
        self.dir = 0

    def compute_stat(self, min_value, modifier, exponent):
        return min_value + pow((math.log(modifier + 1) / math.log(10)), exponent) * 100

    def get_value(self):
        return (self._vitality_variation / self._variation) * (self._resistance_variation / self._variation) * (self._odds_variation / self._variation)