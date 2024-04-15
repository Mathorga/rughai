class State ():
    """
    State interface, defines all mandatory methods for state implementations.
    This class cannot be used as is, you must always define a specialization through inheritance.
    """

    __slots__ = ()

    def start(self) -> None:
        pass

    def on_animation_end(self) -> str | None:
        pass

    def on_collision(self, tags: list[str], enter: bool) -> str | None:
        pass

    def update(self, dt: float) -> str | None:
        pass

    def end(self) -> None:
        pass

class StateMachine:
    """
    Base state machine class, handles state transition and events pass-through to states.
    This class can be used as-is or specialized through inheritance.
    """

    __slots__ = (
        "states",
        "current_key"
    )

    def __init__(
        self,
        states: dict[str, State] | None
    ) -> None:
        self.states: dict[str, State] = states if states is not None else {}
        self.current_key: str | None = list(self.states.keys())[0] if len(self.states) > 0 else None

        current_state: State | None = self.get_current_state()
        if current_state is None:
            return

        current_state.start()

    def get_current_state(self) -> State | None:
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
            # End current state if any.
            if self.current_key is not None:
                self.states[self.current_key].end()

            self.current_key = key

            # Call the new state's start method.
            self.states[self.current_key].start()

    def on_animation_end(self) -> None:
        current_state: State | None = self.get_current_state()
        if current_state is None:
            return

        self.transition(current_state.on_animation_end())

    def on_collision(self, tags: list[str], enter: bool) -> None:
        current_state: State | None = self.get_current_state()
        if current_state is None:
            return

        self.transition(current_state.on_collision(tags = tags, enter = enter))

    def transition(self, key: str | None) -> None:
        """
        Sets a new state from the provided key.
        No state is set if [key] is null.
        """

        # Exit condition: key is not defined.
        if key is None:
            return

        # Exit condition: the provided key does not match any state.
        if not key in self.states:
            return

        # End the current state if present.
        if self.current_key is not None:
            self.states[self.current_key].end()

        # Update the current state.
        self.current_key = key

        # Start the new current state.
        self.states[self.current_key].start()

    def update(self, dt: float) -> None:
        # Just return if there's no current state.
        if self.current_key is None:
            return

        # Call the current state's update method.
        self.transition(self.states[self.current_key].update(dt = dt))