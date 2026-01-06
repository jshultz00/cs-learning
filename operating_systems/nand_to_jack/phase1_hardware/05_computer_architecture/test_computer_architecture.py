"""
Unit tests for the Hack computer architecture components.

Tests individual components (ALU, RAM, ROM, Assembler) and integration (CPU).
"""

import unittest
from alu import ALU
from ram import RAM
from rom import ROM
from assembler import Assembler
from cpu import CPU


class TestALU(unittest.TestCase):
    """Test ALU operations"""

    def setUp(self):
        self.alu = ALU()

    def test_constants(self):
        """Test constant generation"""
        self.assertEqual(self.alu.compute(0b101010, 0, 0), 0)      # 0
        self.assertEqual(self.alu.compute(0b111111, 0, 0), 1)      # 1
        self.assertEqual(self.alu.compute(0b111010, 0, 0), 0xFFFF) # -1 (as unsigned)

    def test_pass_through(self):
        """Test pass-through operations"""
        self.assertEqual(self.alu.compute(0b001100, 42, 0), 42)    # D
        self.assertEqual(self.alu.compute(0b110000, 0, 100), 100)  # A/M

    def test_bitwise_not(self):
        """Test bitwise NOT operations"""
        self.assertEqual(self.alu.compute(0b001101, 0xFFFF, 0), 0)     # !D
        self.assertEqual(self.alu.compute(0b110001, 0, 0xFFFF), 0)     # !A/M

    def test_arithmetic_negate(self):
        """Test two's complement negation"""
        self.assertEqual(self.alu.compute(0b001111, 5, 0), 0xFFFB)     # -D (-5 as unsigned)
        self.assertEqual(self.alu.compute(0b110011, 0, 10), 0xFFF6)    # -A/M (-10 as unsigned)

    def test_increment(self):
        """Test increment operations"""
        self.assertEqual(self.alu.compute(0b011111, 5, 0), 6)      # D+1
        self.assertEqual(self.alu.compute(0b110111, 0, 10), 11)    # A+1/M+1

    def test_decrement(self):
        """Test decrement operations"""
        self.assertEqual(self.alu.compute(0b001110, 5, 0), 4)      # D-1
        self.assertEqual(self.alu.compute(0b110010, 0, 10), 9)     # A-1/M-1

    def test_addition(self):
        """Test addition"""
        self.assertEqual(self.alu.compute(0b000010, 5, 10), 15)    # D+A/M

    def test_subtraction(self):
        """Test subtraction"""
        self.assertEqual(self.alu.compute(0b010011, 10, 3), 7)     # D-A/M
        self.assertEqual(self.alu.compute(0b000111, 3, 10), 7)     # A-D/M-D

    def test_bitwise_and(self):
        """Test bitwise AND"""
        self.assertEqual(self.alu.compute(0b000000, 0xFF, 0x0F), 0x0F)  # D&A/M

    def test_bitwise_or(self):
        """Test bitwise OR"""
        self.assertEqual(self.alu.compute(0b010101, 0xFF, 0x0F), 0xFF)  # D|A/M


class TestRAM(unittest.TestCase):
    """Test RAM operations"""

    def setUp(self):
        self.ram = RAM(size=1024)

    def test_initial_state(self):
        """Test that RAM starts with all zeros"""
        for i in range(10):
            self.assertEqual(self.ram[i], 0)

    def test_write_read(self):
        """Test writing and reading values"""
        self.ram[0] = 42
        self.assertEqual(self.ram[0], 42)

        self.ram[100] = 0xFFFF
        self.assertEqual(self.ram[100], 0xFFFF)

    def test_array_style_access(self):
        """Test array-style indexing"""
        self.ram[5] = 123
        self.assertEqual(self.ram[5], 123)

    def test_bounds_checking(self):
        """Test that out-of-bounds access returns 0 or ignores write"""
        self.ram[2000] = 999  # Out of bounds for 1024-size RAM
        self.assertEqual(self.ram[2000], 0)

    def test_reset(self):
        """Test RAM reset functionality"""
        self.ram[0] = 100
        self.ram[10] = 200
        self.ram.reset()
        self.assertEqual(self.ram[0], 0)
        self.assertEqual(self.ram[10], 0)


class TestROM(unittest.TestCase):
    """Test ROM operations"""

    def setUp(self):
        self.rom = ROM(size=1024)

    def test_load_program_binary_strings(self):
        """Test loading program from binary strings"""
        program = ["0000000000000101", "1110110000010000"]
        self.rom.load_program(program)
        self.assertEqual(self.rom[0], 0b0000000000000101)
        self.assertEqual(self.rom[1], 0b1110110000010000)

    def test_load_program_integers(self):
        """Test loading program from integer values"""
        program = [5, 1000, 2000]
        self.rom.load_program_binary(program)
        self.assertEqual(self.rom[0], 5)
        self.assertEqual(self.rom[1], 1000)
        self.assertEqual(self.rom[2], 2000)

    def test_fetch(self):
        """Test fetching instructions"""
        self.rom.load_program_binary([42])
        self.assertEqual(self.rom.fetch(0), 42)

    def test_array_style_access(self):
        """Test array-style indexing"""
        self.rom.load_program_binary([100])
        self.assertEqual(self.rom[0], 100)

    def test_reset(self):
        """Test ROM reset functionality"""
        self.rom.load_program_binary([1, 2, 3])
        self.rom.reset()
        self.assertEqual(self.rom[0], 0)
        self.assertEqual(self.rom[1], 0)


