import unittest
import os
from assembler import SymbolTable, Parser, CodeGenerator, Assembler


class TestSymbolTable(unittest.TestCase):
    def setUp(self):
        self.st = SymbolTable()

    def test_predefined_and_operations(self):
        """Test predefined symbols and add operations"""
        # Predefined
        assert self.st.get_address('R5') == 5
        assert self.st.get_address('SP') == 0
        assert self.st.get_address('SCREEN') == 16384

        # Labels
        self.st.add_label('LOOP', 10)
        assert self.st.get_address('LOOP') == 10
        with self.assertRaises(ValueError):
            self.st.add_label('LOOP', 20)

        # Variables
        assert self.st.add_variable('sum', 16) == 16
        assert self.st.add_variable('sum', 99) == 16  # Idempotent
        assert self.st.contains('sum')


class TestParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.test_file = os.path.join(test_dir, 'test_program.asm')

    def setUp(self):
        self.parser = Parser(self.test_file)

    def test_navigation_and_types(self):
        """Test line navigation and instruction type detection"""
        assert self.parser.has_more_lines()

        # Find each type
        types_found = {'A': False, 'C': False, 'L': False}
        while self.parser.has_more_lines():
            itype = self.parser.instruction_type()
            if itype in types_found:
                types_found[itype] = True
            self.parser.advance()

        assert all(types_found.values())
        assert not self.parser.has_more_lines()

        # Reset works
        self.parser.reset()
        assert self.parser.current_line == 0

    def test_field_extraction(self):
        """Test dest, comp, jump extraction"""
        # Find D=A
        while self.parser.has_more_lines():
            if self.parser.current_instruction() == 'D=A':
                break
            self.parser.advance()
        assert self.parser.dest() == 'D'
        assert self.parser.comp() == 'A'
        assert self.parser.jump() == ''

        # Find D;JGT
        self.parser.reset()
        while self.parser.has_more_lines():
            if 'D;JGT' in self.parser.current_instruction():
                break
            self.parser.advance()
        assert self.parser.comp() == 'D'
        assert self.parser.jump() == 'JGT'


class TestCodeGenerator(unittest.TestCase):
    def setUp(self):
        self.cg = CodeGenerator()

    def test_instructions(self):
        """Test A and C instruction generation"""
        # A-instructions
        assert self.cg.generate_a_instruction(0) == '0000000000000000'
        assert self.cg.generate_a_instruction(16384) == '0100000000000000'

        # C-instructions
        assert self.cg.generate_c_instruction('D', 'A', '') == '1110110000010000'
        assert self.cg.generate_c_instruction('', '0', 'JMP') == '1110101010000111'
        assert self.cg.generate_c_instruction('M', 'M+1', '') == '1111110111001000'
        assert self.cg.generate_c_instruction('AMD', 'A', '') == '1110110000111000'

        # Error handling
        with self.assertRaises(ValueError):
            self.cg.generate_c_instruction('D', 'INVALID', '')


class TestAssembler(unittest.TestCase):
    def setUp(self):
        self.assembler = Assembler()
        self.test_dir = os.path.dirname(os.path.abspath(__file__))

    def _test_file(self, name, content, checks):
        """Helper to test assembly with cleanup"""
        asm = os.path.join(self.test_dir, f'{name}.asm')
        hack = os.path.join(self.test_dir, f'{name}.hack')
        try:
            with open(asm, 'w') as f:
                f.write(content)
            binary = self.assembler.assemble(asm, hack)
            for check in checks:
                check(binary)
            assert os.path.exists(hack)
        finally:
            for f in [asm, hack]:
                if os.path.exists(f):
                    os.remove(f)

    def test_a_instructions(self):
        """Test A-instructions and symbols"""
        self._test_file('test1', '@2\n@R5\n@SCREEN\n', [
            lambda b: self.assertEqual(len(b), 3),
            lambda b: self.assertEqual(b[0], '0000000000000010'),
            lambda b: self.assertEqual(b[1], '0000000000000101'),
            lambda b: self.assertEqual(b[2], '0100000000000000')
        ])

    def test_labels_and_variables(self):
        """Test label resolution and variable allocation"""
        self._test_file('test2', '@2\nD=A\n(LOOP)\n@LOOP\n@sum\n@sum\n', [
            lambda b: self.assertEqual(len(b), 5),
            lambda b: self.assertEqual(b[2], '0000000000000010'),  # @LOOP=2
            lambda b: self.assertEqual(b[3], '0000000000010000'),  # @sum=16
            lambda b: self.assertEqual(b[4], '0000000000010000')   # @sum reused
        ])

    def test_c_instructions(self):
        """Test C-instruction assembly"""
        self._test_file('test3', 'D=A\nM=D+1\nD;JGT\n', [
            lambda b: self.assertEqual(b[0], '1110110000010000'),
            lambda b: self.assertEqual(b[1], '1110011111001000'),
            lambda b: self.assertEqual(b[2], '1110001100000001')
        ])

    def test_complete_program(self):
        """Test complete program with all features"""
        program = '// Calculate 5+3\n@5\nD=A\n@3\nD=D+A\n@sum\nM=D\n(END)\n@END\n0;JMP\n'
        self._test_file('test4', program, [
            lambda b: self.assertEqual(len(b), 8),
            lambda b: self.assertEqual(b[0], '0000000000000101'),  # @5
            lambda b: self.assertEqual(b[4], '0000000000010000'),  # @sum=16
            lambda b: self.assertEqual(b[6], '0000000000000110')   # @END=6
        ])


if __name__ == '__main__':
    unittest.main()
