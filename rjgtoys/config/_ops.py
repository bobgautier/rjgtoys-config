"""
Operations on config data

"""

import collections.abc

from rjgtoys.thing import Thing

from copy import deepcopy


def config_normalise(raw):
    """Normalise a config object to make it easier to process later.

    Ensure it has both 'defaults' and '__view__' entries, that
    'defaults' is a single map, and '__view__' represents a merge
    of any 'local' '__view__' with that of the 'defaults'.
    """

    result = Thing(raw)

    defaults = normalise_defaults(raw)

    result.defaults = defaults

    view = deepcopy(defaults.get('__view__', {}))
    local_view = raw.get('__view__')

    if local_view:
        config_merge(local_view, view)

    result.__view__ = view

    return result


def normalise_defaults(raw):

    try:
        defaults = raw.defaults
    except AttributeError:
        return {}

    # If only a single set of defaults, work around it

    if isinstance(defaults, collections.abc.Mapping):
        return config_normalise(defaults)

    result = {}
    for layer in defaults:
        layer = config_normalise(layer)
        config_merge(layer, result)

    return result


def config_resolve(raw):
    """Resolve 'defaults' in some raw config data."""

    # If there are no defaults to apply, just return the raw data

    defaults = resolve_defaults(raw)
    if not defaults:
        return raw

    del raw['defaults']

    # override defaults with raw data, return result

    config_merge(raw, defaults)

    return defaults


def resolve_defaults(raw):
    """Resolve 'defaults' in some raw config data."""

    # If there are no defaults to apply, just return an empty dict

#    print("resolve_defaults %s" % (raw))

    try:
        defaults = raw.defaults
    except AttributeError:
        return {}

    # If only a single set of defaults, work around it

    if isinstance(defaults, collections.abc.Mapping):
        defaults = (defaults,)

    result = {}
    for layer in defaults:
        layer = config_resolve(layer)
        config_merge(layer, result)

    return result

def config_merge(part, result):
    """Merge a set of defaults 'part' into 'result'."""

    for (key, value) in part.items():
        # If value is a mapping, any
        # existing value in result had better
        # be a mapping too.
        # Merge the mappings.
        # Otherwise, just override
        if not isinstance(value, collections.abc.Mapping):
            result[key] = value
            continue

        # See if there's an existing value

        try:
            prev = result[key]
        except KeyError:
            # No, just override
            result[key] = value
            continue

        # Merge prev and new

        config_merge(value, prev)

