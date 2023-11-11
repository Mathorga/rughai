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
        