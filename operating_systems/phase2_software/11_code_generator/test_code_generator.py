#!/usr/bin/env python3
"""
Unit tests for Jack code generator components.

Tests the symbol table and VM writer modules that form the foundation
of the code generation phase.

Run with: python3 test_code_generator.py
"""

import unittest
import tempfile
import os
from symbol_table import SymbolTable
from vm_writer import VMWriter


class TestSymbolTable(unittest.TestCase):
    """Test cases for SymbolTable."""

    def setUp(self):
        """Create fresh symbol table for each test."""
        self.symbol_table = SymbolTable()

    def test_class_level_variables(self):
        """Test field and static variable tracking."""
        # Define class variables
        self.symbol_table.define('x', 'int', 'field')
        self.symbol_table.define('y', 'int', 'field')
        self.symbol_table.define('count', 'int', 'static')

        # Verify counts
        self.assertEqual(self.symbol_table.var_count('field'), 2)
        self.assertEqual(self.symbol_table.var_count('static'), 1)

        # Verify kinds
        self.assertEqual(self.symbol_table.kind_of('x'), 'field')
        self.assertEqual(self.symbol_table.kind_of('y'), 'field')
        self.assertEqual(self.symbol_table.kind_of('count'), 'static')

        # Verify types
        self.assertEqual(self.symbol_table.type_of('x'), 'int')
        self.assertEqual(self.symbol_table.type_of('y'), 'int')
        self.assertEqual(self.symbol_table.type_of('count'), 'int')

        # Verify indexes
        self.assertEqual(self.symbol_table.index_of('x'), 0)
        self.assertEqual(self.symbol_table.index_of('y'), 1)
        self.assertEqual(self.symbol_table.index_of('count'), 0)

    def test_subroutine_level_variables(self):
        """Test local and argument variable tracking."""
        self.symbol_table.start_subroutine()

        # Define subroutine variables
        self.symbol_table.define('this', 'Point', 'argument')  # Implicit for methods
        self.symbol_table.define('x', 'int', 'argument')
        self.symbol_table.define('y', 'int', 'argument')
        self.symbol_table.define('temp', 'int', 'local')
        self.symbol_table.define('result', 'int', 'local')

        # Verify counts
        self.assertEqual(self.symbol_table.var_count('argument'), 3)
        self.assertEqual(self.symbol_table.var_count('local'), 2)

        # Verify indexes
        self.assertEqual(self.symbol_table.index_of('this'), 0)
        self.assertEqual(self.symbol_table.index_of('x'), 1)
        self.assertEqual(self.symbol_table.index_of('y'), 2)
        self.assertEqual(self.symbol_table.index_of('temp'), 0)
        self.assertEqual(self.symbol_table.index_of('result'), 1)

    def test_scope_reset(self):
        """Test that start_subroutine() clears subroutine scope."""
        # First subroutine
        self.symbol_table.start_subroutine()
        self.symbol_table.define('x', 'int', 'local')
        self.symbol_table.define('y', 'int', 'local')
        self.assertEqual(self.symbol_table.var_count('local'), 2)

        # Second subroutine (should reset)
        self.symbol_table.start_subroutine()
        self.assertEqual(self.symbol_table.var_count('local'), 0)
        self.assertIsNone(self.symbol_table.kind_of('x'))
        self.assertIsNone(self.symbol_table.kind_of('y'))

        # New variables in second subroutine
        self.symbol_table.define('a', 'int', 'local')
        self.assertEqual(self.symbol_table.var_count('local'), 1)
        self.assertEqual(self.symbol_table.index_of('a'), 0)

    def test_class_variables_persist(self):
        """Test that class variables persist across subroutine resets."""
        # Define class variable
        self.symbol_table.define('count', 'int', 'static')

        # Start subroutine
        self.symbol_table.start_subroutine()
        self.symbol_table.define('x', 'int', 'local')

        # Verify class variable still exists
        self.assertEqual(self.symbol_table.kind_of('count'), 'static')
        self.assertEqual(self.symbol_table.index_of('count'), 0)

        # Reset subroutine again
        self.symbol_table.start_subroutine()

        # Class variable should still exist
        self.assertEqual(self.symbol_table.kind_of('count'), 'static')

        # But local variable should be gone
        self.assertIsNone(self.symbol_table.kind_of('x'))

    def test_variable_shadowing(self):
        """Test that subroutine variables shadow class variables."""
        # Define class variable
        self.symbol_table.define('x', 'int', 'field')

        # Start subroutine and define local with same name
        self.symbol_table.start_subroutine()
        self.symbol_table.define('x', 'int', 'local')

        # Subroutine variable should shadow class variable
        self.assertEqual(self.symbol_table.kind_of('x'), 'local')
        self.assertEqual(self.symbol_table.index_of('x'), 0)

    def test_undefined_variable(self):
        """Test lookup of undefined variables."""
        self.assertIsNone(self.symbol_table.kind_of('undefined'))
        self.assertIsNone(self.symbol_table.type_of('undefined'))
        self.assertIsNone(self.symbol_table.index_of('undefined'))

    def test_complex_class(self):
        """Test complete Point class symbol table."""
        # Class-level variables
        self.symbol_table.define('x', 'int', 'field')
        self.symbol_table.define('y', 'int', 'field')
        self.symbol_table.define('pointCount', 'int', 'static')

        # Method: move(int dx, int dy)
        self.symbol_table.start_subroutine()
        self.symbol_table.define('this', 'Point', 'argument')
        self.symbol_table.define('dx', 'int', 'argument')
        self.symbol_table.define('dy', 'int', 'argument')
        self.symbol_table.define('oldX', 'int', 'local')

        # Verify complete state
        self.assertEqual(self.symbol_table.var_count('field'), 2)
        self.assertEqual(self.symbol_table.var_count('static'), 1)
        self.assertEqual(self.symbol_table.var_count('argument'), 3)
        self.assertEqual(self.symbol_table.var_count('local'), 1)

        # Verify access to all variables
        self.assertEqual(self.symbol_table.index_of('x'), 0)
        self.assertEqual(self.symbol_table.index_of('y'), 1)
        self.assertEqual(self.symbol_table.index_of('pointCount'), 0)
        self.assertEqual(self.symbol_table.index_of('this'), 0)
        self.assertEqual(self.symbol_table.index_of('dx'), 1)
        self.assertEqual(self.symbol_table.index_of('dy'), 2)
        self.assertEqual(self.symbol_table.index_of('oldX'), 0)

    def test_invalid_kind(self):
        """Test that invalid kind raises error."""
        with self.assertRaises(ValueError):
            self.symbol_table.define('x', 'int', 'invalid_kind')


