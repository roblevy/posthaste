from __future__ import annotations  # Help type hints with circular depencies
import abc
from enum import Enum
import re
from typing import List


class StateComplete(Exception):
    pass


class StateType(Enum):
    # FROM, WHERE etc.
    SECTION = 1
    # SELECT, INSERT, UPDATE
    QUERY_TYPE = 2


class StateTransitionType(Enum):
    REPLACE = 1
    APPEND = 2


class StateTransition:
    def __init__(self, to: State, transition_type: StateTransitionType):
        self.to = to
        self.type = transition_type


class _StateBase:
    def __init__(self, name: str, _type: StateType = None):
        self.name: str = name
        self.type: StateType = _type

    def __repr__(self):
        return self.name

    @abc.abstractmethod
    def next(self, buffer: str, next_char: str) -> StateTransition:
        """
        Given the SQL read since this state was entered, and the character
        which will follow, where do we go next?
        """


class NoState(_StateBase):
    def __init__(self):
        super().__init__("NONE", None)

    def next(self, buffer: str, next_char: str) -> StateTransition:
        """
        Look for one of the QUERY_TYPE states, followed by whitespace.
        """
        buffer = buffer + next_char
        if re.match(r"SELECT\s", buffer):
            return StateTransition(
                to=State.SELECT, transition_type=StateTransitionType.REPLACE
            )
        elif re.match(r"FROM\s", buffer):
            return StateTransition(
                to=State.FROM, transition_type=StateTransitionType.REPLACE
            )
        elif re.match(r"INSERT\s", buffer):
            raise NotImplementedError
        elif re.match(r"UPDATE\s", buffer):
            raise NotImplementedError


class CommaSeparatedState:
    def next(self, buffer: str, next_char: str) -> StateTransition:
        """
        Do nothing until we have two whitespace-separated word-characters. It's
        important to look ahead using `next_char` so we don't gobble up the
        first character of the next state.

        TODO: This doesn't do anything yet
        TODO: How will I detect the end of a comma-separated list once various
        types of quoting are allowed?
        """
        if re.search(r"\w\s\w", buffer + next_char):
            raise StateComplete


class SelectState(CommaSeparatedState, _StateBase):
    def __init__(self):
        super().__init__("SELECT", StateType.QUERY_TYPE)


class FromState(_StateBase):
    def __init__(self):
        super().__init__("FROM", StateType.SECTION)

    def next(self, buffer: str, next_char: str) -> StateTransition:
        """
        TODO: This doesn't do anything yet.
        """
        pass


class State:
    """
    A list of allowed states. All code using this module should only refer to
    states using one of the elements of this enumeration.
    """

    COMMA_SEPARATED = CommaSeparatedState()
    FROM = FromState()
    NONE = NoState()
    SELECT = SelectState()


class StateStack:
    """
    A standard stack where None is represented throughout as State.NONE.
    """

    def __init__(self):
        self.stack: List[State] = []

    def __eq__(self, other):
        return other == self.stack

    def __repr__(self):
        return str(self.stack)

    def top(self) -> State:
        """
        The top of the stack, or State.NONE if it's empty
        """
        try:
            return self.stack[-1]
        except IndexError:
            return State.NONE

    def push(self, state: State) -> None:
        """
        Add to the stack. State.NONE has no effect.
        """
        if state != State.NONE:
            self.stack.append(state)

    def pop(self) -> State:
        """
        Pop from the top of the stack, or return State.NONE if it's empty
        """
        try:
            return self.stack.pop()
        except IndexError:
            return State.NONE

    def queue(self, index=None) -> List[State]:
        """
        Every element except the last, in reverse order.

        (A, B, C, D).queue() -> (C, B, A)

        If the queue is empty, return State.NONE
        """
        try:
            without_final = self.stack[:-1]
        except IndexError:
            # Stack is empty
            return State.NONE
        _queue = list(reversed(without_final))
        if index is None:
            index = slice(None)
        try:
            return _queue[index]
        except IndexError:
            return State.NONE
