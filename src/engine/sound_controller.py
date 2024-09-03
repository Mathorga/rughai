import random
import pyglet

from engine.settings import SETTINGS, Keys
from engine.utils import utils

# def on_effect_eos(self: pyglet.media.Player) -> None:
#     self.pause()
#     self.delete()

# pyglet.media.Player.on_effect_eos = on_effect_eos

class SoundController:
    def __init__(self) -> None:
        # Background music.
        self.bg_music: pyglet.media.Player = pyglet.media.Player()

        # Sound effects
        self.effects: list[pyglet.media.Player] = []

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

    def __on_effect_eos(self, player: pyglet.media.Player) -> None:
        player.pause()
        self.effects.remove(player)
        player.delete()

    def play_effect(self, sound: pyglet.media.StaticSource) -> None:
        """
        Plays the provided sound effect.
        """

        # Just return if sound is disabled.
        if not SETTINGS[Keys.SOUND] or not SETTINGS[Keys.SFX]:
            return

        # Create a temporary player.
        player: pyglet.media.Player = pyglet.media.Player()

        # Queue the source to play.
        player.queue(sound)

        # Pitch shift the sound.
        player.pitch = utils.scale(val = random.random(), src = (0.0, 1.0), dst = (0.8, 1.2))
        player.play()

        # End and delete on end of source event.
        player.on_eos = lambda : self.__on_effect_eos(player)

        # Store the temporary player.
        self.effects.append(player)