class TestVMWriter(unittest.TestCase):
    """Test cases for VMWriter."""

    def setUp(self):
        """Create temporary file for each test."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.vm', delete=False)
        self.temp_filename = self.temp_file.name
        self.temp_file.close()
        self.vm_writer = VMWriter(self.temp_filename)

    def tearDown(self):
        """Clean up temporary file."""
        if os.path.exists(self.temp_filename):
            os.unlink(self.temp_filename)

    def test_push_commands(self):
        """Test push command generation."""
        self.vm_writer.write_push('constant', 5)
        self.vm_writer.write_push('local', 0)
        self.vm_writer.write_push('argument', 2)
        self.vm_writer.write_push('this', 1)

        expected = 'push constant 5\npush local 0\npush argument 2\npush this 1\n'
        self.assertEqual(self.vm_writer.get_output(), expected)

    def test_pop_commands(self):
        """Test pop command generation."""
        self.vm_writer.write_pop('local', 0)
        self.vm_writer.write_pop('argument', 1)
        self.vm_writer.write_pop('this', 2)
        self.vm_writer.write_pop('that', 0)

        expected = 'pop local 0\npop argument 1\npop this 2\npop that 0\n'
        self.assertEqual(self.vm_writer.get_output(), expected)

    def test_arithmetic_commands(self):
        """Test arithmetic/logical command generation."""
        self.vm_writer.write_arithmetic('add')
        self.vm_writer.write_arithmetic('sub')
        self.vm_writer.write_arithmetic('neg')
        self.vm_writer.write_arithmetic('eq')
        self.vm_writer.write_arithmetic('gt')
        self.vm_writer.write_arithmetic('lt')
        self.vm_writer.write_arithmetic('and')
        self.vm_writer.write_arithmetic('or')
        self.vm_writer.write_arithmetic('not')

        expected = 'add\nsub\nneg\neq\ngt\nlt\nand\nor\nnot\n'
        self.assertEqual(self.vm_writer.get_output(), expected)

    def test_invalid_arithmetic(self):
        """Test that invalid arithmetic command raises error."""
        with self.assertRaises(ValueError):
            self.vm_writer.write_arithmetic('invalid')

    def test_label_commands(self):
        """Test label, goto, and if-goto commands."""
        self.vm_writer.write_label('LOOP_START')
        self.vm_writer.write_goto('LOOP_END')
        self.vm_writer.write_if('CONTINUE')

        expected = 'label LOOP_START\ngoto LOOP_END\nif-goto CONTINUE\n'
        self.assertEqual(self.vm_writer.get_output(), expected)

    def test_function_commands(self):
        """Test function declaration and call."""
        self.vm_writer.write_function('Main.main', 2)
        self.vm_writer.write_call('Math.multiply', 2)
        self.vm_writer.write_return()

        expected = 'function Main.main 2\ncall Math.multiply 2\nreturn\n'
        self.assertEqual(self.vm_writer.get_output(), expected)

    def test_simple_function(self):
        """Test complete simple function generation."""
        # function Main.main() { var int x; let x = 5; return; }
        self.vm_writer.write_function('Main.main', 1)
        self.vm_writer.write_push('constant', 5)
        self.vm_writer.write_pop('local', 0)
        self.vm_writer.write_push('constant', 0)
        self.vm_writer.write_return()

        expected = (
            'function Main.main 1\n'
            'push constant 5\n'
            'pop local 0\n'
            'push constant 0\n'
            'return\n'
        )
        self.assertEqual(self.vm_writer.get_output(), expected)

    def test_expression_compilation(self):
        """Test expression: (x + 5) * 3."""
        # Assuming x is local 0
        self.vm_writer.write_push('local', 0)  # x
        self.vm_writer.write_push('constant', 5)
        self.vm_writer.write_arithmetic('add')  # x + 5
        self.vm_writer.write_push('constant', 3)
        self.vm_writer.write_call('Math.multiply', 2)  # (x + 5) * 3

        expected = (
            'push local 0\n'
            'push constant 5\n'
            'add\n'
            'push constant 3\n'
            'call Math.multiply 2\n'
        )
        self.assertEqual(self.vm_writer.get_output(), expected)

    def test_if_statement(self):
        """Test if-else statement generation."""
        # if (x > 10) { y = 5; } else { y = 0; }
        self.vm_writer.write_push('local', 0)  # x
        self.vm_writer.write_push('constant', 10)
        self.vm_writer.write_arithmetic('gt')
        self.vm_writer.write_arithmetic('not')
        self.vm_writer.write_if('IF_FALSE')

        # True branch
        self.vm_writer.write_push('constant', 5)
        self.vm_writer.write_pop('local', 1)
        self.vm_writer.write_goto('IF_END')

        # False branch
        self.vm_writer.write_label('IF_FALSE')
        self.vm_writer.write_push('constant', 0)
        self.vm_writer.write_pop('local', 1)

        self.vm_writer.write_label('IF_END')

        expected = (
            'push local 0\n'
            'push constant 10\n'
            'gt\n'
            'not\n'
            'if-goto IF_FALSE\n'
            'push constant 5\n'
            'pop local 1\n'
            'goto IF_END\n'
            'label IF_FALSE\n'
            'push constant 0\n'
            'pop local 1\n'
            'label IF_END\n'
        )
        self.assertEqual(self.vm_writer.get_output(), expected)

    def test_while_loop(self):
        """Test while loop generation."""
        # while (i < 10) { i = i + 1; }
        self.vm_writer.write_label('WHILE_START')
        self.vm_writer.write_push('local', 0)  # i
        self.vm_writer.write_push('constant', 10)
        self.vm_writer.write_arithmetic('lt')
        self.vm_writer.write_arithmetic('not')
        self.vm_writer.write_if('WHILE_END')

        # Loop body
        self.vm_writer.write_push('local', 0)
        self.vm_writer.write_push('constant', 1)
        self.vm_writer.write_arithmetic('add')
        self.vm_writer.write_pop('local', 0)

        self.vm_writer.write_goto('WHILE_START')
        self.vm_writer.write_label('WHILE_END')

        expected = (
            'label WHILE_START\n'
            'push local 0\n'
            'push constant 10\n'
            'lt\n'
            'not\n'
            'if-goto WHILE_END\n'
            'push local 0\n'
            'push constant 1\n'
            'add\n'
            'pop local 0\n'
            'goto WHILE_START\n'
            'label WHILE_END\n'
        )
        self.assertEqual(self.vm_writer.get_output(), expected)

    def test_method_setup(self):
        """Test method setup code (setting THIS pointer)."""
        # Method preamble
        self.vm_writer.write_function('Point.move', 0)
        self.vm_writer.write_push('argument', 0)  # Get 'this'
        self.vm_writer.write_pop('pointer', 0)    # Set THIS

        expected = (
            'function Point.move 0\n'
            'push argument 0\n'
            'pop pointer 0\n'
        )
        self.assertEqual(self.vm_writer.get_output(), expected)

    def test_constructor_allocation(self):
        """Test constructor memory allocation."""
        # Constructor with 2 fields
        self.vm_writer.write_function('Point.new', 0)
        self.vm_writer.write_push('constant', 2)  # Number of fields
        self.vm_writer.write_call('Memory.alloc', 1)
        self.vm_writer.write_pop('pointer', 0)  # Set THIS

        expected = (
            'function Point.new 0\n'
            'push constant 2\n'
            'call Memory.alloc 1\n'
            'pop pointer 0\n'
        )
        self.assertEqual(self.vm_writer.get_output(), expected)

    def test_array_assignment(self):
        """Test array assignment: arr[i] = value."""
        # arr is local 0, i is local 1, value is 100
        self.vm_writer.write_push('local', 0)  # Base address
        self.vm_writer.write_push('local', 1)  # Index
        self.vm_writer.write_arithmetic('add')  # arr + i
        self.vm_writer.write_push('constant', 100)  # Value
        self.vm_writer.write_pop('temp', 0)  # Save value
        self.vm_writer.write_pop('pointer', 1)  # THAT = arr + i
        self.vm_writer.write_push('temp', 0)  # Restore value
        self.vm_writer.write_pop('that', 0)  # Memory[THAT] = value

        expected = (
            'push local 0\n'
            'push local 1\n'
            'add\n'
            'push constant 100\n'
            'pop temp 0\n'
            'pop pointer 1\n'
            'push temp 0\n'
            'pop that 0\n'
        )
        self.assertEqual(self.vm_writer.get_output(), expected)

    def test_file_write(self):
        """Test that close() writes to file correctly."""
        self.vm_writer.write_function('Test.test', 0)
        self.vm_writer.write_push('constant', 42)
        self.vm_writer.write_return()
        self.vm_writer.close()

        # Read file and verify
        with open(self.temp_filename, 'r') as f:
            content = f.read()

        expected = 'function Test.test 0\npush constant 42\nreturn\n'
        self.assertEqual(content, expected)

    def test_comments(self):
        """Test comment generation."""
        self.vm_writer.write_comment('This is a test')
        self.vm_writer.write_push('constant', 5)
        self.vm_writer.write_comment('Push value')

        expected = '// This is a test\npush constant 5\n// Push value\n'
        self.assertEqual(self.vm_writer.get_output(), expected)


class TestIntegration(unittest.TestCase):
    """Integration tests combining symbol table and VM writer."""

    def test_simple_assignment(self):
        """Test: var int x; let x = 5;"""
        symbol_table = SymbolTable()
        vm = VMWriter(tempfile.mktemp(suffix='.vm'))

        # Start function
        symbol_table.start_subroutine()

        # var int x
        symbol_table.define('x', 'int', 'local')

        # let x = 5
        vm.write_push('constant', 5)
        kind = symbol_table.kind_of('x')
        index = symbol_table.index_of('x')
        segment = 'local' if kind == 'local' else kind
        vm.write_pop(segment, index)

        expected = 'push constant 5\npop local 0\n'
        self.assertEqual(vm.get_output(), expected)

    def test_field_access(self):
        """Test: field int x; return x; (in method)"""
        symbol_table = SymbolTable()
        vm = VMWriter(tempfile.mktemp(suffix='.vm'))

        # field int x
        symbol_table.define('x', 'int', 'field')

        # Method setup
        symbol_table.start_subroutine()
        symbol_table.define('this', 'Point', 'argument')

        # Method preamble
        vm.write_push('argument', 0)
        vm.write_pop('pointer', 0)

        # return x (field access via THIS)
        kind = symbol_table.kind_of('x')
        index = symbol_table.index_of('x')
        segment = 'this' if kind == 'field' else kind
        vm.write_push(segment, index)
        vm.write_return()

        expected = (
            'push argument 0\n'
            'pop pointer 0\n'
            'push this 0\n'
            'return\n'
        )
        self.assertEqual(vm.get_output(), expected)


def run_tests():
    """Run all test suites."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSymbolTable))
    suite.addTests(loader.loadTestsFromTestCase(TestVMWriter))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
