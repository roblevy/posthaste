import pytest

from posthaste.states import StateStack
from posthaste.states import State


@pytest.fixture
def state_stack():
    ss = StateStack()
    for x in ["a", "b", "c", "d"]:
        ss.push(x)
    return ss


def test_empty():
    ss = StateStack()
    assert ss == []
    assert ss == [State.NONE]


def test_push():
    ss = StateStack()
    ss.push("A")
    assert ss == ["A"]
    ss.push("B")
    assert ss == ["A", "B"]


def test_pop():
    ss = StateStack()
    ss.push("A")
    ss.push("B")
    popped = ss.pop()
    assert popped == "B"
    popped = ss.pop()
    assert popped == "A"
    assert ss == []
    assert ss == [State.NONE]
    ss.push("D")
    assert ss == ["D"]


def test_queue(state_stack):
    assert state_stack.queue() == ["c", "b", "a"]
    assert state_stack.queue(0) == "c"
    assert state_stack.queue(1) == "b"


def test_queue_bad_index(state_stack):
    assert state_stack.queue(4) == State.NONE
