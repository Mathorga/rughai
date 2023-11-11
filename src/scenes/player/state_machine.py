from typing import Dict, Optional

class State:
    """
    Base class for all states inside a state machine.
    """

    def start(self):
        """
        Behavior on state start.
        """
        pass

    def update(self):
        """
        Behavior on state update.
        """
        pass

    def end(self):
        """
        Behavior on state end.
        """
        pass

class StateMachine:
    """
    States handler.
    """

    def __init__(
        self,
        states: Optional[Dict[str, State]] = None,
    ) -> None:
        self.states: Optional[Dict[str, State]] = states
        self.current_state: Optional[State] = None

    def set_state(self, key: str) -> None:
        """
        Sets the state associated to the provided [key].
        """

        if key in self.states.keys():
            self.current_state = self.states[key]