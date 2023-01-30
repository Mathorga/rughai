import settings
from application import Application
from tile_map import TileSet, TileMap
from character import Player

# Create app.
app = Application(
    view_width = settings.VIEW_WIDTH,
    view_height = settings.VIEW_HEIGHT,
    window_width = 600,
    window_height = 600,
    title = settings.TITLE,
    assets_path = "../assets",
    debug = True
)

# Add a tilemap to the app.
rughai_ground_tile_map = TileMap.from_tmj_file(
    source = "tilemaps/rughai/hub.tmj",
    order = 1,
    tile_set = TileSet(
        source = "tilemaps/tilesets/rughai/ground.png",
        tile_width = 8,
        tile_height = 8
    ),
)

iryo = Player(
    res_folder = "sprites/rughai/iryo/iryo.gif",
    x = 0,
    y = 0
)


app.add_object(rughai_ground_tile_map)
app.add_object(iryo, cam_target = True)

app.run()