<p align="center" width="100%">
    <img width="66%" style="image-rendering:pixelated" src="/assets/sprites/menus/main/title.png"> 
</p>
Rughai is an action RPG game built entirely in Python.

## Install dependencies
`pip install pyglet==2.0.3 pillow==9.5.0`

## Run
`python -O .\src\main.py`

## Settings
You can change game settings by manually editing the `assets/settings.json` file:</br>

### Debug
`debug` -> General debug settings, shows some useful features such as update time, render time and collisions.</br>
`show_collisions` -> Specific debug setting, shows collisions, but only if debug is true</br>
`show_tiles_grid` -> Specific debug setting, shows tilemap grid lines.</br>

### Texts
`title` -> Game title: defines the title of the game window.</br>
`font_name` -> Game font; if you don't have the font installed, then an error will occur.</br>

### Rendering
`view_width` -> Base view width, defines the amount of pixels you can see horizontally</br>
`view_height` -> Base view height, defines the amount of pixels you can see vertically</br>
`pixel_perfect` -> Unused.</br>
`window_width` -> Actual window width in pixels (only used if not fullscreen).</br>
`window_height` -> Actual window height in pixels (only used if not fullscreen).</br>
`fullscreen` -> Fullscreen mode toggle.</br>
`target_fps` -> Target FPS; keep this value high if you don't want any lags.</br>

### Misc
`camera_speed` -> The speed at which the camera follows the player, the higher the speed, the closer it will be to the player.</br>