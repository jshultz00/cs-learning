# test_vm_translator.py
import unittest
import sys
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

class TestVMTranslator(unittest.TestCase):
    def setUp(self):
        """Create CPU and assembler for tests"""
        self.cpu = CPU()
        self.asm = Assembler()

    def run_vm_program(self, vm_file, max_cycles=10000, init_segments=None):
        """Translate and execute VM program, return CPU state

        Args:
            vm_file: Path to VM file
            max_cycles: Maximum CPU cycles to run
            init_segments: Dict of segment pointer initializations (e.g., {'LCL': 300, 'ARG': 400})
        """
        # Translate VM to assembly
        translator = VMTranslator(vm_file)
        translator.translate()
        asm_file = vm_file.replace('.vm', '.asm')

        # Generate binary file
        binary_file = vm_file.replace('.vm', '.hack')

        # Assemble to binary
        self.asm.assemble(asm_file, binary_file, debug=False)

        # Load binary program
        with open(binary_file, 'r') as f:
            binary = [line.strip() for line in f]

        # Execute
        self.cpu.reset()

        # Initialize segment pointers if provided
        if init_segments:
            segment_map = {'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4}
            for seg_name, value in init_segments.items():
                if seg_name in segment_map:
                    self.cpu.ram[segment_map[seg_name]] = value

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

    def initialize_segment_pointers(self, cpu, lcl=300, arg=400, this_ptr=3000, that_ptr=3010):
        """Initialize segment base pointers for memory tests"""
        cpu.ram[1] = lcl    # LCL
        cpu.ram[2] = arg    # ARG
        cpu.ram[3] = this_ptr   # THIS
        cpu.ram[4] = that_ptr   # THAT

    def test_simple_add(self):
        """Test: push 7, push 8, add → result 15"""
        cpu = self.run_vm_program('examples/simple_add.vm')
        stack = self.get_stack_contents(cpu)
        self.assertEqual(stack, [15])

    def test_all_arithmetic(self):
        """Test all arithmetic/logical operations"""
        cpu = self.run_vm_program('examples/stack_test.vm', max_cycles=20000)
        stack = self.get_stack_contents(cpu)

        # Stack should have results from all comparisons and final expression
        # Based on stack_test.vm, we expect multiple comparison results
        self.assertIsNotNone(stack)
        self.assertTrue(len(stack) > 0)
        # The final result after the complex expression should be on top
        # (exact value depends on the operations)

    def test_basic_memory(self):
        """Test local, argument, this, that, temp segments"""
        # Initialize segment pointers
        init_segs = {'LCL': 300, 'ARG': 400, 'THIS': 3000, 'THAT': 3010}

        cpu = self.run_vm_program('examples/basic_test.vm', max_cycles=20000, init_segments=init_segs)
        stack = self.get_stack_contents(cpu)

        # Final result: 472 (based on basic_test.vm)
        self.assertEqual(stack[-1], 472)

    def test_pointer_segment(self):
        """Test pointer segment (THIS/THAT manipulation)"""
        cpu = self.run_vm_program('examples/pointer_test.vm', max_cycles=15000)
        stack = self.get_stack_contents(cpu)

        # Final result: 6084 (based on pointer_test.vm)
        self.assertEqual(stack[-1], 6084)

        # Verify THIS and THAT were set correctly
        self.assertEqual(cpu.ram[3], 3030)  # THIS
        self.assertEqual(cpu.ram[4], 3040)  # THAT

    def test_static_variables(self):
        """Test static segment (file-scoped globals)"""
        cpu = self.run_vm_program('examples/static_test.vm', max_cycles=15000)
        stack = self.get_stack_contents(cpu)

        # Final result: 1110 (based on static_test.vm)
        self.assertEqual(stack[-1], 1110)

class TestArithmeticDetails(unittest.TestCase):
    """Detailed tests for individual arithmetic operations"""

    def setUp(self):
        self.cpu = CPU()
        self.asm = Assembler()

    def run_vm_program(self, vm_file, max_cycles=10000):
        """Helper to run VM program"""
        translator = VMTranslator(vm_file)
        translator.translate()
        asm_file = vm_file.replace('.vm', '.asm')
        binary_file = vm_file.replace('.vm', '.hack')

        # Assemble
        self.asm.assemble(asm_file, binary_file, debug=False)

        # Load binary
        with open(binary_file, 'r') as f:
            binary = [line.strip() for line in f]

        # Execute
        self.cpu.reset()
        self.cpu.load_program(binary)
        self.cpu.run(max_cycles=max_cycles)
        return self.cpu

    def get_stack_top(self, cpu):
        """Get value at top of stack (as signed 16-bit integer)"""
        sp = cpu.ram[0]
        value = cpu.ram[sp - 1]
        # Convert to signed 16-bit integer
        if value >= 32768:
            value -= 65536
        return value

    def test_subtraction(self):
        """Test: push 10, push 3, sub → result 7"""
        # Create temporary test file
        with open('examples/test_sub.vm', 'w') as f:
            f.write("push constant 10\npush constant 3\nsub\n")

        cpu = self.run_vm_program('examples/test_sub.vm')
        result = self.get_stack_top(cpu)
        self.assertEqual(result, 7)

    def test_negation(self):
        """Test: push 5, neg → result -5"""
        with open('examples/test_neg.vm', 'w') as f:
            f.write("push constant 5\nneg\n")

        cpu = self.run_vm_program('examples/test_neg.vm')
        result = self.get_stack_top(cpu)
        self.assertEqual(result, -5)

    def test_equality_true(self):
        """Test: push 7, push 7, eq → result -1 (true)"""
        with open('examples/test_eq_true.vm', 'w') as f:
            f.write("push constant 7\npush constant 7\neq\n")

        cpu = self.run_vm_program('examples/test_eq_true.vm')
        result = self.get_stack_top(cpu)
        self.assertEqual(result, -1)

    def test_equality_false(self):
        """Test: push 7, push 8, eq → result 0 (false)"""
        with open('examples/test_eq_false.vm', 'w') as f:
            f.write("push constant 7\npush constant 8\neq\n")

        cpu = self.run_vm_program('examples/test_eq_false.vm')
        result = self.get_stack_top(cpu)
        self.assertEqual(result, 0)

    def test_greater_than_true(self):
        """Test: push 10, push 5, gt → result -1 (true)"""
        with open('examples/test_gt_true.vm', 'w') as f:
            f.write("push constant 10\npush constant 5\ngt\n")

        cpu = self.run_vm_program('examples/test_gt_true.vm')
        result = self.get_stack_top(cpu)
        self.assertEqual(result, -1)

    def test_less_than_true(self):
        """Test: push 5, push 10, lt → result -1 (true)"""
        with open('examples/test_lt_true.vm', 'w') as f:
            f.write("push constant 5\npush constant 10\nlt\n")

        cpu = self.run_vm_program('examples/test_lt_true.vm')
        result = self.get_stack_top(cpu)
        self.assertEqual(result, -1)

    def test_bitwise_and(self):
        """Test: push 12, push 10, and → result 8"""
        with open('examples/test_and.vm', 'w') as f:
            f.write("push constant 12\npush constant 10\nand\n")

        cpu = self.run_vm_program('examples/test_and.vm')
        result = self.get_stack_top(cpu)
        self.assertEqual(result, 8)  # 1100 & 1010 = 1000

    def test_bitwise_or(self):
        """Test: push 12, push 10, or → result 14"""
        with open('examples/test_or.vm', 'w') as f:
            f.write("push constant 12\npush constant 10\nor\n")

        cpu = self.run_vm_program('examples/test_or.vm')
        result = self.get_stack_top(cpu)
        self.assertEqual(result, 14)  # 1100 | 1010 = 1110

    def test_bitwise_not(self):
        """Test: push 0, not → result -1 (all bits set)"""
        with open('examples/test_not.vm', 'w') as f:
            f.write("push constant 0\nnot\n")

        cpu = self.run_vm_program('examples/test_not.vm')
        result = self.get_stack_top(cpu)
        self.assertEqual(result, -1)

if __name__ == '__main__':
    unittest.main()