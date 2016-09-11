from slang.atom import atom
import unittest

class ParseException(Exception):
    pass

class lexeme:
    __slots__ = 'type', 'value'

    def __init__(self, type, value=None):
        self.type = type
        self.value = value

def lex(text):
    while True:
        text = text.lstrip()
        if text == '':
            while True:
                yield lexeme('eof')

        if text[0] == '(':
            text = text[1:]
            yield lexeme('(')
            continue
        elif text[0] == ')':
            text = text[1:]
            yield lexeme(')')
            yield lexeme(')')
            continue
        elif text[0].isalpha():
            name = ''
            while text != '' and text[0].isalpha():
                name += text[0]
                text = text[1:]
            yield lexeme('atom', atom(name))
            continue

        raise ParseException()

def parse(lexemes):
    lexeme = next(lexemes)
    if lexeme.type == '(':
        result = []
        while True:
            try:
                item = parse(lexemes)
            except ParseException:
                break
            result.append(item)
        if next(lexemes).type != ')':
            raise ParseException()
        return result
    elif lexeme.type == 'atom':
        return lexeme.value
    raise ParseException()

class ParseTest(unittest.TestCase):
    def test(self):
        self.assertEqual(parse(lex('()')), [])
        self.assertEqual(parse(lex('(())')), [[]])
        self.assertEqual(parse(lex('(()())')), [[], []])
        self.assertEqual(parse(lex('a')), atom('a'))
        self.assertEqual(parse(lex('(ab cd)')), [atom('ab'), atom('cd')])
