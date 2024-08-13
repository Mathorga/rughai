import pyglet

# Sprite resource type alias.
SpriteRes = pyglet.image.Texture | pyglet.image.animation.Animation

# Optional sprite resource type alias.
OptionalSpriteRes = pyglet.image.Texture | pyglet.image.animation.Animation | None