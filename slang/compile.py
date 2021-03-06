from io import StringIO
from slang.atom import atom
import unittest

__fresh = 0
def _fresh():
    global __fresh
    __fresh += 1
    return '_slang_' + str(__fresh)

class CompileException(Exception):
    pass

def compile(expr):
    if (not isinstance(expr, list)
        or len(expr) == 0
        or expr[0] != atom('module')):
        raise CompileException()

    scope = set()
    io = StringIO()
    io.write('from slang.atom import atom as _slang_atom\n')
    io.write('_slang_bool = bool\n')
    for e in expr[1:]:
        if isinstance(e, list) and len(e) != 0 and e[0] == atom('def'):
            if len(e) != 3:
                raise CompileException()
            if not isinstance(e[1], atom):
                raise CompileException()
            scope.add(e[1])
            value = _compile(io, '', e[2], scope)
            io.write(e[1].name + ' = ' + value + '\n')
        else:
            _compile(io, '', e, scope)
    return io.getvalue()

def _compile(io, indent, expr, scope):
    if isinstance(expr, list):
        if len(expr) != 0 and isinstance(expr[0], atom):
            if expr[0].name == 'fn':
                return _compile_fn(io, indent, expr, scope)
            elif expr[0].name == 'let':
                return _compile_let(io, indent, expr, scope)
            elif expr[0].name == 'if':
                return _compile_if(io, indent, expr, scope)
            elif expr[0].name == 'quote':
                return _compile_quote(io, indent, expr, scope)
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

def _compile_let(io, indent, expr, scope):
    if len(expr) != 4:
        raise CompileException()
    iife = [[atom('fn'), [expr[1]], expr[3]], expr[2]]
    return _compile(io, indent, iife, scope)

def _compile_if(io, indent, expr, scope):
    if len(expr) != 4:
        raise CompileException()
    id = _fresh()
    cond = _compile(io, indent, expr[1], scope)
    io.write(indent + 'assert isinstance(' + cond + ', _slang_bool)\n')
    io.write(indent + 'if ' + cond + ':\n')
    true = _compile(io, indent + '    ', expr[2], scope)
    io.write(indent + '    ' + id + ' = ' + true + '\n')
    io.write(indent + 'else:\n')
    false = _compile(io, indent + '    ', expr[3], scope)
    io.write(indent + '    ' + id + ' = ' + false + '\n')
    return id

def _compile_quote(io, indent, expr, scope):
    def quote(expr):
        if isinstance(expr, list):
            return '[' + ', '.join(quote(e) for e in expr) + ']'
        elif isinstance(expr, atom):
            return '_slang_atom(' + repr(expr.name) + ')'
        else:
            raise CompileException()
    id = _fresh()
    io.write(indent + id + ' = ' + quote(expr[1]) + '\n')
    return id

def _compile_call(io, indent, expr, scope):
    if len(expr) == 0:
        raise CompileException()
    func = _compile(io, indent, expr[0], scope)
    args = [_compile(io, indent, e, scope) for e in expr[1:]]
    id = _fresh()
    io.write(indent + id + ' = ' + func + '(' + ', '.join(args) + ')\n')
    return id

def _compile_var(io, indent, expr, scope):
    if expr not in scope:
        raise CompileException()
    id = _fresh()
    io.write(indent + id + ' = ' + expr.name + '\n')
    return id

class CompileTest(unittest.TestCase):
    def test_empty_list(self):
        with self.assertRaises(CompileException):
            compile([atom('module'), []])

    def test_not_in_scope(self):
        with self.assertRaises(CompileException):
            compile([atom('module'), atom('a')])

    def test_bad_lambda(self):
        with self.assertRaises(CompileException):
            compile([atom('module'), [atom('fn')]])
        with self.assertRaises(CompileException):
            compile([atom('module'), [atom('fn'), atom('a'), atom('a')]])
        with self.assertRaises(CompileException):
            compile([atom('module'), [atom('fn'), [atom('a'), []], atom('a')]])
