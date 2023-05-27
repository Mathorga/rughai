from typing import Tuple
import pyglet

from engine.collision.collision_controller import CollisionController
from engine.dialog_controller import DialogController
from engine.input_controller import InputController


collision_controller: CollisionController
input_controller: InputController
dialog_controller: DialogController

def create_controllers(window: pyglet.window.Window) -> Tuple:
    global collision_controller
    global input_controller
    global dialog_controller

    collision_controller = CollisionController()
    input_controller = InputController(window = window)
    dialog_controller = DialogController()