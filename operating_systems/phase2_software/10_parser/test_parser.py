#!/usr/bin/env python3
"""
Unit tests for Jack tokenizer and parser.

Run with: python3 test_parser.py
"""

import unittest
import os
import tempfile
from tokenizer import JackTokenizer
from parser import CompilationEngine


class TestTokenizer(unittest.TestCase):
    """Test cases for JackTokenizer."""

    def test_keywords(self):
        """Test keyword recognition."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jack', delete=False) as f:
            f.write('class while return')
            filename = f.name

        try:
            tokenizer = JackTokenizer(filename)

            # class
            self.assertTrue(tokenizer.has_more_tokens())
            tokenizer.advance()
            self.assertEqual(tokenizer.token_type(), JackTokenizer.KEYWORD)
            self.assertEqual(tokenizer.keyword(), 'class')

            # while
            tokenizer.advance()
            self.assertEqual(tokenizer.token_type(), JackTokenizer.KEYWORD)
            self.assertEqual(tokenizer.keyword(), 'while')

            # return
            tokenizer.advance()
            self.assertEqual(tokenizer.token_type(), JackTokenizer.KEYWORD)
            self.assertEqual(tokenizer.keyword(), 'return')

            self.assertFalse(tokenizer.has_more_tokens())
        finally:
            os.unlink(filename)

    def test_symbols(self):
        """Test symbol recognition."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jack', delete=False) as f:
            f.write('{ } ( ) [ ]')
            filename = f.name

        try:
            tokenizer = JackTokenizer(filename)
            symbols = ['{', '}', '(', ')', '[', ']']

            for expected in symbols:
                self.assertTrue(tokenizer.has_more_tokens())
                tokenizer.advance()
                self.assertEqual(tokenizer.token_type(), JackTokenizer.SYMBOL)
                self.assertEqual(tokenizer.symbol(), expected)

            self.assertFalse(tokenizer.has_more_tokens())
        finally:
            os.unlink(filename)

    def test_identifiers(self):
        """Test identifier recognition."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jack', delete=False) as f:
            f.write('myVar _test var123')
            filename = f.name

        try:
            tokenizer = JackTokenizer(filename)
            identifiers = ['myVar', '_test', 'var123']

            for expected in identifiers:
                self.assertTrue(tokenizer.has_more_tokens())
                tokenizer.advance()
                self.assertEqual(tokenizer.token_type(), JackTokenizer.IDENTIFIER)
                self.assertEqual(tokenizer.identifier(), expected)

            self.assertFalse(tokenizer.has_more_tokens())
        finally:
            os.unlink(filename)

    def test_integer_constants(self):
        """Test integer constant recognition."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jack', delete=False) as f:
            f.write('0 123 32767')
            filename = f.name

        try:
            tokenizer = JackTokenizer(filename)
            values = [0, 123, 32767]

            for expected in values:
                self.assertTrue(tokenizer.has_more_tokens())
                tokenizer.advance()
                self.assertEqual(tokenizer.token_type(), JackTokenizer.INT_CONST)
                self.assertEqual(tokenizer.int_val(), expected)

            self.assertFalse(tokenizer.has_more_tokens())
        finally:
            os.unlink(filename)

    def test_string_constants(self):
        """Test string constant recognition."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jack', delete=False) as f:
            f.write('"hello" "world"')
            filename = f.name

        try:
            tokenizer = JackTokenizer(filename)
            strings = ['hello', 'world']

            for expected in strings:
                self.assertTrue(tokenizer.has_more_tokens())
                tokenizer.advance()
                self.assertEqual(tokenizer.token_type(), JackTokenizer.STRING_CONST)
                self.assertEqual(tokenizer.string_val(), expected)

            self.assertFalse(tokenizer.has_more_tokens())
        finally:
            os.unlink(filename)

    def test_comment_removal(self):
        """Test single-line and multi-line comment removal."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jack', delete=False) as f:
            f.write("""
                // Single-line comment
                class /* inline comment */ Main {
                    /* Multi-line
                       comment */
                    function void main() {
                        return; // end comment
                    }
                }
            """)
            filename = f.name

        try:
            tokenizer = JackTokenizer(filename)
            expected = ['class', 'Main', '{', 'function', 'void', 'main',
                       '(', ')', '{', 'return', ';', '}', '}']

            for exp in expected:
                self.assertTrue(tokenizer.has_more_tokens())
                tokenizer.advance()
                if tokenizer.token_type() == JackTokenizer.KEYWORD:
                    self.assertEqual(tokenizer.keyword(), exp)
                elif tokenizer.token_type() == JackTokenizer.SYMBOL:
                    self.assertEqual(tokenizer.symbol(), exp)
                elif tokenizer.token_type() == JackTokenizer.IDENTIFIER:
                    self.assertEqual(tokenizer.identifier(), exp)

            self.assertFalse(tokenizer.has_more_tokens())
        finally:
            os.unlink(filename)


