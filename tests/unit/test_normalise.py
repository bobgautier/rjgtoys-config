
from rjgtoys.thing import Thing
from rjgtoys.config._ops import config_normalise, normalise_defaults

def test_normalise_defaults_missing():

    data = Thing(a=1)
    assert normalise_defaults(data) == {}

def test_normalise_defaults_simple():

    defaults = Thing(b=2)

    expected = Thing(
                defaults=Thing(),
                __view__=Thing()
                )
    expected.update(defaults)


    data = Thing(
            defaults=defaults,
            a=1
        )

    result = normalise_defaults(data)

    assert result == expected
    assert result is not expected   # It's a copy

def test_config_normalise_triv():

    data = Thing(a=1)

    result = config_normalise(data)

    assert result == Thing(
        defaults=Thing(),
        a=1,
        __view__=Thing()
        )

def test_config_normalise_easy():

    views = Thing({
        'x.y': Thing(x='a')
    })

    defaults = Thing(
        b=2,
        __view__=views
    )

    data = Thing(
        defaults=defaults,
        a=1
    )

    result = config_normalise(data)

    # Expect the view definition to be copied up

    assert result == Thing(
        defaults=Thing(
            defaults=Thing(),
            b=2,
            __view__=views
        ),
        a=1,
        __view__=views
    )

def test_config_normalise_merging():

    views = Thing({
        'x.y': Thing(x='a')
    })

    defaults = Thing(
        b=2,
        __view__=views
    )

    data = Thing(
        defaults=defaults,
        a=1,
        __view__=Thing({
            'x.z': Thing(z='b')
        })
    )

    result = config_normalise(data)

    # Expect the view definition to be copied up

    assert result == Thing(
        defaults=Thing(
            defaults=Thing(),
            b=2,
            __view__=views
        ),
        a=1,
        __view__=Thing({
                'x.y': Thing(x='a'),
                'x.z': Thing(z='b')
        })
    )
