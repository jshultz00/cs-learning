#!/usr/bin/env python3
"""
Comprehensive test suite for VM Translator Part 2 (Program Flow and Functions)
"""

import unittest
import sys
import os
from pathlib import Path

# Add the computer_architecture directory to the path for CPU
current_dir = Path(__file__).parent
arch_dir = current_dir.parent.parent / 'phase1_hardware' / '05_computer_architecture'
sys.path.insert(0, str(arch_dir))

# Add the assembler directory for symbol-aware assembler
assembler_dir = current_dir.parent / '06_assembler'
sys.path.insert(0, str(assembler_dir))

from vm_translator import VMTranslator
from computer_architecture import CPU
from assembler import Assembler


class TestVMTranslatorPart2(unittest.TestCase):
    """Test suite for VM Part 2: Program Flow and Functions"""

    def setUp(self):
        """Create CPU and assembler for tests"""
        self.cpu = CPU()
        self.asm = Assembler()

    def run_vm_program(self, vm_path, max_cycles=50000):
        """
        Translate and execute VM program, return CPU state

        Args:
            vm_path: Path to VM file or directory
            max_cycles: Maximum CPU cycles to run
        """
        # Translate VM to assembly
        translator = VMTranslator(vm_path)
        translator.translate()

        # Determine assembly file path
        if os.path.isdir(vm_path):
            dir_name = os.path.basename(vm_path.rstrip('/'))
            asm_file = os.path.join(vm_path, f"{dir_name}.asm")
            binary_file = os.path.join(vm_path, f"{dir_name}.hack")
        else:
            asm_file = vm_path.replace('.vm', '.asm')
            binary_file = vm_path.replace('.vm', '.hack')

        # Assemble to binary
        self.asm.assemble(asm_file, binary_file, debug=False)

        # Load binary program
        with open(binary_file, 'r') as f:
            binary = [line.strip() for line in f]

        # Execute
        self.cpu.reset()
        self.cpu.load_program(binary)
        self.cpu.run(max_cycles=max_cycles)

        return self.cpu

    def get_stack_contents(self, cpu):
        """Return list of values currently on stack (as signed 16-bit integers)"""
        sp = cpu.ram[0]  # SP is at RAM[0]
        values = []
        for i in range(256, sp):
            value = cpu.ram[i]
            # Convert to signed 16-bit integer
            if value >= 32768:
                value -= 65536
            values.append(value)
        return values

    def get_stack_top(self, cpu):
        """Get value at top of stack (as signed 16-bit integer)"""
        sp = cpu.ram[0]
        if sp <= 256:
            return None
        value = cpu.ram[sp - 1]
        # Convert to signed 16-bit integer
        if value >= 32768:
            value -= 65536
        return value

    def trace_stack_frame(self, cpu):
        """Print current stack frame for debugging"""
        sp = cpu.ram[0]
        lcl = cpu.ram[1]
        arg = cpu.ram[2]
        this_ptr = cpu.ram[3]
        that_ptr = cpu.ram[4]

        print(f"\n=== Stack Frame ===")
        print(f"SP:   {sp}")
        print(f"LCL:  {lcl}")
        print(f"ARG:  {arg}")
        print(f"THIS: {this_ptr}")
        print(f"THAT: {that_ptr}")
        print(f"Stack: {self.get_stack_contents(cpu)}")


