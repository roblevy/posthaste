from posthaste.states import StateComplete
from posthaste.states import StateStack
from posthaste.states import StateTransition
from posthaste.states import StateTransitionType


class ParsingError(Exception):
    pass


class SqlParser:
    def __init__(self, sql: str):
        self.sql = sql
        # Where are we in the current query?
        self.state_stack = StateStack()
        # The position of the character being parsed
        self.cursor: int = 0
        # The chunk being parsed
        self.buffer: str = ""

    def _readn(self, n):
        """
        Read `n` characters
        """
        return any([self.read() for _ in range(n)])

    def read(self):
        """
        Read the next character of the SQL, increment the cursor and move us on
        to the next state if that turns out to be necessary.
        """
        try:
            next_char = self.sql[self.cursor]
        except IndexError:
            return False
        self.buffer += next_char
        try:
            next_char = self.sql[self.cursor + 1]
        except IndexError:
            next_char = ""
        self.next_char = next_char
        self.cursor += 1
        self.check_state()
        return True

    def check_state(self):
        """
        Check the buffer and change the state stack if necesssary. Clear the
        buffer if a transition occurs.
        """
        try:
            transition = self.current_state.next(self.buffer, self.next_char)
        except StateComplete:
            transition = StateTransition(
                self.previous_state, StateTransitionType.REPLACE
            )
        if transition:
            self.transition_state(transition)
            self.buffer = ""

    def transition_state(self, transition):
        if transition.type == StateTransitionType.REPLACE:
            # Remove existing SECTION state
            try:
                self.state_stack.pop()
            except IndexError:
                # The state stack is already empty!
                pass
        self.state_stack.push(transition.to)

    @property
    def EOF(self):
        return self.cursor >= len(self.sql)

    @property
    def current_state(self):
        return self.state_stack.top()

    @property
    def previous_state(self):
        return self.state_stack.queue(0)
