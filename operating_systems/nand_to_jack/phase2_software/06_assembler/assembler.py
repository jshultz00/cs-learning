class SymbolTable:
    """Manages symbol-to-address mappings"""

    def __init__(self):
        # Initialize with predefined symbols
        self.symbols = {
            # Virtual registers
            'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4,
            'R5': 5, 'R6': 6, 'R7': 7, 'R8': 8, 'R9': 9,
            'R10': 10, 'R11': 11, 'R12': 12, 'R13': 13,
            'R14': 14, 'R15': 15,

            # Special pointers
            'SP': 0,     # Stack pointer
            'LCL': 1,    # Local base
            'ARG': 2,    # Argument base
            'THIS': 3,   # This pointer
            'THAT': 4,   # That pointer

            # I/O addresses
            'SCREEN': 16384,  # 0x4000
            'KBD': 24576      # 0x6000
        }

    def add_label(self, symbol, address):
        """Add a label with its instruction address"""
        if symbol in self.symbols:
            raise ValueError(f"Duplicate symbol: {symbol}")
        self.symbols[symbol] = address

    def add_variable(self, symbol, address):
        """Add a variable with its RAM address"""
        if symbol in self.symbols:
            return self.symbols[symbol]  # Already exists
        self.symbols[symbol] = address
        return address

    def contains(self, symbol):
        """Check if symbol exists"""
        return symbol in self.symbols

    def get_address(self, symbol):
        """Get address of symbol"""
        return self.symbols.get(symbol)


class Parser:
    """Parses assembly language into instruction components"""

    def __init__(self, filename):
        with open(filename, 'r') as f:
            # Read all lines and store for processing
            self.lines = [line.strip() for line in f.readlines()]
        self.current_line = 0

    def has_more_lines(self):
        """Check if more lines remain"""
        return self.current_line < len(self.lines)

    def advance(self):
        """Move to next line"""
        self.current_line += 1

    def reset(self):
        """Reset to beginning (for second pass)"""
        self.current_line = 0

    def current_instruction(self):
        """Get current line with comments and whitespace removed"""
        line = self.lines[self.current_line]

        # Remove comments
        if '//' in line:
            line = line[:line.index('//')]

        # Remove whitespace
        return line.strip()

    def instruction_type(self):
        """Determine instruction type: A, C, or L (label)"""
        instruction = self.current_instruction()

        if not instruction:
            return None  # Empty line

        if instruction.startswith('@'):
            return 'A'
        elif instruction.startswith('(') and instruction.endswith(')'):
            return 'L'  # Label
        else:
            return 'C'

    def symbol(self):
        """Extract symbol from A-instruction or label"""
        instruction = self.current_instruction()

        if instruction.startswith('@'):
            return instruction[1:]  # Remove '@'
        elif instruction.startswith('('):
            return instruction[1:-1]  # Remove '(' and ')'
        else:
            raise ValueError("Not an A-instruction or label")

    def dest(self):
        """Extract dest field from C-instruction"""
        instruction = self.current_instruction()

        if '=' in instruction:
            return instruction.split('=')[0].strip()
        return ""  # No destination

    def comp(self):
        """Extract comp field from C-instruction"""
        instruction = self.current_instruction()

        # Remove dest if present
        if '=' in instruction:
            instruction = instruction.split('=')[1]

        # Remove jump if present
        if ';' in instruction:
            instruction = instruction.split(';')[0]

        return instruction.strip()

    def jump(self):
        """Extract jump field from C-instruction"""
        instruction = self.current_instruction()

        if ';' in instruction:
            return instruction.split(';')[1].strip()
        return ""  # No jump


class CodeGenerator:
    """Translates assembly mnemonics to binary machine code"""

    def __init__(self):
        # Computation lookup table (from Project 4)
        self.comp_table = {
            # a=0 (use A register)
            "0":   "0101010",
            "1":   "0111111",
            "-1":  "0111010",
            "D":   "0001100",
            "A":   "0110000",
            "!D":  "0001101",
            "!A":  "0110001",
            "-D":  "0001111",
            "-A":  "0110011",
            "D+1": "0011111",
            "A+1": "0110111",
            "D-1": "0001110",
            "A-1": "0110010",
            "D+A": "0000010",
            "D-A": "0010011",
            "A-D": "0000111",
            "D&A": "0000000",
            "D|A": "0010101",

            # a=1 (use M register, RAM[A])
            "M":   "1110000",
            "!M":  "1110001",
            "-M":  "1110011",
            "M+1": "1110111",
            "M-1": "1110010",
            "D+M": "1000010",
            "D-M": "1010011",
            "M-D": "1000111",
            "D&M": "1000000",
            "D|M": "1010101",
        }

        # Destination lookup table
        self.dest_table = {
            "":    "000",
            "M":   "001",
            "D":   "010",
            "MD":  "011",
            "A":   "100",
            "AM":  "101",
            "AD":  "110",
            "AMD": "111",
        }

        # Jump lookup table
        self.jump_table = {
            "":    "000",
            "JGT": "001",
            "JEQ": "010",
            "JGE": "011",
            "JLT": "100",
            "JNE": "101",
            "JLE": "110",
            "JMP": "111",
        }

    def generate_a_instruction(self, address):
        """Generate binary for A-instruction: @address"""
        # Convert to 15-bit binary
        binary = format(int(address), '015b')
        return '0' + binary  # A-instruction starts with 0

    def generate_c_instruction(self, dest, comp, jump):
        """Generate binary for C-instruction: dest=comp;jump"""
        try:
            comp_bits = self.comp_table[comp]
            dest_bits = self.dest_table[dest]
            jump_bits = self.jump_table[jump]
        except KeyError as e:
            raise ValueError(f"Invalid mnemonic: {e}")

        # C-instruction: 111accccccdddjjj
        return '111' + comp_bits + dest_bits + jump_bits