class TestParser(unittest.TestCase):
    """Test cases for CompilationEngine."""

    def test_simple_class(self):
        """Test parsing a simple class."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jack', delete=False) as f:
            f.write("""
                class Main {
                    function void main() {
                        return;
                    }
                }
            """)
            jack_file = f.name

        xml_file = jack_file.replace('.jack', '.xml')

        try:
            # Compile
            engine = CompilationEngine(jack_file, xml_file)
            engine.compile()

            # Verify XML was created
            self.assertTrue(os.path.exists(xml_file))

            # Read XML and verify structure
            with open(xml_file, 'r') as f:
                xml_content = f.read()

            self.assertIn('<class>', xml_content)
            self.assertIn('</class>', xml_content)
            self.assertIn('<keyword> class </keyword>', xml_content)
            self.assertIn('<identifier> Main </identifier>', xml_content)
            self.assertIn('<subroutineDec>', xml_content)
            self.assertIn('<keyword> return </keyword>', xml_content)

        finally:
            os.unlink(jack_file)
            if os.path.exists(xml_file):
                os.unlink(xml_file)

    def test_class_with_variables(self):
        """Test parsing a class with field variables."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jack', delete=False) as f:
            f.write("""
                class Point {
                    field int x, y;

                    constructor Point new() {
                        return this;
                    }
                }
            """)
            jack_file = f.name

        xml_file = jack_file.replace('.jack', '.xml')

        try:
            engine = CompilationEngine(jack_file, xml_file)
            engine.compile()

            with open(xml_file, 'r') as f:
                xml_content = f.read()

            self.assertIn('<classVarDec>', xml_content)
            self.assertIn('<keyword> field </keyword>', xml_content)
            self.assertIn('<keyword> constructor </keyword>', xml_content)

        finally:
            os.unlink(jack_file)
            if os.path.exists(xml_file):
                os.unlink(xml_file)

    def test_let_statement(self):
        """Test parsing let statements."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jack', delete=False) as f:
            f.write("""
                class Main {
                    function void main() {
                        var int x;
                        let x = 5;
                        return;
                    }
                }
            """)
            jack_file = f.name

        xml_file = jack_file.replace('.jack', '.xml')

        try:
            engine = CompilationEngine(jack_file, xml_file)
            engine.compile()

            with open(xml_file, 'r') as f:
                xml_content = f.read()

            self.assertIn('<letStatement>', xml_content)
            self.assertIn('<keyword> let </keyword>', xml_content)
            self.assertIn('<symbol> = </symbol>', xml_content)

        finally:
            os.unlink(jack_file)
            if os.path.exists(xml_file):
                os.unlink(xml_file)

    def test_if_statement(self):
        """Test parsing if statements."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jack', delete=False) as f:
            f.write("""
                class Main {
                    function void main() {
                        if (true) {
                            return;
                        }
                        return;
                    }
                }
            """)
            jack_file = f.name

        xml_file = jack_file.replace('.jack', '.xml')

        try:
            engine = CompilationEngine(jack_file, xml_file)
            engine.compile()

            with open(xml_file, 'r') as f:
                xml_content = f.read()

            self.assertIn('<ifStatement>', xml_content)
            self.assertIn('<keyword> if </keyword>', xml_content)

        finally:
            os.unlink(jack_file)
            if os.path.exists(xml_file):
                os.unlink(xml_file)

    def test_while_statement(self):
        """Test parsing while statements."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jack', delete=False) as f:
            f.write("""
                class Main {
                    function void main() {
                        while (true) {
                            return;
                        }
                        return;
                    }
                }
            """)
            jack_file = f.name

        xml_file = jack_file.replace('.jack', '.xml')

        try:
            engine = CompilationEngine(jack_file, xml_file)
            engine.compile()

            with open(xml_file, 'r') as f:
                xml_content = f.read()

            self.assertIn('<whileStatement>', xml_content)
            self.assertIn('<keyword> while </keyword>', xml_content)

        finally:
            os.unlink(jack_file)
            if os.path.exists(xml_file):
                os.unlink(xml_file)

    def test_expression_with_operators(self):
        """Test parsing expressions with operators."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jack', delete=False) as f:
            f.write("""
                class Main {
                    function void main() {
                        var int x;
                        let x = 1 + 2 * 3;
                        return;
                    }
                }
            """)
            jack_file = f.name

        xml_file = jack_file.replace('.jack', '.xml')

        try:
            engine = CompilationEngine(jack_file, xml_file)
            engine.compile()

            with open(xml_file, 'r') as f:
                xml_content = f.read()

            self.assertIn('<expression>', xml_content)
            self.assertIn('<symbol> + </symbol>', xml_content)
            self.assertIn('<symbol> * </symbol>', xml_content)

        finally:
            os.unlink(jack_file)
            if os.path.exists(xml_file):
                os.unlink(xml_file)

    def test_array_access(self):
        """Test parsing array access."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jack', delete=False) as f:
            f.write("""
                class Main {
                    function void main() {
                        var Array a;
                        var int x;
                        let x = a[0];
                        return;
                    }
                }
            """)
            jack_file = f.name

        xml_file = jack_file.replace('.jack', '.xml')

        try:
            engine = CompilationEngine(jack_file, xml_file)
            engine.compile()

            with open(xml_file, 'r') as f:
                xml_content = f.read()

            self.assertIn('<symbol> [ </symbol>', xml_content)
            self.assertIn('<symbol> ] </symbol>', xml_content)

        finally:
            os.unlink(jack_file)
            if os.path.exists(xml_file):
                os.unlink(xml_file)


def run_tests():
    """Run all test suites."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTokenizer))
    suite.addTests(loader.loadTestsFromTestCase(TestParser))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
