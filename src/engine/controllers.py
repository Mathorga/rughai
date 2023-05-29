from typing import Tuple
import pyglet

from engine.collision.collision_controller import CollisionController
from engine.interaction_controller import InteractionController
from engine.input_controller import InputController


COLLISION_CONTROLLER: CollisionController
INPUT_CONTROLLER: InputController
INTERACTION_CONTROLLER: InteractionController

def create_controllers(window: pyglet.window.Window) -> Tuple:
    global COLLISION_CONTROLLER
    global INPUT_CONTROLLER
    global INTERACTION_CONTROLLER

    COLLISION_CONTROLLER = CollisionController()
    INPUT_CONTROLLER = InputController(window = window)
    INTERACTION_CONTROLLER = InteractionController()