class AssemblerError(Exception):
    """Custom exception for assembly errors"""
    pass

class Assembler:
    """Enhanced assembler with error handling"""

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.code_gen = CodeGenerator()
        self.debug = False  # Enable debug output

    def assemble(self, input_filename, output_filename, debug=False):
        """Assemble with error handling"""
        self.debug = debug

        try:
            # Pass 1
            if self.debug:
                print("=== PASS 1: Building Symbol Table ===")
            self._first_pass(input_filename)

            if self.debug:
                print("\nSymbol Table:")
                for symbol, address in sorted(self.symbol_table.symbols.items()):
                    if address >= 16 or symbol in ['SCREEN', 'KBD']:
                        print(f"  {symbol}: {address}")

            # Pass 2
            if self.debug:
                print("\n=== PASS 2: Generating Code ===")
            binary_code = self._second_pass(input_filename)

            # Write output
            with open(output_filename, 'w') as f:
                for instruction in binary_code:
                    f.write(instruction + '\n')

            print(f"✓ Assembly successful: {len(binary_code)} instructions generated")
            return binary_code

        except AssemblerError as e:
            print(f"✗ Assembly failed: {e}")
            raise
        except FileNotFoundError:
            print(f"✗ File not found: {input_filename}")
            raise

    def _first_pass(self, filename):
        """Pass 1 with error checking"""
        parser = Parser(filename)
        instruction_address = 0
        line_number = 0

        while parser.has_more_lines():
            line_number += 1
            instruction = parser.current_instruction()

            if not instruction:
                parser.advance()
                continue

            try:
                inst_type = parser.instruction_type()

                if inst_type == 'L':
                    label = parser.symbol()

                    # Validate label name
                    if not self._is_valid_symbol(label):
                        raise AssemblerError(
                            f"Line {line_number}: Invalid label name '{label}'"
                        )

                    # Check for duplicate
                    if label in self.symbol_table.symbols:
                        raise AssemblerError(
                            f"Line {line_number}: Duplicate label '{label}'"
                        )

                    self.symbol_table.add_label(label, instruction_address)

                    if self.debug:
                        print(f"  Line {line_number}: Label {label} → {instruction_address}")

                else:
                    instruction_address += 1

            except Exception as e:
                raise AssemblerError(f"Line {line_number}: {e}")

            parser.advance()

    def _second_pass(self, filename):
        """Pass 2 with error checking"""
        parser = Parser(filename)
        binary_code = []
        next_variable_address = 16
        line_number = 0

        while parser.has_more_lines():
            line_number += 1
            instruction = parser.current_instruction()

            if not instruction:
                parser.advance()
                continue

            try:
                inst_type = parser.instruction_type()

                if inst_type == 'A':
                    symbol = parser.symbol()

                    if symbol.isdigit():
                        address = int(symbol)

                        # Validate range
                        if address < 0 or address > 32767:
                            raise AssemblerError(
                                f"Address {address} out of range (0-32767)"
                            )

                    elif self.symbol_table.contains(symbol):
                        address = self.symbol_table.get_address(symbol)

                    else:
                        # Validate variable name
                        if not self._is_valid_symbol(symbol):
                            raise AssemblerError(f"Invalid symbol name '{symbol}'")

                        address = self.symbol_table.add_variable(symbol, next_variable_address)
                        next_variable_address += 1

                        if self.debug:
                            print(f"  Line {line_number}: Variable {symbol} → {address}")

                    binary = self.code_gen.generate_a_instruction(address)
                    binary_code.append(binary)

                    if self.debug:
                        print(f"  Line {line_number}: @{symbol} → {binary}")

                elif inst_type == 'C':
                    dest = parser.dest()
                    comp = parser.comp()
                    jump = parser.jump()

                    binary = self.code_gen.generate_c_instruction(dest, comp, jump)
                    binary_code.append(binary)

                    if self.debug:
                        inst_str = f"{dest+'=' if dest else ''}{comp}{';'+jump if jump else ''}"
                        print(f"  Line {line_number}: {inst_str} → {binary}")

            except ValueError as e:
                raise AssemblerError(f"Line {line_number}: {e}")

            parser.advance()

        return binary_code

    def _is_valid_symbol(self, symbol):
        """Check if symbol name is valid"""
        if not symbol:
            return False

        # Cannot start with digit
        if symbol[0].isdigit():
            return False

        # Valid characters: alphanumeric, _, ., $, :
        valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.$:')
        return all(c in valid_chars for c in symbol)


