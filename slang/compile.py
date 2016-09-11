from io import StringIO
from slang.atom import atom
import unittest

__fresh = 0
def _fresh():
    global __fresh
    __fresh += 1
    return '_v' + str(__fresh)

class CompileException(Exception):
    pass

def compile(expr):
    scope = set()
    io = StringIO()
    _compile(io, '', expr, scope)
    return io.getvalue()

def _compile(io, indent, expr, scope):
    if isinstance(expr, list):
        if len(expr) != 0 and isinstance(expr[0], atom):
            if expr[0].name == 'fn':
                return _compile_fn(io, indent, expr, scope)
        return _compile_call(io, indent, expr, scope)
    elif isinstance(expr, atom):
        return _compile_var(io, indent, expr, scope)
    else:
        raise CompileException()

def _compile_fn(io, indent, expr, scope):
    if len(expr) != 3:
        raise CompileException()
    if (not isinstance(expr[1], list)
        or not all(isinstance(p, atom) for p in expr[1])):
        raise CompileException()
    id = _fresh()
    io.write(indent + 'def ' + id + '(' + ', '.join(p.name for p in expr[1]) + '):\n')
    body = _compile(io, indent + '    ', expr[2], scope | set(expr[1]))
    io.write(indent + '    return ' + body + '\n')
    return id

def _compile_call(io, indent, expr, scope):
    if len(expr) == 0:
        raise CompileException()
    if isinstance(expr[0], atom):
        _compile_
    func = _compile(io, indent, expr[0], scope)
    args = (_compile(io, indent, e, scope) for e in expr[1:])
    id = _fresh()
    io.write(ident + id + ' = (' + func + ')(' + ', '.join(args) + ')\n')
    return id

def _compile_var(io, indent, expr, scope):
    if expr not in scope:
        raise CompileException()
    id = _fresh()
    io.write(indent + id + ' = ' + expr.name + '\n')
    return id

class CompileTest(unittest.TestCase):
    def test(self):
        code = [atom('fn'), [atom('x')], atom('x')]
        token = object()
        scope = {}
        exec(compile(code), scope)
        self.assertEqual(scope['_v1'](token), token)

    def test_empty_list(self):
        with self.assertRaises(CompileException):
            compile([])

    def test_not_in_scope(self):
        with self.assertRaises(CompileException):
            compile(atom('a'))

    def test_bad_lambda(self):
        with self.assertRaises(CompileException):
            compile([atom('fn')])
        with self.assertRaises(CompileException):
            compile([atom('fn'), atom('a'), atom('a')])
        with self.assertRaises(CompileException):
            compile([atom('fn'), [atom('a'), []], atom('a')])
