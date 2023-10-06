<p align="center" width="100%">
    <img width="66%" style="image-rendering:pixelated" src="/assets/sprites/menus/main/title_expo.png"> 
</p>
Rughai is an action RPG game built entirely in Python.

## Install dependencies
`pip3 install -r requirements.txt` or `pip3 install pyglet==2.0.3 pillow==9.5.0`

## Run
`python3 -O .\src\main.py`

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

### Misc
`target_fps` -> Target FPS; keep this value high if you don't want any lags.</br>
`camera_speed` -> The speed at which the camera follows the player, the higher the speed, the closer it will be to the player.</br>
`layers_z_spacing` -> Distance between rendered layers on the Z axis.</br>

## Idle props
Simple prop can be added by defining an appropriate json file.</br>
Idle prop files are defined as follows:</br>

  * `animation_specs[array]`: array of all animation definitions. Every element is structured as follows:</br>
    * `path[string]`: a path to the animation file (starting from the application-defined assets directory).</br>
    * `name[string]`: a name used to reference the single animation across the file.</br>
    * `anchor_x[int](optional)`: the x component of the animation-specific anchor point.</br>
    * `anchor_y[int](optional)`: the y component of the animation-specific anchor point.</br>
  * `animations[object]`: object defining all animations by category. Categories are "idle", "meet_in", "meeting", "meet_out", "interact", "hit" and "destroy". Every element in each category is defined as follows:</br>
    * `name[string]`: the name of the animation name, as defined in animation_specs.</br>
    * `weight[int]`: the selection weight of the specific animation, used during the animation selection algorithm. Probability for a specific animation is calculated as 1 / (category_weight_sum - animation_weight)</br>
  * `anchor_x[int](optional)`: x component of the global animation anchor point, this is used when no animation-specific anchor point is defined.</br>
  * `anchor_y[int](optional)`: y component of the global animation anchor point, this is used when no animation-specific anchor point is defined.</br>
  * `health_points[int](optional)`: amount of damage the prop can take before breaking. If this is not set, then an infinite amount is used, aka the prop cannot be broken.</br>
  * `colliders[array](optional)`: array of all colliders (responsible for "blocking" collisions). Every element in defined as follows:</br>
    * `tags[array]`: array of all collision tags the single collider reacts to.</br>
    * `offset_x[int]`: horizontal displacement, relative to the prop's position.</br>
    * `offset_y[int]`: vertical displacement, relative to the prop's position.</br>
    * `width[int]`: collider width</br>
    * `height[int]`: collider height</br>
    * `anchor_x[int]`: x component of the collider's anchor point.</br>
    * `anchor_y[int]`: y component of the collider's anchor point.</br>
  * `sensors[array](optional)`: array of all sensors (responsible for "non blocking" collisions). Every element in defined as follows:</br>
    * `tags[array]`: array of all collision tags the single sensor reacts to.</br>
    * `offset_x[int]`: horizontal displacement, relative to the prop's position.</br>
    * `offset_y[int]`: vertical displacement, relative to the prop's position.</br>
    * `width[int]`: sensor width</br>
    * `height[int]`: sensor height</br>
    * `anchor_x[int]`: x component of the sensor's anchor point.</br>
    * `anchor_y[int]`: y component of the sensor's anchor point.</br>
