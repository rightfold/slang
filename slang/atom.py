import unittest
from weakref import WeakValueDictionary

_atoms = WeakValueDictionary()

class atom:
    __slots__ = '__weakref__', 'name'

    def __new__(cls, name):
        if name in _atoms:
            return _atoms[name]
        else:
            inst = super(atom, cls).__new__(cls)
            inst.name = name
            _atoms[name] = inst
            return inst

class AtomTest(unittest.TestCase):
    def test(self):
        for name in ['', 'foo', 'bar']:
            self.assertIs(atom(name), atom(name))
            self.assertIsNot(atom(name), atom('foo' + name))
            self.assertEqual(atom(name).name, name)
