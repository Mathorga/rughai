from amonite.state_machine import State
from amonite.state_machine import StateMachine

from iryo.states.iryo_state import IryoState
from iryo.states.iryo_state import IryoStates

from constants import collision_tags

class IryoStateMachine(StateMachine):
    """
    Player state machine specialization. Handles player state transitions and adds input management.
    """

    def enable_input(self) -> None:
        """
        Enables input handling on the current state.
        """

        # Just return if there's no current state.
        if self.current_key is None:
            return

        # Retrieve the current state.
        current_state: State = self.states[self.current_key]

        if isinstance(current_state, IryoState):
            current_state.enable_input()

    def disable_input(self) -> None:
        """
        Disables input handling on the current state.
        """

        # Just return if there's no current state.
        if self.current_key is None:
            return

        # Retrieve the current state.
        current_state: State = self.states[self.current_key]

        if isinstance(current_state, IryoState):
            current_state.disable_input()

    def on_collision(self, tags: list[str], enter: bool) -> None:
        # Transition to fall state if a fall collision is met.
        if enter and collision_tags.FALL in tags:
            self.transition(IryoStates.FALL)