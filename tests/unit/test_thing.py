import pytest

from rjgtoys.config.thing import Thing


def test_thing():

    t = Thing(a=1, b=2)

    assert t.a == 1
    assert t.b == 2

    assert t['a'] == 1
    assert t['b'] == 2


def test_thing_path():

    t = Thing(a=1, b=2)
    tt = Thing(t=t, c=3)

    assert tt.t.a == 1
    assert tt.t.b == 2
    assert tt.c == 3

    assert tt['t.a'] == 1
    assert tt['t.b'] == 2
    assert tt['c'] == 3


def test_thing_from_obj():

    f = Thing.from_object

    assert f(1) == 1

    assert f((1,2)) == (1,2)

    assert f([1,2]) == [1,2]

    assert f(dict(a=1, b=2)) == Thing(a=1, b=2)

    assert f(dict(sub=dict(a=1, b=2), c=3)) == Thing(
        sub=Thing(a=1, b=2),
        c=3
    )
