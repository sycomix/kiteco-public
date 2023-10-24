import sys

from ..foo import Foo
from ..bar import Bar
from ..runtime_helper import LARGE

_PY3 = sys.version >= '3'

foo = Foo()
bar = Bar()




class Test(object):
    foo = Foo.foo if _PY3 else Foo.foo.__func__
    large = LARGE
