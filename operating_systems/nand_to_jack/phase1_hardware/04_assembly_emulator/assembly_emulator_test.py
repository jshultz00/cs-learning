import unittest
from assembly_emulator import Assembler, CPU


class TestAssembler(unittest.TestCase):
    """Test the assembler component"""

    def setUp(self):
        self.assembler = Assembler()

    def test_a_instruction(self):
        """Test A-instruction assembly: @value -> 0vvvvvvvvvvvvvvv"""
        # @5 should become 0000000000000101
        result = self.assembler.assemble_a_instruction("5")
        self.assertEqual(result, "0000000000000101")

        # @100 should become 0000000001100100
        result = self.assembler.assemble_a_instruction("100")
        self.assertEqual(result, "0000000001100100")

    def test_c_instruction_simple(self):
        """Test simple C-instruction: D=A"""
        comp_bits = self.assembler.comp_table["A"]
        dest_bits = self.assembler.dest_table["D"]
        jump_bits = self.assembler.jump_table[""]
        result = self.assembler.assemble_c_instruction("D", "A", "")
        expected = "111" + comp_bits + dest_bits + jump_bits
        self.assertEqual(result, expected)

    def test_c_instruction_with_jump(self):
        """Test C-instruction with jump: D;JGT"""
        comp_bits = self.assembler.comp_table["D"]
        dest_bits = self.assembler.dest_table[""]
        jump_bits = self.assembler.jump_table["JGT"]
        result = self.assembler.assemble_c_instruction("", "D", "JGT")
        expected = "111" + comp_bits + dest_bits + jump_bits
        self.assertEqual(result, expected)

    def test_parse_a_instruction(self):
        """Test parsing A-instruction"""
        result = self.assembler.parse_line("@42")
        self.assertEqual(result, ('A', '42'))

    def test_parse_c_instruction(self):
        """Test parsing C-instruction with dest=comp;jump"""
        result = self.assembler.parse_line("D=D+1;JGT")
        self.assertEqual(result, ('C', 'D', 'D+1', 'JGT'))

        # Test with only dest=comp
        result = self.assembler.parse_line("M=D")
        self.assertEqual(result, ('C', 'M', 'D', ''))

        # Test with only comp;jump
        result = self.assembler.parse_line("D;JEQ")
        self.assertEqual(result, ('C', '', 'D', 'JEQ'))

    def test_parse_with_comments(self):
        """Test parsing lines with comments"""
        result = self.assembler.parse_line("@10  // Load 10 into A")
        self.assertEqual(result, ('A', '10'))

        # Comment-only line should return None
        result = self.assembler.parse_line("// This is a comment")
        self.assertIsNone(result)


class TestCPU(unittest.TestCase):
    """Test the CPU component"""

    def setUp(self):
        self.cpu = CPU()

    def test_a_instruction_execution(self):
        """Test A-instruction loads value into A register"""
        # @5: Load 5 into A
        program = ["0000000000000101"]  # @5
        self.cpu.load_program(program)

        self.cpu.step()
        self.assertEqual(self.cpu.A, 5)
        self.assertEqual(self.cpu.PC, 1)

    def test_simple_arithmetic(self):
        """Test simple program: @5, D=A, @3, D=D+A, M=D"""
        assembler = Assembler()

        # Assemble the program
        instructions = [
            "@5",      # A = 5
            "D=A",     # D = 5
            "@3",      # A = 3
            "D=D+A",   # D = 8
            "@100",    # A = 100 (memory location)
            "M=D"      # RAM[100] = 8
        ]

        binary_program = []
        for instr in instructions:
            parsed = assembler.parse_line(instr)
            if parsed[0] == 'A':
                binary_program.append(assembler.assemble_a_instruction(parsed[1]))
            else:
                binary_program.append(assembler.assemble_c_instruction(parsed[1], parsed[2], parsed[3]))

        self.cpu.load_program(binary_program)
        self.cpu.run(max_cycles=10)

        # Check final state
        self.assertEqual(self.cpu.D, 8, "D register should contain 8")
        self.assertEqual(self.cpu.RAM[100], 8, "RAM[100] should contain 8")

    def test_conditional_jump(self):
        """Test conditional jump: if D > 0, jump to skip some instructions"""
        assembler = Assembler()

        # Program that tests jumping when D > 0
        instructions = [
            "@10",     # PC=0: A = 10
            "D=A",     # PC=1: D = 10
            "@6",      # PC=2: A = 6 (jump target address)
            "D;JGT",   # PC=3: Jump to address 6 if D > 0 (should jump)
            "@50",     # PC=4: This gets skipped
            "M=A",     # PC=5: RAM[50] = 50 (skipped, so RAM[50] stays 0)
            "@100",    # PC=6: Jump lands here, A = 100
            "M=D",     # PC=7: RAM[100] = 10
        ]

        binary_program = []
        for instr in instructions:
            parsed = assembler.parse_line(instr)
            if parsed[0] == 'A':
                binary_program.append(assembler.assemble_a_instruction(parsed[1]))
            else:
                binary_program.append(assembler.assemble_c_instruction(parsed[1], parsed[2], parsed[3]))

        self.cpu.load_program(binary_program)
        self.cpu.run(max_cycles=10)

        # D should still be 10
        self.assertEqual(self.cpu.D, 10, "D should be 10")
        # RAM[50] should be 0 (instruction was skipped due to jump)
        self.assertEqual(self.cpu.RAM[50], 0, "RAM[50] should be 0 (instruction skipped)")
        # RAM[100] should be 10 (jump landed here and stored D)
        self.assertEqual(self.cpu.RAM[100], 10, "RAM[100] should be 10 (jump executed correctly)")


class TestALUOperations(unittest.TestCase):
    """Test ALU computation accuracy"""

    def setUp(self):
        self.cpu = CPU()
        self.assembler = Assembler()

    def test_alu_zero(self):
        """Test ALU can compute 0"""
        comp_bits = 0b101010  # 0
        result = self.cpu.alu_compute(comp_bits, 5, 10)
        self.assertEqual(result, 0)

    def test_alu_addition(self):
        """Test ALU D+A operation"""
        comp_bits = 0b000010  # D+A
        result = self.cpu.alu_compute(comp_bits, 5, 3)
        self.assertEqual(result, 8)

    def test_alu_subtraction(self):
        """Test ALU D-A operation"""
        comp_bits = 0b010011  # D-A
        result = self.cpu.alu_compute(comp_bits, 10, 3)
        self.assertEqual(result, 7)

    def test_alu_bitwise_and(self):
        """Test ALU D&A operation"""
        comp_bits = 0b000000  # D&A
        result = self.cpu.alu_compute(comp_bits, 0b1100, 0b1010)
        self.assertEqual(result, 0b1000)

    def test_alu_bitwise_or(self):
        """Test ALU D|A operation"""
        comp_bits = 0b010101  # D|A
        result = self.cpu.alu_compute(comp_bits, 0b1100, 0b1010)
        self.assertEqual(result, 0b1110)


if __name__ == '__main__':
    unittest.main()