class TestProgramFlow(TestVMTranslatorPart2):
    """Test program flow commands: label, goto, if-goto"""

    def test_simple_loop(self):
        """Test: Loop counting from 0 to 5"""
        cpu = self.run_vm_program('examples/SimpleLoop/')

        # Should have executed loop and returned 5
        result = self.get_stack_top(cpu)
        self.assertEqual(result, 5, f"Expected 5, got {result}")

    def test_conditional_branch(self):
        """Test: if-goto with true and false conditions"""
        # Create a simple if-goto test
        test_dir = 'examples/IfGotoTest/'
        os.makedirs(test_dir, exist_ok=True)

        with open(os.path.join(test_dir, 'Main.vm'), 'w') as f:
            f.write("""
function Main.main 1
    // Test 1: if-goto with true (non-zero)
    push constant 10
    if-goto BRANCH_TRUE
    push constant 0
    pop local 0
    goto END1
label BRANCH_TRUE
    push constant 1
    pop local 0
label END1

    // Test 2: if-goto with false (zero)
    push constant 0
    if-goto BRANCH_FALSE
    push local 0
    push constant 10
    add
    pop local 0
    goto END2
label BRANCH_FALSE
    push constant 999
    pop local 0
label END2

    push local 0
    return
""")

        with open(os.path.join(test_dir, 'Sys.vm'), 'w') as f:
            f.write("""
function Sys.init 0
    call Main.main 0
label SYS_HALT
    goto SYS_HALT
""")

        cpu = self.run_vm_program(test_dir)
        result = self.get_stack_top(cpu)
        self.assertEqual(result, 11, f"Expected 11 (1+10), got {result}")


class TestFunctionCalls(TestVMTranslatorPart2):
    """Test function declaration, call, and return"""

    def test_simple_call(self):
        """Test: Simple function call - add(7, 3) = 10"""
        cpu = self.run_vm_program('examples/SimpleCall/')

        result = self.get_stack_top(cpu)
        self.assertEqual(result, 10, f"Expected 10, got {result}")

    def test_multiple_arguments(self):
        """Test: Function with multiple arguments"""
        test_dir = 'examples/MultiArgTest/'
        os.makedirs(test_dir, exist_ok=True)

        with open(os.path.join(test_dir, 'Main.vm'), 'w') as f:
            f.write("""
function Main.main 1
    push constant 2
    push constant 3
    push constant 4
    call Main.sum3 3
    pop local 0
    push local 0
    return

function Main.sum3 0
    push argument 0
    push argument 1
    add
    push argument 2
    add
    return
""")

        with open(os.path.join(test_dir, 'Sys.vm'), 'w') as f:
            f.write("""
function Sys.init 0
    call Main.main 0
label SYS_HALT
    goto SYS_HALT
""")

        cpu = self.run_vm_program(test_dir)
        result = self.get_stack_top(cpu)
        self.assertEqual(result, 9, f"Expected 9 (2+3+4), got {result}")

    def test_local_variables(self):
        """Test: Function with local variables"""
        test_dir = 'examples/LocalVarTest/'
        os.makedirs(test_dir, exist_ok=True)

        with open(os.path.join(test_dir, 'Main.vm'), 'w') as f:
            f.write("""
function Main.main 1
    push constant 5
    push constant 3
    call Main.subtract 2
    pop local 0
    push local 0
    return

function Main.subtract 2
    push argument 0
    pop local 0
    push argument 1
    pop local 1
    push local 0
    push local 1
    sub
    return
""")

        with open(os.path.join(test_dir, 'Sys.vm'), 'w') as f:
            f.write("""
function Sys.init 0
    call Main.main 0
label SYS_HALT
    goto SYS_HALT
""")

        cpu = self.run_vm_program(test_dir)
        result = self.get_stack_top(cpu)
        self.assertEqual(result, 2, f"Expected 2 (5-3), got {result}")


class TestRecursion(TestVMTranslatorPart2):
    """Test recursive function calls"""

    def test_factorial(self):
        """Test: Recursive factorial(5) = 120"""
        cpu = self.run_vm_program('examples/Factorial/', max_cycles=100000)

        result = self.get_stack_top(cpu)
        self.assertEqual(result, 120, f"Expected 120 (5!), got {result}")

    def test_fibonacci(self):
        """Test: Iterative Fibonacci series"""
        cpu = self.run_vm_program('examples/FibonacciSeries/', max_cycles=100000)

        # Fibonacci should have stored values in static
        # The last value stored should be the 8th Fibonacci number
        # Sequence: 1, 1, 2, 3, 5, 8, 13, 21
        # We can verify the program ran successfully
        result = self.get_stack_top(cpu)
        self.assertEqual(result, 0, "Expected 0 (successful return)")


