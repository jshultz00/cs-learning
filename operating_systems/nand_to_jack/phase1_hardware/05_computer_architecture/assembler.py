"""
Assembler - Converts assembly language to machine code
"""

class Assembler:
    """
    Assembler for the Hack assembly language.

    Converts human-readable assembly instructions into 16-bit binary machine code.

    Instruction types:
    - A-instruction: @value → 0vvvvvvvvvvvvvvv
    - C-instruction: dest=comp;jump → 111accccccdddjjj
    """

    def __init__(self):
        '''
        Computation codes (comp field):

        comp   | a=0    | a=1    | Binary  | Notes
        -------|--------|--------|---------|----------------------------------
        0      | 0      | -      | 101010  | Constant zero (useful for initialization)
        1      | 1      | -      | 111111  | Constant one (increment operations)
        -1     | -1     | -      | 111010  | Constant negative one (decrement)
        D      | D      | -      | 001100  | Pass through D register
        A      | A      | M      | 110000  | Pass through A or memory
        !D     | !D     | -      | 001101  | Bitwise NOT D
        !A     | !A     | !M     | 110001  | Bitwise NOT A/M
        -D     | -D     | -      | 001111  | Arithmetic negate D (two's complement)
        -A     | -A     | -M     | 110011  | Arithmetic negate A/M
        D+1    | D+1    | -      | 011111  | Increment D
        A+1    | A+1    | M+1    | 110111  | Increment A/M
        D-1    | D-1    | -      | 001110  | Decrement D
        A-1    | A-1    | M-1    | 110010  | Decrement A/M
        D+A    | D+A    | D+M    | 000010  | Addition
        D-A    | D-A    | D-M    | 010011  | Subtract A/M from D
        A-D    | A-D    | M-D    | 000111  | Subtract D from A/M
        D&A    | D&A    | D&M    | 000000  | Bitwise AND
        D|A    | D|A    | D|M    | 010101  | Bitwise OR
        '''
        self.comp_table = {
            "0": "0101010", "1": "0111111", "-1": "0111010", "D": "0001100", "A": "0110000", "M": "1110000",
            "!D": "0001101", "!A": "0110001", "!M": "1110001", "-D": "0001111", "-A": "0110011", "-M": "1110011",
            "D+1": "0011111", "A+1": "0110111", "M+1": "1110111", "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
            "D+A": "0000010", "D+M": "1000010", "D-A": "0010011", "D-M": "1010011", "A-D": "0000111", "M-D": "1000111",
            "D&A": "0000000", "D&M": "1000000", "D|A": "0010101", "D|M": "1010101"
        }
        self.dest_table = {
            "": "000", "M": "001", "D": "010", "MD": "011", "A": "100", "AM": "101", "AD": "110", "AMD": "111"
        }
        self.jump_table = {
            "": "000", "JGT": "001", "JEQ": "010", "JGE": "011", "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"
        }

    def assemble_a_instruction(self, value):
        """
        Assemble A-instruction: @value → 0vvvvvvvvvvvvvvv

        Args:
            value: Integer value or address (0-32767)

        Returns:
            16-bit binary string
        """
        binary = format(int(value), '015b')
        return '0' + binary

    def assemble_c_instruction(self, dest, comp, jump):
        """
        Assemble C-instruction: dest=comp;jump → 111accccccdddjjj

        Args:
            dest: Destination register(s) ("", "M", "D", "MD", "A", "AM", "AD", "AMD")
            comp: Computation ("D+1", "D-A", "D&M", etc.)
            jump: Jump condition ("", "JGT", "JEQ", "JGE", "JLT", "JNE", "JLE", "JMP")

        Returns:
            16-bit binary string
        """
        comp_bits = self.comp_table[comp]
        dest_bits = self.dest_table[dest]
        jump_bits = self.jump_table[jump]
        return '111' + comp_bits + dest_bits + jump_bits

    def assemble_halt_instruction(self):
        """
        Assemble HALT instruction → 1111111111111111 (all 1s)

        The HALT instruction is a special C-instruction that signals
        the CPU to stop execution. It uses an encoding that is not
        used by any valid C-instruction in the Hack ISA.

        Returns:
            16-bit binary string (all 1s)
        """
        return '1111111111111111'

    def parse_line(self, line):
        """
        Parse assembly line into components.

        Args:
            line: Assembly language instruction (may include comments)

        Returns:
            Tuple describing instruction:
            - ('A', value) for A-instructions
            - ('C', dest, comp, jump) for C-instructions
            - ('HALT',) for HALT instruction
            - None for empty lines or comment-only lines
        """
        line = line.split('//')[0].strip()  # Remove comments
        if not line:
            return None

        # Check for HALT instruction
        if line.upper() == 'HALT':
            return ('HALT',)

        if line.startswith('@'):  # A-instruction
            value = line[1:]
            return ('A', value)

        # C-instruction: parse dest=comp;jump
        dest = ""
        comp = ""
        jump = ""

        if '=' in line:
            dest, line = line.split('=')
        if ';' in line:
            comp, jump = line.split(';')
        else:
            comp = line

        return ('C', dest.strip(), comp.strip(), jump.strip())

    def assemble(self, assembly_code):
        """
        Assemble complete program from assembly code.

        Args:
            assembly_code: List of assembly language instructions

        Returns:
            List of 16-bit binary instruction strings
        """
        binary_instructions = []
        for line in assembly_code:
            parsed = self.parse_line(line)
            if parsed is None:
                continue

            if parsed[0] == 'A':
                binary_instructions.append(self.assemble_a_instruction(parsed[1]))
            elif parsed[0] == 'C':
                _, dest, comp, jump = parsed
                binary_instructions.append(self.assemble_c_instruction(dest, comp, jump))
            elif parsed[0] == 'HALT':
                binary_instructions.append(self.assemble_halt_instruction())

        return binary_instructions
