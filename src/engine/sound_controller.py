import builtins
from typing import List
import pyglet

from engine.settings import SETTINGS, Keys

def on_effect_eos(self: pyglet.media.Player) -> None:
    self.pause()
    self.delete()

pyglet.media.Player.on_effect_eos = on_effect_eos

class SoundController:
    def __init__(self) -> None:
        # Background music.
        self.bg_music: pyglet.media.Player = pyglet.media.Player()

        # Sound effects
        self.effects: List[pyglet.media.Player] = []

    def set_music(self, music: pyglet.media.Source) -> None:
        # Just return if sound is disabled.
        if not SETTINGS[Keys.SOUND] or not SETTINGS[Keys.MUSIC]:
            return

        if self.bg_music.source is not None:
            self.bg_music.delete()

        self.bg_music = music.play()
        self.bg_music.loop = True

    def pause_music(self) -> None:
        if self.bg_music.source is not None:
            self.bg_music.pause()

    def restart_music(self) -> None:
        if self.bg_music.source is not None:
            # Get the current music source.
            current_source: pyglet.media.Source = self.bg_music.source

            # Replace the player with a new one.
            self.bg_music.delete()
            self.bg_music = current_source.play()
            self.bg_music.loop = True

    def play_effect(self, sound: pyglet.media.StaticSource) -> None:
        """
        Plays the provided sound effect.
        """

        # Just return if sound is disabled.
        if not SETTINGS[Keys.SOUND] or not SETTINGS[Keys.SFX]:
            return

        player: pyglet.media.Player = sound.play()
        player.on_eos = player.on_effect_eos
        self.effects.append(player)