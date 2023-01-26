import settings
from application import Application
from tile_map import TileSet, TileMap
import game_object

# Create app.
app = Application(
    view_width = settings.VIEW_WIDTH,
    view_height = settings.VIEW_HEIGHT,
    window_width = 600,
    window_height = 600,
    title = settings.TITLE,
    assets_path = "../assets"
)

rughai_ground_tile_map = TileMap(
    order = 1,
    tile_set = TileSet(
        source = "tilesets/rughai/ground.png",
        tile_width = 8,
        tile_height = 8
    ),
)


app.add_object(rughai_ground_tile_map)

app.run()