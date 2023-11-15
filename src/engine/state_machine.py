from typing import Dict, Optional

class State:
    def start(self) -> None:
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
        self.__states: Dict[str, State] = states if states is not None else {}
        self.__current_key: Optional[str] = None

    def transition(self, new_key: str) -> None:
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
        new_key: Optional[str] = self.__states[self.__current_key].update(dt = dt)

        if new_key is not None:
            self.transition(new_key = new_key)