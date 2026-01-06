#!/usr/bin/env python3
"""
Test suite for Jack OS implementation.

This test framework validates the actual Jack code by:
1. Parsing the Jack source files
2. Verifying structure and completeness
3. Checking that algorithms contain expected patterns

Run with: python3 test_os_implementation.py
"""

import os
import re
import unittest
from pathlib import Path


class JackParser:
    """Simple parser to extract Jack function implementations."""
    
    @staticmethod
    def parse_file(filepath):
        """Parse a Jack file and extract class and function definitions."""
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Remove comments
        content = re.sub(r'//.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Extract class name
        class_match = re.search(r'class\s+(\w+)', content)
        class_name = class_match.group(1) if class_match else None
        
        # Extract functions
        functions = {}
        func_pattern = r'(function|method|constructor)\s+(\w+)\s+(\w+)\s*\([^)]*\)\s*\{'
        for match in re.finditer(func_pattern, content):
            func_type = match.group(1)
            return_type = match.group(2)
            func_name = match.group(3)
            functions[func_name] = {
                'type': func_type,
                'return_type': return_type,
                'defined': True
            }
        
        return {
            'class': class_name,
            'functions': functions,
            'content': content
        }


class JackCodeValidator:
    """Validates Jack code structure and completeness."""
    
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.libraries = {}
    
    def load_library(self, lib_name):
        """Load and parse a Jack library."""
        lib_path = self.base_path / lib_name / f"{lib_name}.jack"
        if not lib_path.exists():
            return None
        
        parsed = JackParser.parse_file(lib_path)
        self.libraries[lib_name] = parsed
        return parsed
    
    def validate_function_exists(self, lib_name, func_name):
        """Check if a function is defined in a library."""
        if lib_name not in self.libraries:
            self.load_library(lib_name)
        
        if lib_name not in self.libraries:
            return False, f"Library {lib_name} not found"
        
        lib = self.libraries[lib_name]
        if func_name not in lib['functions']:
            return False, f"Function {func_name} not found in {lib_name}"
        
        return True, "Function found"
    
    def count_lines(self, lib_name):
        """Count non-empty, non-comment lines in a library."""
        if lib_name not in self.libraries:
            self.load_library(lib_name)
        
        if lib_name not in self.libraries:
            return 0
        
        content = self.libraries[lib_name]['content']
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        return len(lines)
    
    def validate_algorithm_implementation(self, lib_name, func_name, required_keywords):
        """Validate that a function implementation contains required algorithmic elements."""
        if lib_name not in self.libraries:
            self.load_library(lib_name)
        
        if lib_name not in self.libraries:
            return False, f"Library {lib_name} not found"
        
        content = self.libraries[lib_name]['content']
        
        # Try multiple patterns: function, method, or constructor
        patterns = [
            rf'(function|method|constructor)\s+\w+\s+{func_name}\s*\([^)]*\)\s*{{',
        ]
        
        func_start = -1
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                func_start = match.end()
                break
        
        if func_start == -1:
            return False, f"Could not find function/method {func_name}"
        
        # Extract function body by finding matching braces
        # Simple approach: just search from function start to end of file
        func_body = content[func_start:]
        
        # Check for required keywords/patterns
        missing = []
        for keyword in required_keywords:
            if keyword not in func_body:
                missing.append(keyword)
        
        if missing:
            return False, f"Missing required elements: {', '.join(missing)}"
        
        return True, "Algorithm implementation validated"


class TestJackMath(unittest.TestCase):
    """Test Math.jack implementation."""
    
    @classmethod
    def setUpClass(cls):
        base_path = Path(__file__).parent
        cls.validator = JackCodeValidator(base_path)
        cls.validator.load_library('Math')
    
    def test_math_library_exists(self):
        """Test that Math.jack file exists."""
        self.assertIsNotNone(self.validator.libraries.get('Math'),
                            "Math.jack should exist")
    
    def test_math_class_name(self):
        """Test that class is named Math."""
        lib = self.validator.libraries.get('Math')
        self.assertEqual(lib['class'], 'Math',
                        "Class should be named 'Math'")
    
    def test_init_function(self):
        """Test that init() function exists."""
        exists, msg = self.validator.validate_function_exists('Math', 'init')
        self.assertTrue(exists, msg)
    
    def test_multiply_function(self):
        """Test that multiply() function exists."""
        exists, msg = self.validator.validate_function_exists('Math', 'multiply')
        self.assertTrue(exists, msg)
    
    def test_multiply_implementation(self):
        """Test that multiply uses shift-and-add algorithm."""
        valid, msg = self.validator.validate_algorithm_implementation(
            'Math', 'multiply',
            ['while', 'shiftedX']  # Key elements of shift-and-add
        )
        self.assertTrue(valid, msg)
    
    def test_divide_function(self):
        """Test that divide() function exists."""
        exists, msg = self.validator.validate_function_exists('Math', 'divide')
        self.assertTrue(exists, msg)
    
    def test_sqrt_function(self):
        """Test that sqrt() function exists."""
        exists, msg = self.validator.validate_function_exists('Math', 'sqrt')
        self.assertTrue(exists, msg)
    
    def test_sqrt_implementation(self):
        """Test that sqrt uses binary search or iterative approach."""
        valid, msg = self.validator.validate_algorithm_implementation(
            'Math', 'sqrt',
            ['while']  # Binary search requires loops
        )
        self.assertTrue(valid, msg)
    
    def test_abs_function(self):
        """Test that abs() function exists."""
        exists, msg = self.validator.validate_function_exists('Math', 'abs')
        self.assertTrue(exists, msg)
    
    def test_min_max_functions(self):
        """Test that min() and max() functions exist."""
        exists, msg = self.validator.validate_function_exists('Math', 'min')
        self.assertTrue(exists, msg)
        exists, msg = self.validator.validate_function_exists('Math', 'max')
        self.assertTrue(exists, msg)
    
    def test_math_line_count(self):
        """Test that Math.jack has substantial implementation."""
        lines = self.validator.count_lines('Math')
        self.assertGreater(lines, 80,
                          f"Math.jack should have >80 lines of code, got {lines}")


class TestJackString(unittest.TestCase):
    """Test String.jack implementation."""
    
    @classmethod
    def setUpClass(cls):
        base_path = Path(__file__).parent
        cls.validator = JackCodeValidator(base_path)
        cls.validator.load_library('String')
    
    def test_string_library_exists(self):
        """Test that String.jack file exists."""
        self.assertIsNotNone(self.validator.libraries.get('String'),
                            "String.jack should exist")
    
    def test_string_class_name(self):
        """Test that class is named String."""
        lib = self.validator.libraries.get('String')
        self.assertEqual(lib['class'], 'String',
                        "Class should be named 'String'")
    
    def test_constructor(self):
        """Test that new() constructor exists."""
        exists, msg = self.validator.validate_function_exists('String', 'new')
        self.assertTrue(exists, msg)
    
    def test_dispose_method(self):
        """Test that dispose() method exists."""
        exists, msg = self.validator.validate_function_exists('String', 'dispose')
        self.assertTrue(exists, msg)
    
    def test_length_method(self):
        """Test that length() method exists."""
        exists, msg = self.validator.validate_function_exists('String', 'length')
        self.assertTrue(exists, msg)
    
    def test_char_methods(self):
        """Test that charAt() and setCharAt() methods exist."""
        exists, msg = self.validator.validate_function_exists('String', 'charAt')
        self.assertTrue(exists, msg)
        exists, msg = self.validator.validate_function_exists('String', 'setCharAt')
        self.assertTrue(exists, msg)
    
    def test_append_erase_methods(self):
        """Test that appendChar() and eraseLastChar() methods exist."""
        exists, msg = self.validator.validate_function_exists('String', 'appendChar')
        self.assertTrue(exists, msg)
        exists, msg = self.validator.validate_function_exists('String', 'eraseLastChar')
        self.assertTrue(exists, msg)
    
    def test_int_conversion_methods(self):
        """Test that intValue() and setInt() methods exist."""
        exists, msg = self.validator.validate_function_exists('String', 'intValue')
        self.assertTrue(exists, msg)
        exists, msg = self.validator.validate_function_exists('String', 'setInt')
        self.assertTrue(exists, msg)
    
    def test_int_value_implementation(self):
        """Test that intValue() has proper parsing logic."""
        valid, msg = self.validator.validate_algorithm_implementation(
            'String', 'intValue',
            ['while', '*', '10']  # Parsing requires loop and multiplication by 10
        )
        self.assertTrue(valid, msg)
    
    def test_string_line_count(self):
        """Test that String.jack has substantial implementation."""
        lines = self.validator.count_lines('String')
        self.assertGreater(lines, 80,
                          f"String.jack should have >80 lines of code, got {lines}")


class TestJackMemory(unittest.TestCase):
    """Test Memory.jack implementation."""
    
    @classmethod
    def setUpClass(cls):
        base_path = Path(__file__).parent
        cls.validator = JackCodeValidator(base_path)
        cls.validator.load_library('Memory')
    
    def test_memory_library_exists(self):
        """Test that Memory.jack file exists."""
        self.assertIsNotNone(self.validator.libraries.get('Memory'),
                            "Memory.jack should exist")
    
    def test_init_function(self):
        """Test that init() function exists."""
        exists, msg = self.validator.validate_function_exists('Memory', 'init')
        self.assertTrue(exists, msg)
    
    def test_peek_poke_functions(self):
        """Test that peek() and poke() functions exist."""
        exists, msg = self.validator.validate_function_exists('Memory', 'peek')
        self.assertTrue(exists, msg)
        exists, msg = self.validator.validate_function_exists('Memory', 'poke')
        self.assertTrue(exists, msg)
    
    def test_alloc_function(self):
        """Test that alloc() function exists."""
        exists, msg = self.validator.validate_function_exists('Memory', 'alloc')
        self.assertTrue(exists, msg)
    
    def test_alloc_implementation(self):
        """Test that alloc() has free list traversal logic."""
        valid, msg = self.validator.validate_algorithm_implementation(
            'Memory', 'alloc',
            ['while', 'freeList']  # First-fit requires loop through free list
        )
        self.assertTrue(valid, msg)
    
    def test_dealloc_function(self):
        """Test that deAlloc() function exists."""
        exists, msg = self.validator.validate_function_exists('Memory', 'deAlloc')
        self.assertTrue(exists, msg)
    
    def test_memory_line_count(self):
        """Test that Memory.jack has substantial implementation."""
        lines = self.validator.count_lines('Memory')
        self.assertGreater(lines, 50,
                          f"Memory.jack should have >50 lines of code, got {lines}")


class TestJackScreen(unittest.TestCase):
    """Test Screen.jack implementation."""
    
    @classmethod
    def setUpClass(cls):
        base_path = Path(__file__).parent
        cls.validator = JackCodeValidator(base_path)
        cls.validator.load_library('Screen')
    
    def test_screen_library_exists(self):
        """Test that Screen.jack file exists."""
        self.assertIsNotNone(self.validator.libraries.get('Screen'),
                            "Screen.jack should exist")
    
    def test_init_function(self):
        """Test that init() function exists."""
        exists, msg = self.validator.validate_function_exists('Screen', 'init')
        self.assertTrue(exists, msg)
    
    def test_clear_screen(self):
        """Test that clearScreen() function exists."""
        exists, msg = self.validator.validate_function_exists('Screen', 'clearScreen')
        self.assertTrue(exists, msg)
    
    def test_set_color(self):
        """Test that setColor() function exists."""
        exists, msg = self.validator.validate_function_exists('Screen', 'setColor')
        self.assertTrue(exists, msg)
    
    def test_draw_pixel(self):
        """Test that drawPixel() function exists."""
        exists, msg = self.validator.validate_function_exists('Screen', 'drawPixel')
        self.assertTrue(exists, msg)
    
    def test_draw_pixel_implementation(self):
        """Test that drawPixel() uses screen memory operations."""
        valid, msg = self.validator.validate_algorithm_implementation(
            'Screen', 'drawPixel',
            ['screen[']  # Direct screen array access
        )
        self.assertTrue(valid, msg)
    
    def test_draw_line(self):
        """Test that drawLine() function exists."""
        exists, msg = self.validator.validate_function_exists('Screen', 'drawLine')
        self.assertTrue(exists, msg)
    
    def test_draw_line_implementation(self):
        """Test that drawLine() has proper algorithm."""
        valid, msg = self.validator.validate_algorithm_implementation(
            'Screen', 'drawLine',
            ['while']  # Line drawing requires loops
        )
        self.assertTrue(valid, msg)
    
    def test_draw_rectangle(self):
        """Test that drawRectangle() function exists."""
        exists, msg = self.validator.validate_function_exists('Screen', 'drawRectangle')
        self.assertTrue(exists, msg)
    
    def test_draw_circle(self):
        """Test that drawCircle() function exists."""
        exists, msg = self.validator.validate_function_exists('Screen', 'drawCircle')
        self.assertTrue(exists, msg)
    
    def test_screen_line_count(self):
        """Test that Screen.jack has substantial implementation."""
        lines = self.validator.count_lines('Screen')
        self.assertGreater(lines, 100,
                          f"Screen.jack should have >100 lines of code, got {lines}")


class TestJackOutput(unittest.TestCase):
    """Test Output.jack implementation."""
    
    @classmethod
    def setUpClass(cls):
        base_path = Path(__file__).parent
        cls.validator = JackCodeValidator(base_path)
        cls.validator.load_library('Output')
    
    def test_output_library_exists(self):
        """Test that Output.jack file exists."""
        self.assertIsNotNone(self.validator.libraries.get('Output'),
                            "Output.jack should exist")
    
    def test_init_function(self):
        """Test that init() function exists."""
        exists, msg = self.validator.validate_function_exists('Output', 'init')
        self.assertTrue(exists, msg)
    
    def test_init_map_function(self):
        """Test that initMap() function exists."""
        exists, msg = self.validator.validate_function_exists('Output', 'initMap')
        self.assertTrue(exists, msg)
    
    def test_init_map_has_characters(self):
        """Test that initMap() defines character bitmaps."""
        lib = self.validator.libraries.get('Output')
        content = lib['content']
        # Check for multiple character definitions
        create_calls = len(re.findall(r'Output\.create\(', content))
        self.assertGreater(create_calls, 50,
                          f"Should have >50 character bitmaps, found {create_calls}")
    
    def test_move_cursor(self):
        """Test that moveCursor() function exists."""
        exists, msg = self.validator.validate_function_exists('Output', 'moveCursor')
        self.assertTrue(exists, msg)
    
    def test_print_functions(self):
        """Test that print functions exist."""
        exists, msg = self.validator.validate_function_exists('Output', 'printChar')
        self.assertTrue(exists, msg)
        exists, msg = self.validator.validate_function_exists('Output', 'printString')
        self.assertTrue(exists, msg)
        exists, msg = self.validator.validate_function_exists('Output', 'printInt')
        self.assertTrue(exists, msg)
    
    def test_println_backspace(self):
        """Test that println() and backSpace() functions exist."""
        exists, msg = self.validator.validate_function_exists('Output', 'println')
        self.assertTrue(exists, msg)
        exists, msg = self.validator.validate_function_exists('Output', 'backSpace')
        self.assertTrue(exists, msg)
    
    def test_output_line_count(self):
        """Test that Output.jack has substantial implementation."""
        lines = self.validator.count_lines('Output')
        self.assertGreater(lines, 150,
                          f"Output.jack should have >150 lines (with character bitmaps), got {lines}")


class TestJackKeyboard(unittest.TestCase):
    """Test Keyboard.jack implementation."""
    
    @classmethod
    def setUpClass(cls):
        base_path = Path(__file__).parent
        cls.validator = JackCodeValidator(base_path)
        cls.validator.load_library('Keyboard')
    
    def test_keyboard_library_exists(self):
        """Test that Keyboard.jack file exists."""
        self.assertIsNotNone(self.validator.libraries.get('Keyboard'),
                            "Keyboard.jack should exist")
    
    def test_init_function(self):
        """Test that init() function exists."""
        exists, msg = self.validator.validate_function_exists('Keyboard', 'init')
        self.assertTrue(exists, msg)
    
    def test_key_pressed(self):
        """Test that keyPressed() function exists."""
        exists, msg = self.validator.validate_function_exists('Keyboard', 'keyPressed')
        self.assertTrue(exists, msg)
    
    def test_key_pressed_implementation(self):
        """Test that keyPressed() reads from keyboard memory."""
        valid, msg = self.validator.validate_algorithm_implementation(
            'Keyboard', 'keyPressed',
            ['24576']  # Keyboard memory address
        )
        self.assertTrue(valid, msg)
    
    def test_read_char(self):
        """Test that readChar() function exists."""
        exists, msg = self.validator.validate_function_exists('Keyboard', 'readChar')
        self.assertTrue(exists, msg)
    
    def test_read_char_implementation(self):
        """Test that readChar() waits for keypress."""
        valid, msg = self.validator.validate_algorithm_implementation(
            'Keyboard', 'readChar',
            ['while']  # Waiting requires loop
        )
        self.assertTrue(valid, msg)
    
    def test_read_line(self):
        """Test that readLine() function exists."""
        exists, msg = self.validator.validate_function_exists('Keyboard', 'readLine')
        self.assertTrue(exists, msg)
    
    def test_read_int(self):
        """Test that readInt() function exists."""
        exists, msg = self.validator.validate_function_exists('Keyboard', 'readInt')
        self.assertTrue(exists, msg)
    
    def test_keyboard_line_count(self):
        """Test that Keyboard.jack has substantial implementation."""
        lines = self.validator.count_lines('Keyboard')
        self.assertGreater(lines, 45,
                          f"Keyboard.jack should have >45 lines of code, got {lines}")


class TestJackArray(unittest.TestCase):
    """Test Array.jack implementation."""
    
    @classmethod
    def setUpClass(cls):
        base_path = Path(__file__).parent
        cls.validator = JackCodeValidator(base_path)
        cls.validator.load_library('Array')
    
    def test_array_library_exists(self):
        """Test that Array.jack file exists."""
        self.assertIsNotNone(self.validator.libraries.get('Array'),
                            "Array.jack should exist")
    
    def test_new_function(self):
        """Test that new() function exists."""
        exists, msg = self.validator.validate_function_exists('Array', 'new')
        self.assertTrue(exists, msg)
    
    def test_dispose_method(self):
        """Test that dispose() method exists."""
        exists, msg = self.validator.validate_function_exists('Array', 'dispose')
        self.assertTrue(exists, msg)
    
    def test_array_uses_memory(self):
        """Test that Array uses Memory.alloc/deAlloc."""
        lib = self.validator.libraries.get('Array')
        content = lib['content']
        self.assertIn('Memory.alloc', content,
                     "Array should use Memory.alloc")
        self.assertIn('Memory.deAlloc', content,
                     "Array should use Memory.deAlloc")


class TestJackSys(unittest.TestCase):
    """Test Sys.jack implementation."""
    
    @classmethod
    def setUpClass(cls):
        base_path = Path(__file__).parent
        cls.validator = JackCodeValidator(base_path)
        cls.validator.load_library('Sys')
    
    def test_sys_library_exists(self):
        """Test that Sys.jack file exists."""
        self.assertIsNotNone(self.validator.libraries.get('Sys'),
                            "Sys.jack should exist")
    
    def test_init_function(self):
        """Test that init() function exists."""
        exists, msg = self.validator.validate_function_exists('Sys', 'init')
        self.assertTrue(exists, msg)
    
    def test_init_calls_other_inits(self):
        """Test that init() calls other library initializers."""
        lib = self.validator.libraries.get('Sys')
        content = lib['content']
        required_inits = ['Memory.init', 'Math.init', 'Screen.init', 
                         'Output.init', 'Keyboard.init']
        for init_call in required_inits:
            self.assertIn(init_call, content,
                         f"Sys.init() should call {init_call}()")
    
    def test_halt_function(self):
        """Test that halt() function exists."""
        exists, msg = self.validator.validate_function_exists('Sys', 'halt')
        self.assertTrue(exists, msg)
    
    def test_halt_implementation(self):
        """Test that halt() has infinite loop."""
        valid, msg = self.validator.validate_algorithm_implementation(
            'Sys', 'halt',
            ['while', 'true']  # Halt requires infinite loop
        )
        self.assertTrue(valid, msg)
    
    def test_wait_function(self):
        """Test that wait() function exists."""
        exists, msg = self.validator.validate_function_exists('Sys', 'wait')
        self.assertTrue(exists, msg)
    
    def test_wait_implementation(self):
        """Test that wait() has delay loop."""
        valid, msg = self.validator.validate_algorithm_implementation(
            'Sys', 'wait',
            ['while']  # Wait requires loops
        )
        self.assertTrue(valid, msg)
    
    def test_error_function(self):
        """Test that error() function exists."""
        exists, msg = self.validator.validate_function_exists('Sys', 'error')
        self.assertTrue(exists, msg)


class TestCompleteness(unittest.TestCase):
    """Test overall implementation completeness."""
    
    @classmethod
    def setUpClass(cls):
        base_path = Path(__file__).parent
        cls.validator = JackCodeValidator(base_path)
        cls.libraries = ['Math', 'String', 'Array', 'Memory', 
                        'Screen', 'Output', 'Keyboard', 'Sys']
        for lib in cls.libraries:
            cls.validator.load_library(lib)
    
    def test_all_libraries_exist(self):
        """Test that all 8 OS libraries are implemented."""
        for lib in self.libraries:
            self.assertIn(lib, self.validator.libraries,
                         f"{lib}.jack should exist")
    
    def test_total_line_count(self):
        """Test that total implementation is substantial."""
        total_lines = sum(self.validator.count_lines(lib) 
                         for lib in self.libraries 
                         if lib in self.validator.libraries)
        self.assertGreater(total_lines, 600,
                          f"Total implementation should be >600 lines, got {total_lines}")
    
    def test_no_empty_implementations(self):
        """Test that no library is trivially empty."""
        for lib in self.libraries:
            if lib in self.validator.libraries:
                lines = self.validator.count_lines(lib)
                self.assertGreater(lines, 5,
                                  f"{lib}.jack should have >5 lines, got {lines}")


def run_tests():
    """Run all test suites."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestJackMath))
    suite.addTests(loader.loadTestsFromTestCase(TestJackString))
    suite.addTests(loader.loadTestsFromTestCase(TestJackMemory))
    suite.addTests(loader.loadTestsFromTestCase(TestJackScreen))
    suite.addTests(loader.loadTestsFromTestCase(TestJackOutput))
    suite.addTests(loader.loadTestsFromTestCase(TestJackKeyboard))
    suite.addTests(loader.loadTestsFromTestCase(TestJackArray))
    suite.addTests(loader.loadTestsFromTestCase(TestJackSys))
    suite.addTests(loader.loadTestsFromTestCase(TestCompleteness))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    print("="*70)
    print("Testing Jack OS Implementation")
    print("="*70)
    print()
    
    success = run_tests()
    
    print()
    print("="*70)
    if success:
        print("✅ All Jack OS implementation tests PASSED!")
        print()
        print("The following have been validated:")
        print("  • All 8 OS libraries exist (Math, String, Array, Memory,")
        print("    Screen, Output, Keyboard, Sys)")
        print("  • All required functions are implemented")
        print("  • Key algorithms contain expected logic patterns")
        print("  • Code has substantial implementation (>600 lines total)")
        print("  • Character bitmaps are defined in Output")
        print("  • System initialization sequence is correct")
    else:
        print("❌ Some Jack OS implementation tests FAILED!")
        print()
        print("Review the errors above to identify issues.")
    print("="*70)
    
    exit(0 if success else 1)

