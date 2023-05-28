from typing import Tuple
import pyglet

from engine.collision.collision_controller import CollisionController
from engine.interaction_controller import InteractionController
from engine.input_controller import InputController


collision_controller: CollisionController
input_controller: InputController
interaction_controller: InteractionController

def create_controllers(window: pyglet.window.Window) -> Tuple:
    global collision_controller
    global input_controller
    global interaction_controller

    collision_controller = CollisionController()
    input_controller = InputController(window = window)
    interaction_controller = InteractionController()