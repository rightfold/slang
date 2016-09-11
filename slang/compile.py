from slang.atom import atom
import unittest

class CompileException(Exception):
    pass

def compile(expr):
    scope = set()
    return _compile(expr, scope)

def _compile(expr, scope):
    if isinstance(expr, list):
        if len(expr) != 0 and isinstance(expr[0], atom):
            if expr[0].name == 'fn':
                return _compile_fn(expr, scope)
        return _compile_call(expr, scope)
    elif isinstance(expr, atom):
        return _compile_var(expr, scope)
    else:
        raise CompileException()

def _compile_fn(expr, scope):
    if len(expr) != 3:
        raise CompileException()
    if (not isinstance(expr[1], list)
        or not all(isinstance(p, atom) for p in expr[1])):
        raise CompileException()
    body = _compile(expr[2], scope | set(expr[1]))
    return 'lambda ' + ', '.join(p.name for p in expr[1]) + ': ' + body

def _compile_call(expr, scope):
    if len(expr) == 0:
        raise CompileException()
    if isinstance(expr[0], atom):
        _compile_
    func = _compile(expr[0], scope)
    args = (_compile(e, scope) for e in expr[1:])
    return '(' + func + ')(' + ', '.join(args) + ')'

def _compile_var(expr, scope):
    if expr not in scope:
        raise CompileException()
    return expr.name

class CompileTest(unittest.TestCase):
    def test(self):
        code = [atom('fn'), [atom('x')], atom('x')]
        token = object()
        self.assertEqual(eval(compile(code))(token), token)

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
