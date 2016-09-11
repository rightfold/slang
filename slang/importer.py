from importlib.abc import Finder, Loader
import os.path
import sys
from types import ModuleType as module

class SlangFinder(Finder):
    def find_module(self, fullname, path=None):
        if path is None:
            return None
        base_name = fullname.split('.')[-1]
        for dir in path:
            source_path = '{}/{}.slang'.format(dir, base_name)
            if os.path.exists(source_path):
                return SlangLoader(source_path)
        return None

class SlangLoader(Loader):
    def __init__(self, source_path):
        self.source_path = source_path

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        m = module(fullname)
        sys.modules[fullname] = m

        from slang.compile import compile
        from slang.read import lex, parse
        with open(self.source_path, 'r', encoding='utf8') as file:
            slang = file.read()
        python = compile(parse(lex(slang)))

        exec(python, m.__dict__)
