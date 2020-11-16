
from rjgtoys.config._config import config_normalise, normalise_defaults

def test_normalise_defaults_missing():

    data = dict(a=1)
    assert normalise_defaults(data) == {}

def test_normalise_defaults_simple():

    defaults = dict(b=2)

    expected = dict(
                defaults={},
                __view__={}
                )
    expected.update(defaults)


    data = dict(
            defaults=defaults,
            a=1
        )

    result = normalise_defaults(data)

    assert result == expected
    assert result is not expected   # It's a copy

def test_config_normalise_triv():

    data = dict(a=1)

    result = config_normalise(data)

    assert result == dict(
        defaults={},
        a=1,
        __view__={}
        )

def test_config_normalise_easy():

    views = {
        'x.y': dict(x='a')
    }

    defaults = dict(
        b=2,
        __view__=views
    )

    data = dict(
        defaults=defaults,
        a=1
    )

    result = config_normalise(data)

    # Expect the view definition to be copied up

    assert result == dict(
        defaults=dict(
            defaults={},
            b=2,
            __view__=views
        ),
        a=1,
        __view__=views
    )

def test_config_normalise_merging():

    views = {
        'x.y': dict(x='a')
    }

    defaults = dict(
        b=2,
        __view__=views
    )

    data = dict(
        defaults=defaults,
        a=1,
        __view__={
            'x.z': dict(z='b')
        }
    )

    result = config_normalise(data)

    # Expect the view definition to be copied up

    assert result == dict(
        defaults=dict(
            defaults={},
            b=2,
            __view__=views
        ),
        a=1,
        __view__={
                'x.y': dict(x='a'),
                'x.z': dict(z='b')
        }
    )
