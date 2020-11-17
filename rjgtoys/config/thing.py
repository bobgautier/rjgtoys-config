"""

.. autoclass:: Thing

"""

import collections


class Thing(dict):
    """
    A :class:`dict`-like thing that behaves like a JavaScript object;
    attribute access and item access are equivalent.  This makes writing
    code that operates on things read from JSON or YAML much simpler
    because there's no need to use lots of square brackets and string
    quotes.

    It also understands about getting items with dots in their names:
    ``something['x.y']`` will return an item called ``x.y`` if one exists,
    but otherwise will try to return ``something['x']['y']``.

    """

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getitem__(self, name):
        """Get an item, allowing dots to separate path components."""

        try:
            return super(Thing, self).__getitem__(name)
        except KeyError:
            if '.' not in name:
                raise
            # Otherwise try harder...

        (prefix, tail) = name.split('.', 1)

        return self[prefix][tail]

    __getattr__ = __getitem__

    def merge(self, other):
        """A recursive 'update'.

        Any members that are themselves mappings or sets
        are also updated.
        """

        self.dict_merge(self, other)

    @classmethod
    def dict_merge(cls, dest, other):
        """Merge one dict-like object into another."""

#        print("merge %s into %s" % (other, dest))

        for (k, v) in other.items():
            try:
                orig = dest[k]
            except KeyError:
                dest[k] = v
                continue

            # Maybe it's another Thing, or similar

            try:
                orig.merge(v)
                continue
            except AttributeError:
                pass

            # Maybe it's a dict or similar

            if isinstance(orig, collections.abc.Mapping):
                dict_merge(orig, v)
                continue

            # Can't do lists or sets yet

            # By default, other takes precedence

            dest[k] = v

    @classmethod
    def from_object(cls, src=None, **kwargs):
        """Deep-copy src replacing all mappings by instances of cls."""

        if kwargs:
            if src is not None:
                dst = cls.from_object(src)
            else:
                dst = cls()
            dst.update(cls.from_object(kwargs))
            return dst

        if isinstance(src, cls):
            return src

        if isinstance(src, collections.abc.Mapping):
            return cls((k, cls.from_object(v)) for (k, v) in src.items())

        if isinstance(src, (str, bytes)):
            return src

        if isinstance(src, collections.abc.Iterable):
            return src.__class__(cls.from_object(item) for item in src)

        return src
