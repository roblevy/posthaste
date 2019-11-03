import pytest

from posthaste.parsing import SqlParser
from posthaste.states import State

# TODO: This is currently broken due to a weirdness with EmptyState which gets
# set to [] at some point during execution. Now I come to think about it, maybe
# it doesn't need to be represented as something other than [] after all...


def test_read_one():
    sp = SqlParser("foo")
    assert sp.cursor == 0
    sp.read()
    assert sp.buffer == "f"
    assert sp.cursor == 1


def test_read_all():
    sp = SqlParser("foo")
    while sp.read():
        pass
    assert sp.buffer == "foo"
    assert sp.EOF


def test_select_state():
    sp = SqlParser("SELECT foo")
    sp._readn(5)  # SELEC
    assert sp.state_stack == []
    sp._readn(1)  # SELECT
    assert sp.state_stack == [State.SELECT]
    assert sp.buffer == ""


def test_exit_state():
    sp = SqlParser("SELECT foo FROM bar")
    sp._readn(10)  # SELECT foo
    assert sp.state_stack == [State.SELECT]
    sp._readn(1)  # SELECT foo<whitespace>
    assert sp.state_stack == []


def test_change_section():
    sp = SqlParser("SELECT foo FROM bar")
    sp._readn(14)  # SELECT foo FRO
    assert sp.state_stack == []
    sp._readn(2)  # SELECT foo FROM
    print(sp.buffer)
    assert sp.state_stack == [State.FROM]
