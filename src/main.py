import settings
from application import Application

# Create app.
app = Application(
    view_width = settings.VIEW_WIDTH,
    view_height = settings.VIEW_HEIGHT,
    window_width = 400,
    window_height = 400,
    title = settings.TITLE
)



app.run()