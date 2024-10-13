<p align="center" width="100%">
    <img width="66%" style="image-rendering:pixelated" src="/assets/sprites/menus/main/title_expo.png">
</p>
Rughai is an action RPG game built entirely in Python.

## Create a new venv and activate it
`python3 -m venv .`</br>
`chmod +x ./bin/activate`</br>
`source ./bin/activate`</br>

## Install dependencies
`pip3 install -r requirements.txt`<br/>

## Run the game
`python3 -O .\src\main.py`<br/>

## Run the scene editor
`python3 -O .\src\scene_editor.py`<br/>

### Editor tools
The editor provides various tools, all with the same commands:<br/>
  * `WASD` to move the cursor on the map;<br/>
  * `IJKL` to move the camera around the current cursor position;<br/>
  * `LSHIFT`+`WASD` to move the cursor faster on the map;<br/>
  * `ENTER` to open the tool's dedicated menu (if present);<br/>
  * `SPACE` to trigger the tool's main mode;<br/>
  * `RSHIFT`+`SPACE` to trigger the tool's alternate mode (if present).<br/>

The currently available tools are:<br/>
  * Prop placement tool<br/>
  * Idle prop placement tool<br/>
  * Wall placement tool<br/>
  * Door placement tool (TODO)<br/>

## Compile to executable (using Nuitka)
In order to compile to executable you first need to install Nuitka:</br>
`pip3 install nuitka`</br>

Then you can launch the compile command:</br>
  * Windows:</br>
`py -m nuitka .\src\main.py --standalone --include-data-dir=./assets=.`</br>

  * Linux and MacOS:</br>
`python3 -m nuitka ./src/main.py --standalone --include-data-dir=./assets=.`</br>

You can then find the compiled version of the game inside the main_dist:</br>
  * Windows:</br>
`.\main_dist\main.exe`</br>

  * Linux:</br>
`./main_dist/main`</br>

  * MacOS:</br>
`./main.dist/main.bin`</br>

## Settings
You can change game settings by manually editing the [assets/settings.json](/assets/settings.json) file:</br>

### Debug
  * **debug** -> General debug setting, shows some useful features such as update time, render time and collisions.</br>
  * **show_collisions** -> Specific debug setting, shows collisions, but only if debug is true</br>
  * **show_tiles_grid** -> Specific debug setting, shows tilemap grid lines.</br>
  * **free_cam_bounds** -> Specific debug setting, allows the player to see beyond camera bounds.</br>

### Texts
  * **title** -> Game title: defines the title of the game window.</br>
  * **font_name** -> Game font; if you don't have the font installed, then an error will occur.</br>

### Rendering
  * **view_width** -> Base view width, defines the amount of pixels you can see horizontally</br>
  * **view_height** -> Base view height, defines the amount of pixels you can see vertically</br>
  * **pixel_perfect** -> Unused.</br>
  * **window_width** -> Actual window width in pixels (only used if not fullscreen).</br>
  * **window_height** -> Actual window height in pixels (only used if not fullscreen).</br>
  * **fullscreen** -> Fullscreen mode toggle.</br>

### Misc
  * **target_fps** -> Target FPS; keep this value high if you don't want any lags.</br>
  * **camera_speed** -> The speed at which the camera follows the player, the higher the speed, the closer it will be to the player.</br>
  * **layers_z_spacing** -> Distance between rendered layers on the Z axis.</br>
  * **tilemap_buffer** -> Width (in tiles number) of tilemap buffer, a higher tilemap buffer will reduce room size.</br>

### Sound
  * **sound** -> General sound setting, defines whether the game plays audio or not.</br>
  * **music** -> Specific sound setting, defines whether the game plays music or not.</br>
  * **sfx** -> Specific sound setting, defines whether the game plays sound effects or not.</br>

