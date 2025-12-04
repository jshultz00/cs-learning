class Assembler:
    def __init__(self):
        '''
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
        """@value -> 0vvvvvvvvvvvvvvv"""
        binary = format(int(value), '015b')
        return '0' + binary

    def assemble_c_instruction(self, dest, comp, jump):
        """dest=comp;jump -> 111accccccdddjjj"""
        comp_bits = self.comp_table[comp]
        dest_bits = self.dest_table[dest]
        jump_bits = self.jump_table[jump]
        return '111' + comp_bits + dest_bits + jump_bits

    def parse_line(self, line):
        """Parse assembly line into components"""
        line = line.split('//')[0].strip()  # Remove comments
        if not line:
            return None

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


class CPU:
    """Simulates the CPU executing instructions"""
    def __init__(self, rom_size=32768, ram_size=32768):
        self.A = 0          # Address register
        self.D = 0          # Data register
        self.PC = 0         # Program counter
        self.RAM = [0] * ram_size
        self.ROM = [0] * rom_size  # Instruction memory

    def load_program(self, binary_instructions):
        """Load program into ROM"""
        for i, instruction in enumerate(binary_instructions):
            self.ROM[i] = int(instruction, 2)

    def fetch(self):
        """Fetch instruction from ROM[PC]"""
        return self.ROM[self.PC]

    def execute_a_instruction(self, instruction):
        """Execute A-instruction: @value"""
        value = instruction & 0x7FFF  # Bottom 15 bits
        self.A = value
        self.PC += 1

    def execute_c_instruction(self, instruction):
        """Execute C-instruction: dest=comp;jump"""
        # Decode instruction bits
        a_bit = (instruction >> 12) & 1
        comp_bits = (instruction >> 6) & 0x3F
        dest_bits = (instruction >> 3) & 0x7
        jump_bits = instruction & 0x7

        # Compute using ALU
        y = self.RAM[self.A] if a_bit else self.A
        result = self.alu_compute(comp_bits, self.D, y)

        # Store result in destinations
        if dest_bits & 0x4:  # A
            self.A = result
        if dest_bits & 0x2:  # D
            self.D = result
        if dest_bits & 0x1:  # M
            self.RAM[self.A] = result

        # Handle jump
        if self.should_jump(jump_bits, result):
            self.PC = self.A
        else:
            self.PC += 1

    def alu_compute(self, comp_bits, d_val, ay_val):
        """Perform ALU operation based on comp bits (6-bit comp field, no a-bit)"""
        # Helper to convert to signed 16-bit
        def to_signed(val):
            val = val & 0xFFFF
            return val if val < 0x8000 else val - 0x10000

        # Helper to convert back to unsigned 16-bit
        def to_unsigned(val):
            return val & 0xFFFF

        operations = {
            # Constants
            0b101010: lambda d, a: 0,                           # 0
            0b111111: lambda d, a: 1,                           # 1
            0b111010: lambda d, a: -1,                          # -1

            # Pass-through
            0b001100: lambda d, a: d,                           # D
            0b110000: lambda d, a: a,                           # A or M

            # Bitwise NOT
            0b001101: lambda d, a: ~d,                          # !D
            0b110001: lambda d, a: ~a,                          # !A or !M

            # Arithmetic negate (two's complement)
            0b001111: lambda d, a: -to_signed(d),               # -D
            0b110011: lambda d, a: -to_signed(a),               # -A or -M

            # Increment
            0b011111: lambda d, a: to_signed(d) + 1,            # D+1
            0b110111: lambda d, a: to_signed(a) + 1,            # A+1 or M+1

            # Decrement
            0b001110: lambda d, a: to_signed(d) - 1,            # D-1
            0b110010: lambda d, a: to_signed(a) - 1,            # A-1 or M-1

            # Addition
            0b000010: lambda d, a: to_signed(d) + to_signed(a), # D+A or D+M

            # Subtraction
            0b010011: lambda d, a: to_signed(d) - to_signed(a), # D-A or D-M
            0b000111: lambda d, a: to_signed(a) - to_signed(d), # A-D or M-D

            # Bitwise operations
            0b000000: lambda d, a: d & a,                       # D&A or D&M
            0b010101: lambda d, a: d | a,                       # D|A or D|M
        }

        result = operations[comp_bits](d_val, ay_val)
        return to_unsigned(result)

    def should_jump(self, jump_bits, value):
        """Determine if jump condition is met"""
        if jump_bits == 0:  # No jump
            return False
        if jump_bits == 0b111:  # Unconditional
            return True

        # Check conditions
        is_negative = (value & 0x8000) != 0
        is_zero = value == 0
        is_positive = not is_negative and not is_zero

        conditions = {
            0b001: is_positive,  # JGT
            0b010: is_zero,      # JEQ
            0b011: not is_negative,  # JGE
            0b100: is_negative,  # JLT
            0b101: not is_zero,  # JNE
            0b110: is_negative or is_zero,  # JLE
        }
        return conditions.get(jump_bits, False)

    def step(self):
        """Execute one instruction"""
        instruction = self.fetch()
        if instruction & 0x8000:  # C-instruction
            self.execute_c_instruction(instruction)
        else:  # A-instruction
            self.execute_a_instruction(instruction)

    def run(self, max_cycles=1000):
        """Run until halt or max cycles"""
        for _ in range(max_cycles):
            self.step()
            if self.PC >= len(self.ROM) or self.ROM[self.PC] == 0:
                break