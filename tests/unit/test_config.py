"""

Tests for the config machinery.

"""

from rjgtoys.config._config import config_resolve, config_merge

def test_config_merge_to_empty():
    """Merging to an empty destination just copies."""

    part =dict(a=1)

    dest = dict()

    config_merge(part, dest)

    assert dest == part

def test_config_merge_simple():
    """Merging simple values works."""

    part = dict(p1=1, common1='part')

    dest = dict(p2=2, common1='dest')

    config_merge(part, dest)

    assert dest == dict(p1=1, p2=2, common1='part')


def test_config_merge_mapping():
    """Merging a mapping merges the mappings."""

    part = dict(
        frompart='part',
        common=dict(
            frompart=1,
            final='part'
        )
    )

    dest = dict(
        fromdest='dest',
        common=dict(
            fromdest=2,
            final='dest'
        )
    )

    config_merge(part, dest)

    assert dest == dict(
        frompart='part',
        fromdest='dest',
        common=dict(
            frompart=1,
            fromdest=2,
            final='part'
        )
    )


def test_config_resolve_triv():
    """Resolution works when there are no defaults."""

    data = dict(a=1, b='two')

    result = config_resolve(data)

    assert result == data

def test_config_resolve_simple():
    """A simple resolution case works."""

    data = dict(
        defaults=[
            dict(a=0,b='absent', c=3)
            ],
        a=1,
        b='two'
        )

    result = config_resolve(data)

    assert result == dict(
        a=1,
        b='two',
        c=3
    )

def test_config_resolve_nested():
    """Resolve works when there are two levels of defaulting."""

    data = dict(
        defaults=[
            dict(
                defaults=[
                    dict(a=0, b=1, c=3, d=4)
                ],
                e=5,
                f=6
            )
        ],
        a='zero',
        e='five'
    )

    result = config_resolve(data)

    assert result == dict(
        a='zero',
        b=1,
        c=3,
        d=4,
        e='five',
        f=6
    )