class TestAssembler(unittest.TestCase):
    """Test assembler functionality"""

    def setUp(self):
        self.assembler = Assembler()

    def test_a_instruction(self):
        """Test A-instruction assembly"""
        self.assertEqual(self.assembler.assemble_a_instruction("5"), "0000000000000101")
        self.assertEqual(self.assembler.assemble_a_instruction("100"), "0000000001100100")

    def test_c_instruction_dest_only(self):
        """Test C-instruction with destination"""
        result = self.assembler.assemble_c_instruction("D", "A", "")
        self.assertEqual(result[:3], "111")  # C-instruction prefix
        self.assertEqual(result[10:13], "010")  # D destination

    def test_c_instruction_jump_only(self):
        """Test C-instruction with jump"""
        result = self.assembler.assemble_c_instruction("", "D", "JGT")
        self.assertEqual(result[:3], "111")  # C-instruction prefix
        self.assertEqual(result[13:16], "001")  # JGT jump code

    def test_parse_a_instruction(self):
        """Test parsing A-instructions"""
        parsed = self.assembler.parse_line("@5")
        self.assertEqual(parsed, ('A', '5'))

    def test_parse_c_instruction_full(self):
        """Test parsing full C-instructions"""
        parsed = self.assembler.parse_line("D=D+1;JGT")
        self.assertEqual(parsed, ('C', 'D', 'D+1', 'JGT'))

    def test_parse_c_instruction_dest_only(self):
        """Test parsing C-instruction with only destination"""
        parsed = self.assembler.parse_line("M=D")
        self.assertEqual(parsed, ('C', 'M', 'D', ''))

    def test_parse_c_instruction_jump_only(self):
        """Test parsing C-instruction with only jump"""
        parsed = self.assembler.parse_line("0;JMP")
        self.assertEqual(parsed, ('C', '', '0', 'JMP'))

    def test_parse_comments(self):
        """Test parsing lines with comments"""
        parsed = self.assembler.parse_line("@5 // Load 5")
        self.assertEqual(parsed, ('A', '5'))

    def test_parse_empty_line(self):
        """Test parsing empty lines"""
        self.assertIsNone(self.assembler.parse_line(""))
        self.assertIsNone(self.assembler.parse_line("   "))
        self.assertIsNone(self.assembler.parse_line("// Just a comment"))

    def test_assemble_program(self):
        """Test assembling a complete program"""
        program = [
            "@5",
            "D=A",
            "@10",
            "M=D"
        ]
        binary = self.assembler.assemble(program)
        self.assertEqual(len(binary), 4)
        self.assertEqual(binary[0], "0000000000000101")  # @5
        self.assertTrue(binary[1].startswith("111"))     # D=A (C-instruction)


