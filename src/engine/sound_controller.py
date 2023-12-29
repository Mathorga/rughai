from typing import List
import pyglet

class SoundController:
    def __init__(self) -> None:
        # Background music.
        self.bg_music: pyglet.media.Player = pyglet.media.Player()

        # Sound effects
        self.effects: List[pyglet.media.Player] = []

    def set_music(self, music: pyglet.media.Source) -> None:
        if self.bg_music.source is not None:
            self.bg_music.delete()

        self.bg_music = music.play()
        self.bg_music.loop = True

    def pause_music(self) -> None:
        self.bg_music.pause()

    def restart_music(self) -> None:
        if self.bg_music.source is not None:
            # Get the current music source.
            current_source: pyglet.media.Source = self.bg_music.source

            # Replace the player with a new one.
            self.bg_music.delete()
            self.bg_music = current_source.play()
            self.bg_music.loop = True

    def play_effect(self, sound: pyglet.media.Source) -> None:
        """
        Plays the provided sound effect.
        """

        player: pyglet.media.Player = sound.play()
        player.on_eos = player.delete
        self.effects.append(player)