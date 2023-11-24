from typing import Dict, Optional

class State:
    def start(self) -> None:
        pass

    def on_animation_end(self) -> Optional[str]:
        pass

    def on_collision(self, enter: bool) -> Optional[str]:
        pass

    def update(self, dt: float) -> Optional[str]:
        pass

    def end(self) -> None:
        pass

class StateMachine:
    def __init__(
        self,
        states: Optional[Dict[str, State]]
    ) -> None:
        self.states: Dict[str, State] = states if states is not None else {}
        self.current_key: Optional[str] = list(self.states.keys())[0] if len(self.states) > 0 else None

        current_state: Optional[State] = self.get_current_state()
        if current_state is None:
            return

        current_state.start()

    def get_current_state(self) -> Optional[State]:
        """
        Returns the current state of the state machine.
        """
        if self.current_key is None:
            return None

        return self.states[self.current_key]

    def set_state(self, key: str) -> None:
        """
        Sets as current state the one with the given key, if present.
        """

        if key in self.states:
            self.current_key = key

    def on_animation_end(self) -> Optional[str]:
        current_state: Optional[State] = self.get_current_state()
        if current_state is None:
            return

        self.transition(current_state.on_animation_end())

    def on_collision(self, enter: bool) -> Optional[str]:
        current_state: Optional[State] = self.get_current_state()
        if current_state is None:
            return

        self.transition(current_state.on_collision(enter = enter))

    def transition(self, new_key: Optional[str]) -> None:
        if new_key is None:
            return

        # End the current state if present.
        if self.current_key is not None:
            self.states[self.current_key].end()

        # Update the current state.
        self.current_key = new_key

        # Start the new current state.
        self.states[self.current_key].start()

    def update(self, dt: float) -> None:
        # Just return if there's no current state.
        if self.current_key is None:
            return

        # Call the current state's update method.
        self.transition(self.states[self.current_key].update(dt = dt))