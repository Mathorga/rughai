from typing import Dict, Optional

class State:
    def __init__(self) -> None:
        self.input_enabled = True

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

    def enable_input(self) -> None:
        pass

    def disable_input(self) -> None:
        pass

class StateMachine:
    def __init__(
        self,
        states: Optional[Dict[str, State]]
    ) -> None:
        self.__states: Dict[str, State] = states if states is not None else {}
        self.__current_key: Optional[str] = list(self.__states.keys())[0] if len(self.__states) > 0 else None

    def get_current_state(self) -> Optional[State]:
        """
        Returns the current state of the state machine.
        """
        if self.__current_key is None:
            return None

        return self.__states[self.__current_key]

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
        if self.__current_key is not None:
            self.__states[self.__current_key].end()

        # Update the current state.
        self.__current_key = new_key

        # Start the new current state.
        self.__states[self.__current_key].start()

    def update(self, dt: float) -> None:
        # Just return if there's no current state.
        if self.__current_key is None:
            return

        # Call the current state's update method.
        self.transition(self.__states[self.__current_key].update(dt = dt))

    def enable_input(self) -> None:
        # Just return if there's no current state.
        if self.__current_key is None:
            return

        self.__states[self.__current_key].enable_input()

    def disable_input(self) -> None:
        # Just return if there's no current state.
        if self.__current_key is None:
            return

        self.__states[self.__current_key].disable_input()