<p align="center" width="100%">
    <img width="66%" style="image-rendering:pixelated" src="/assets/sprites/menus/main/title.png"> 
</p>
Rughai is an action RPG game built entirely in Python.

## Install dependencies
`pip install pyglet pillow`

## Run
`python -O .\src\main.py`

## Settings
You can change game settings by manually editing the `assets/settings.json` file:</br>
`"debug": false` -> General debug settings, shows some useful features such as update time, render time and collisions.</br>
`"show_collisions": true` -> Specific debug setting, shows collisions, but only if debug is true</br>
`"title": "RUGHAI"` -> Game title: defines the title of the game window.</br>
`"font_name": "I pixel u"` -> Game font; if you don't have the font installed, then an error will occur.</br>
`"view_width": 240` -> Base view width, defines the amount of pixels you can see horizontally</br>
`"view_height": 160` -> Base view height, defines the amount of pixels you can see vertically</br>
`"pixel_perfect": false` -> Unused.</br>
`"window_width": 720` -> Actual window width in pixels (only used if not fullscreen).</br>
`"window_height": 480` -> Actual window height in pixels (only used if not fullscreen).</br>
`"fullscreen": true` -> Fullscreen mode toggle.</br>
`"target_fps": 480` -> Target FPS; keep this value high if you don't want any lags.</br>
`"camera_speed": 5.0` -> The speed at which the camera follows the player, the higher the speed, the closer it will be to the player.</br>