class TestCPU(unittest.TestCase):
    """Test CPU execution"""

    def setUp(self):
        self.cpu = CPU()
        self.assembler = Assembler()

    def test_a_instruction_execution(self):
        """Test executing A-instructions"""
        program = ["@42"]
        binary = self.assembler.assemble(program)
        self.cpu.load_program(binary)

        self.cpu.step()
        self.assertEqual(self.cpu.A, 42)
        self.assertEqual(self.cpu.PC, 1)

    def test_simple_computation(self):
        """Test simple computation: @5, D=A"""
        program = [
            "@5",
            "D=A"
        ]
        binary = self.assembler.assemble(program)
        self.cpu.load_program(binary)

        self.cpu.step()  # @5
        self.assertEqual(self.cpu.A, 5)

        self.cpu.step()  # D=A
        self.assertEqual(self.cpu.D, 5)

    def test_memory_write(self):
        """Test writing to memory"""
        program = [
            "@10",   # Set address
            "M=1",   # Write 1 to RAM[10]
            "HALT"   # Stop execution
        ]
        binary = self.assembler.assemble(program)
        self.cpu.load_program(binary)

        halted, cycles = self.cpu.run()
        self.assertTrue(halted)
        self.assertEqual(self.cpu.ram[10], 1)

    def test_memory_read(self):
        """Test reading from memory"""
        # Manually set up RAM
        self.cpu.ram[15] = 42

        program = [
            "@15",   # Point to RAM[15]
            "D=M",   # Load RAM[15] into D
            "HALT"   # Stop execution
        ]
        binary = self.assembler.assemble(program)
        self.cpu.load_program(binary)

        halted, cycles = self.cpu.run()
        self.assertTrue(halted)
        self.assertEqual(self.cpu.D, 42)

    def test_unconditional_jump(self):
        """Test unconditional jump"""
        program = [
            "@10",
            "0;JMP"
        ]
        binary = self.assembler.assemble(program)
        self.cpu.load_program(binary)

        # Execute exactly 2 instructions before jump lands at address 10
        self.cpu.step()  # @10: A=10, PC=1
        self.cpu.step()  # 0;JMP: PC=10
        self.assertEqual(self.cpu.PC, 10)

    def test_conditional_jump_taken(self):
        """Test conditional jump that should be taken"""
        program = [
            "@1",
            "D=A",    # D=1 (positive)
            "@10",
            "D;JGT"   # Jump because D > 0
        ]
        binary = self.assembler.assemble(program)
        self.cpu.load_program(binary)

        # Run with limited cycles - just enough to execute the jump
        self.cpu.run(max_cycles=4)
        self.assertEqual(self.cpu.PC, 10)

    def test_conditional_jump_not_taken(self):
        """Test conditional jump that should not be taken"""
        program = [
            "@1",
            "D=A",    # D=1
            "D=D-A",  # D=1-1=0
            "@10",
            "D;JGT",  # Don't jump because D is 0 (not > 0)
            "@99",    # Continue to this instruction instead
            "D=A"     # Set D=99 to verify we got here
        ]
        binary = self.assembler.assemble(program)
        self.cpu.load_program(binary)

        # Run with limited cycles - just enough to execute all instructions
        self.cpu.run(max_cycles=7)
        self.assertEqual(self.cpu.D, 99)  # Should have executed the instructions after the non-jump
        self.assertEqual(self.cpu.A, 99)

    def test_arithmetic_computation(self):
        """Test arithmetic: add two numbers"""
        program = [
            "@5",
            "D=A",    # D = 5
            "@3",
            "D=D+A",  # D = 5 + 3 = 8
            "HALT"    # Stop execution
        ]
        binary = self.assembler.assemble(program)
        self.cpu.load_program(binary)

        halted, cycles = self.cpu.run()
        self.assertTrue(halted)
        self.assertEqual(self.cpu.D, 8)

    def test_cpu_reset(self):
        """Test CPU reset functionality"""
        program = ["@42", "D=A"]
        binary = self.assembler.assemble(program)
        self.cpu.load_program(binary)
        self.cpu.run()

        self.cpu.reset()
        self.assertEqual(self.cpu.A, 0)
        self.assertEqual(self.cpu.D, 0)
        self.assertEqual(self.cpu.PC, 0)

    def test_at_zero_instruction(self):
        """Test that @0 is a valid instruction, not a halt"""
        program = [
            "@0",      # Should set A=0, not halt
            "D=A",     # D=0
            "@100",    # A=100
            "M=D",     # RAM[100]=0
            "HALT"     # Stop execution
        ]
        binary = self.assembler.assemble(program)
        self.cpu.load_program(binary)

        halted, cycles = self.cpu.run()
        self.assertTrue(halted)
        self.assertEqual(self.cpu.D, 0)
        self.assertEqual(self.cpu.ram[100], 0)
        self.assertEqual(self.cpu.PC, 4)  # Should have executed all 4 instructions before HALT

    def test_halt_instruction(self):
        """Test HALT instruction stops execution"""
        program = [
            "@42",
            "D=A",     # D = 42
            "HALT",    # Should stop here
            "@99",     # Should NOT execute
            "D=A"      # Should NOT execute
        ]
        binary = self.assembler.assemble(program)
        self.cpu.load_program(binary)

        halted, cycles = self.cpu.run()
        self.assertTrue(halted, "HALT instruction should stop execution")
        self.assertEqual(cycles, 3, "Should execute 2 instructions + HALT")
        self.assertEqual(self.cpu.D, 42, "D should be 42, not 99")
        self.assertEqual(self.cpu.A, 42, "A should be 42, not 99")
        self.assertEqual(self.cpu.PC, 2, "PC should be at HALT instruction")

    def test_cpu_reset_before_run(self):
        """Test that CPU should be reset between program runs"""
        # First program
        program1 = ["@10", "D=A", "HALT"]
        binary1 = self.assembler.assemble(program1)
        self.cpu.load_program(binary1)
        self.cpu.run()
        self.assertEqual(self.cpu.D, 10)

        # Reset CPU before next program
        self.cpu.reset()

        # Second program - verify state is clean
        program2 = ["@20", "HALT"]
        binary2 = self.assembler.assemble(program2)
        self.cpu.load_program(binary2)
        halted, cycles = self.cpu.run()
        self.assertTrue(halted)
        self.assertEqual(self.cpu.A, 20)
        self.assertEqual(self.cpu.D, 0, "D should be reset to 0")
        self.assertEqual(self.cpu.PC, 1)


if __name__ == '__main__':
    unittest.main()
