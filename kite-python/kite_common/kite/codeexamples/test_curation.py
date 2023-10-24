#!/usr/bin/env python
import unittest

from . import extract


class TestCuratedSnippetExtraction(unittest.TestCase):
    def test_print_call(self):
        code = """
from requests import get
print get("http://mock.kite.com/text")
"""

        expected_snippets = [
            {
                'incantations': [
                    ("requests.get", ["__builtin__.str"], {}),
                ],
            }
        ]

        self._check_snippets(code, expected_snippets)

    def test_inline_call_attribute(self):
        code = """
from requests import get
print get("http://mock.kite.com/text").encoding
"""

        expected_snippets = [
            {
                'incantations': [
                    ("requests.get", ["__builtin__.str"], {}),
                ],
                'attributes': ["requests.get"]
            }
        ]

        self._check_snippets(code, expected_snippets)

    def test_attributes(self):
        code = """
import string
print string.uppercase
"""

        expected_snippets = [
            {
                'attributes': ["string.uppercase"]
            }
        ]

        self._check_snippets(code, expected_snippets)

    def test_multiple_functions(self):
        code = """
import inspect
def f1():
    f2()

def f2():
    s = inspect.stack()
    print "===Current function==="
    print "line number:", s[0][2]
    print "function name:", s[0][3]

    print "\\n===Caller function==="
    print "line number:", s[1][2]
    print "function name:", s[1][3]

    print "\\n===Outermost call==="
    print "line number:", s[2][2]
    print "function name:", s[2][3]

f1()
"""

        expected_snippets = [
            {
                'incantations': [
                    ("inspect.stack", [], {}),
                ],
                'attributes': ["inspect.stack"]
            }
        ]

        self._check_snippets(code, expected_snippets)

    def _check_snippets(self, code, expected):
        snippets = extract.curated_snippets(code)
        self.assertEqual(
            len(expected), len(snippets),
            "expected %d, got %d (expected %s got %s)" % (len(expected), len(snippets), expected, [x.to_json() for x in snippets]))

        for idx, snippet in enumerate(snippets):
            incantations = expected[idx].get('incantations', [])
            decorators = expected[idx].get('decorators', [])
            attributes = expected[idx].get('attributes', [])

            self.assertEqual(
                len(snippet.incantations),
                len(incantations),
                f"expected {incantations} incantations got {[x.to_json() for x in snippet.incantations]}",
            )
            self.assertEqual(
                len(snippet.decorators),
                len(decorators),
                f"expected {decorators} decorators got {[x.to_json() for x in snippet.decorators]}",
            )
            self.assertEqual(
                len(snippet.attributes),
                len(attributes),
                f"expected {attributes} attributes got {snippet.attributes}",
            )

            self._check_incantations(incantations, snippet.incantations)
            self._check_incantations(decorators, snippet.decorators)
            for attr in attributes:
                self.assertIn(attr, snippet.attributes, f"expected {attr} in attributes")


    def _check_incantations(self, expected, incantations):
        snippet_map = {inc.example_of: inc for inc in incantations}
        for name, args, kwargs in expected:
            self.assertIn(name, snippet_map, f"expected {name} to be in {snippet_map}")

            inc = snippet_map[name]
            self.assertEqual(len(args), inc.num_args,
                             "expected %d args, got %d" % (len(args), inc.num_args))

            for idx in range(len(args)):
                self.assertEqual(
                    args[idx],
                    inc.args[idx]['Type'],
                    f"expected {args[idx]}, got {inc.args[idx]['Type']}",
                )

            self.assertEqual(len(kwargs), inc.num_keyword_args,
                             "expected %d args, got %d" % (len(kwargs), inc.num_keyword_args))

            for kwarg in inc.kwargs:
                self.assertIn(
                    kwarg['Key'],
                    kwargs,
                    f"unexpected kwarg {kwarg['Key']}, expected one of {kwargs}",
                )


if __name__ == "__main__":
    unittest.main()