## Idle props
Simple prop can be added by defining an appropriate json file.</br>
Idle prop files are defined as follows:</br>
  * **animation_specs[array]**: array of all animation definitions. Every element is structured as follows:</br>
    * **path[string]**: a path to the animation file (starting from the application-defined assets directory).</br>
    * **name[string]**: a name used to reference the single animation across the file.</br>
    * **center_x[bool][optional]**: whether the animation should be centered on its x-axis.</br>
    * **center_y[bool][optional]**: whether the animation should be centered on its y-axis.</br>
    * **anchor_x[int][optional]**: the x component of the animation-specific anchor point. This is ignored if "center_x" is true.</br>
    * **anchor_y[int][optional]**: the y component of the animation-specific anchor point. This is ignored if "center_y" is true.</br>
    * **loop[bool][optional]**: whether the animation should loop or not. Defaults to true. This is useful when a non looping state should stick for a long time (e.g. destroyed or destroy when no destroy is provided).
  * **animations[object]**: object defining all animations by category. Categories are "idle", "meet_in", "meeting", "meet_out", "interact", "hit" and "destroy". Every element in each category is defined as follows:</br>
    * **name[string]**: the name of the animation name, as defined in animation_specs.</br>
    * **weight[int]**: the selection weight of the specific animation, used during the animation selection algorithm. Probability for a specific animation is calculated as `animation_weight / category_weight_sum`</br>
  * **anchor_x[int][optional]**: x component of the global animation anchor point, this is used when no animation-specific anchor point is defined.</br>
  * **anchor_y[int][optional]**: y component of the global animation anchor point, this is used when no animation-specific anchor point is defined.</br>
  * **layer[string][optional]**: layer in which to place the prop. Possible options are "dig", "rat" and "pid", which respectively place the prop below, in or above the player movement layer. Defaults to "rat".
  * **health_points[int][optional]**: amount of damage the prop can take before breaking. If this is not set, then an infinite amount is used, aka the prop cannot be broken.</br>
  * **colliders[array][optional]**: array of all colliders (responsible for "blocking" collisions). Every element in defined as follows:</br>
    * **tags[array]**: array of all collision tags the single collider reacts to.</br>
    * **offset_x[int]**: horizontal displacement, relative to the prop's position.</br>
    * **offset_y[int]**: vertical displacement, relative to the prop's position.</br>
    * **width[int]**: collider width</br>
    * **height[int]**: collider height</br>
    * **anchor_x[int]**: x component of the collider's anchor point.</br>
    * **anchor_y[int]**: y component of the collider's anchor point.</br>
  * **sensors[array][optional]**: array of all sensors (responsible for "non blocking" collisions). Every element in defined as follows:</br>
    * **meet_tags[array]**: array of all collision tags causing meeting.</br>
    * **interact_tags[array]**: array of all collision tags causing interaction.</br>
    * **hit_tags[array]**: array of all collision tags causing hit.</br>
    * **offset_x[int]**: horizontal displacement, relative to the prop's position.</br>
    * **offset_y[int]**: vertical displacement, relative to the prop's position.</br>
    * **width[int]**: sensor width</br>
    * **height[int]**: sensor height</br>
    * **anchor_x[int]**: x component of the sensor's anchor point.</br>
    * **anchor_y[int]**: y component of the sensor's anchor point.</br>

[Examples](/assets/idle_prop/rughai)</br>

## Animations
All animations can be defined via a simple json definition file.</br>
Animation files are defined as follows:</br>
  * **name[string]**: name of the animation.</br>
  * **path[string]**: path to the animation file (starting from the application-defined assets directory).</br>
  * **anchor_x[int][optional]**: the x component of the animation anchor point.</br>
  * **anchor_y[int][optional]**: the y component of the animation anchor point.</br>
  * **center_x[bool][optional]**: whether the animation should be centered on the x axis. If present, this overrides the "anchor_x" parameter.</br>
  * **center_y[bool][optional]**: whether the animation should be centered on the y axis. If present, this overrides the "anchor_y" parameter.</br>
  * **duration[float][optional]**: the duration of each animation frame.</br>
  * **loop[bool][optional]**: whether the animation should loop or not.</br>

[Examples](/assets/sprites/iryo/animations)</br>

## Inventory
The inventory structure (sections, sizes etc) is defined by a json file made up as follows:
  * **sections[array]**: array of all inventory sections, each defined as follows:</br>
    * **size[string]**: string representation of the section size (in slots count), encoded as "[width],[height]".</br>
    * **name[string]**: name of the section, used to section to section linkage.</br>
    * **overflows[object]**: links to other sections upon overflow: tells which section the cursor should go to when overflowing in each direction. The go to for each overflow can be the name of another section or the "wrap" keyword, which means wrapping around itself keeping the other index unchanged.</br>
      * **top[string]**: section to go to when overflowing to the top.</br>
      * **bottom[string]**: section to go to when overflowing to the bottom.</br>
      * **left[string]**: section to go to when overflowing to the left.</br>
      * **right[string]**: section to go to when overflowing to the right.</br>

## Wallmaps
All walls for a room can be defined via a simple json placement file.</br>
#TODO

[Examples](/assets/wallmaps)</br>

## Doormaps
All doors for a room can be defined via a simple json placement file.</br>
#TODO

[Examples](/assets/doormaps)</br>