import pyglet

from engine.collision.collision_controller import CollisionController
from engine.interaction_controller import InteractionController
from engine.input_controller import InputController
from engine.inventory_controller import InventoryController, MenuController
from engine.sound_controller import SoundController

COLLISION_CONTROLLER: CollisionController
INPUT_CONTROLLER: InputController
INTERACTION_CONTROLLER: InteractionController
SOUND_CONTROLLER: SoundController
INVENTORY_CONTROLLER: InventoryController
MENU_CONTROLLER: MenuController

def create_controllers(window: pyglet.window.Window) -> None:
    global COLLISION_CONTROLLER
    global INPUT_CONTROLLER
    global INTERACTION_CONTROLLER
    global SOUND_CONTROLLER
    global INVENTORY_CONTROLLER
    global MENU_CONTROLLER

    COLLISION_CONTROLLER = CollisionController()
    INPUT_CONTROLLER = InputController(window = window)
    INTERACTION_CONTROLLER = InteractionController()
    SOUND_CONTROLLER = SoundController()
    INVENTORY_CONTROLLER = InventoryController()
    MENU_CONTROLLER = MenuController()