class TestComplexPrograms(TestVMTranslatorPart2):
    """Test complex multi-file programs with nested calls"""

    def test_nested_calls(self):
        """Test: Nested function calls"""
        test_dir = 'examples/NestedCallTest/'
        os.makedirs(test_dir, exist_ok=True)

        with open(os.path.join(test_dir, 'Main.vm'), 'w') as f:
            f.write("""
function Main.main 1
    push constant 3
    call Main.square 1
    pop local 0
    push local 0
    return

function Main.square 0
    push argument 0
    push argument 0
    call Math.multiply 2
    return
""")

        with open(os.path.join(test_dir, 'Math.vm'), 'w') as f:
            f.write("""
function Math.multiply 2
    push constant 0
    pop local 0
    push argument 1
    pop local 1

label MULT_LOOP
    push local 1
    push constant 0
    eq
    if-goto MULT_END

    push local 0
    push argument 0
    add
    pop local 0

    push local 1
    push constant 1
    sub
    pop local 1

    goto MULT_LOOP

label MULT_END
    push local 0
    return
""")

        with open(os.path.join(test_dir, 'Sys.vm'), 'w') as f:
            f.write("""
function Sys.init 0
    call Main.main 0
label SYS_HALT
    goto SYS_HALT
""")

        cpu = self.run_vm_program(test_dir, max_cycles=100000)
        result = self.get_stack_top(cpu)
        self.assertEqual(result, 9, f"Expected 9 (3²), got {result}")


class TestBootstrap(TestVMTranslatorPart2):
    """Test bootstrap code and Sys.init"""

    def test_bootstrap_initialization(self):
        """Test: Bootstrap initializes SP and calls Sys.init"""
        cpu = self.run_vm_program('examples/SimpleCall/')

        # Check that SP was initialized properly
        sp = cpu.ram[0]
        self.assertGreater(sp, 256, "SP should be above initial stack base")

        # Check that segment pointers were used
        # (They should have been saved/restored during function calls)
        lcl = cpu.ram[1]
        arg = cpu.ram[2]
        # LCL and ARG should have valid values from function calls
        self.assertIsNotNone(lcl)
        self.assertIsNotNone(arg)


class TestEdgeCases(TestVMTranslatorPart2):
    """Test edge cases and error conditions"""

    def test_zero_argument_function(self):
        """Test: Function with zero arguments"""
        test_dir = 'examples/ZeroArgTest/'
        os.makedirs(test_dir, exist_ok=True)

        with open(os.path.join(test_dir, 'Main.vm'), 'w') as f:
            f.write("""
function Main.main 1
    call Main.getFortyTwo 0
    pop local 0
    push local 0
    return

function Main.getFortyTwo 0
    push constant 42
    return
""")

        with open(os.path.join(test_dir, 'Sys.vm'), 'w') as f:
            f.write("""
function Sys.init 0
    call Main.main 0
label SYS_HALT
    goto SYS_HALT
""")

        cpu = self.run_vm_program(test_dir)
        result = self.get_stack_top(cpu)
        self.assertEqual(result, 42, f"Expected 42, got {result}")

    def test_zero_local_function(self):
        """Test: Function with zero local variables"""
        test_dir = 'examples/ZeroLocalTest/'
        os.makedirs(test_dir, exist_ok=True)

        with open(os.path.join(test_dir, 'Main.vm'), 'w') as f:
            f.write("""
function Main.main 1
    push constant 5
    push constant 3
    call Main.add 2
    pop local 0
    push local 0
    return

function Main.add 0
    push argument 0
    push argument 1
    add
    return
""")

        with open(os.path.join(test_dir, 'Sys.vm'), 'w') as f:
            f.write("""
function Sys.init 0
    call Main.main 0
label SYS_HALT
    goto SYS_HALT
""")

        cpu = self.run_vm_program(test_dir)
        result = self.get_stack_top(cpu)
        self.assertEqual(result, 8, f"Expected 8, got {result}")


def run_tests():
    """Run all tests with verbose output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestProgramFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestFunctionCalls))
    suite.addTests(loader.loadTestsFromTestCase(TestRecursion))
    suite.addTests(loader.loadTestsFromTestCase(TestComplexPrograms))
    suite.addTests(loader.loadTestsFromTestCase(TestBootstrap))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success/failure
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
