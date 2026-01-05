class CodeGenerator:
    """Generate Hack assembly from VM commands"""

    def __init__(self, filename=None):
        self.label_counter = 0  # For unique labels in comparisons
        # Extract filename for static scope (remove path and .vm extension)
        if filename:
            self.current_file = filename.replace('.vm', '').split('/')[-1]
        else:
            self.current_file = "default"

    def init(self):
        """Bootstrap code: initialize stack pointer"""
        return (
            "// ===== Bootstrap: Initialize VM State =====\n"
            "@256\n"
            "D=A\n"
            "@SP\n"
            "M=D           // SP = 256 (stack starts at RAM[256])\n"
            "\n"
        )

    def generate(self, command):
        """Generate assembly for one VM command"""
        if command['type'] == 'arithmetic':
            return self.generate_arithmetic(command['operation'])
        elif command['type'] == 'push':
            return self.generate_push(command['segment'], command['index'])
        elif command['type'] == 'pop':
            return self.generate_pop(command['segment'], command['index'])

    def generate_arithmetic(self, operation):
        """Generate assembly for arithmetic/logical operations"""

        # Binary operations: pop y, pop x, push (x op y)
        if operation in ['add', 'sub', 'and', 'or']:
            asm = (
                f"// {operation}\n"
                "@SP\n"
                "M=M-1\n"      # SP--
                "A=M\n"        # A = SP
                "D=M\n"        # D = RAM[SP] = y (second operand)
                "@SP\n"
                "M=M-1\n"      # SP--
                "A=M\n"        # A = SP
            )

            # Perform operation
            # Note: Hack ISA supports D+M, D-M, D&M, D|M but not M+D, M-D, etc.
            # We must ensure D is the first operand
            if operation == 'add':
                asm += "M=D+M\n"    # RAM[SP] = y + x (commutative)
            elif operation == 'sub':
                asm += "M=M-D\n"    # RAM[SP] = x - y (not commutative!)
            elif operation == 'and':
                asm += "M=D&M\n"    # RAM[SP] = y & x (commutative)
            elif operation == 'or':
                asm += "M=D|M\n"    # RAM[SP] = y | x (commutative)

            asm += (
                "@SP\n"
                "M=M+1\n"      # SP++
            )

            return asm

        # Unary operations: pop x, push (op x)
        elif operation in ['neg', 'not']:
            asm = (
                f"// {operation}\n"
                "@SP\n"
                "M=M-1\n"      # SP--
                "A=M\n"        # A = SP
            )

            if operation == 'neg':
                asm += "M=-M\n"     # RAM[SP] = -RAM[SP]
            elif operation == 'not':
                asm += "M=!M\n"     # RAM[SP] = !RAM[SP]

            asm += (
                "@SP\n"
                "M=M+1\n"      # SP++
            )

            return asm

        # Comparison operations: pop y, pop x, push (x op y ? -1 : 0)
        elif operation in ['eq', 'gt', 'lt']:
            label_true = f"TRUE_{self.label_counter}"
            label_end = f"END_{self.label_counter}"
            self.label_counter += 1

            asm = (
                f"// {operation}\n"
                "@SP\n"
                "M=M-1\n"      # SP--
                "A=M\n"        # A = SP
                "D=M\n"        # D = y (second operand)
                "@SP\n"
                "M=M-1\n"      # SP--
                "A=M\n"        # A = SP
                "D=M-D\n"      # D = x - y
            )

            # Jump based on comparison
            if operation == 'eq':
                asm += f"@{label_true}\nD;JEQ\n"  # Jump if x == y
            elif operation == 'gt':
                asm += f"@{label_true}\nD;JGT\n"  # Jump if x > y
            elif operation == 'lt':
                asm += f"@{label_true}\nD;JLT\n"  # Jump if x < y

            # False case: push 0
            asm += (
                "@SP\n"
                "A=M\n"
                "M=0\n"        # RAM[SP] = 0 (false)
                f"@{label_end}\n"
                "0;JMP\n"
            )

            # True case: push -1
            asm += (
                f"({label_true})\n"
                "@SP\n"
                "A=M\n"
                "M=-1\n"       # RAM[SP] = -1 (true)
            )

            # Continue
            asm += (
                f"({label_end})\n"
                "@SP\n"
                "M=M+1\n"      # SP++
            )

            return asm

    def generate_push(self, segment, index):
        """Generate assembly for push commands"""

        # Segment: constant (push literal value)
        if segment == 'constant':
            return (
                f"// push constant {index}\n"
                f"@{index}\n"
                "D=A\n"          # D = constant value
                "@SP\n"
                "A=M\n"          # A = *SP
                "M=D\n"          # RAM[SP] = value
                "@SP\n"
                "M=M+1\n"        # SP++
            )

        # Segments: local, argument, this, that (pointer-based)
        elif segment in ['local', 'argument', 'this', 'that']:
            # Map segment name to pointer symbol
            pointer_map = {
                'local': 'LCL',
                'argument': 'ARG',
                'this': 'THIS',
                'that': 'THAT'
            }
            pointer = pointer_map[segment]

            return (
                f"// push {segment} {index}\n"
                f"@{pointer}\n"
                "D=M\n"          # D = base address
                f"@{index}\n"
                "A=D+A\n"        # A = base + index
                "D=M\n"          # D = RAM[base + index]
                "@SP\n"
                "A=M\n"          # A = *SP
                "M=D\n"          # RAM[SP] = value
                "@SP\n"
                "M=M+1\n"        # SP++
            )

        # Segment: temp (direct addressing, RAM[5-12])
        elif segment == 'temp':
            address = 5 + index  # temp[0] = RAM[5], temp[1] = RAM[6], etc.
            return (
                f"// push temp {index}\n"
                f"@{address}\n"
                "D=M\n"          # D = RAM[5+index]
                "@SP\n"
                "A=M\n"          # A = *SP
                "M=D\n"          # RAM[SP] = value
                "@SP\n"
                "M=M+1\n"        # SP++
            )

        # Segment: pointer (access THIS/THAT base addresses)
        elif segment == 'pointer':
            pointer = 'THIS' if index == 0 else 'THAT'
            return (
                f"// push pointer {index}\n"
                f"@{pointer}\n"
                "D=M\n"          # D = THIS or THAT base address
                "@SP\n"
                "A=M\n"          # A = *SP
                "M=D\n"          # RAM[SP] = base address
                "@SP\n"
                "M=M+1\n"        # SP++
            )

        # Segment: static (global variables, RAM[16-255])
        elif segment == 'static':
            # Static variables are file-scoped
            # Use filename.index as symbol (e.g., Main.0, Main.1)
            static_symbol = f"{self.current_file}.{index}"
            return (
                f"// push static {index}\n"
                f"@{static_symbol}\n"
                "D=M\n"          # D = RAM[symbol]
                "@SP\n"
                "A=M\n"          # A = *SP
                "M=D\n"          # RAM[SP] = value
                "@SP\n"
                "M=M+1\n"        # SP++
            )

    def generate_pop(self, segment, index):
        """Generate assembly for pop commands"""

        # Cannot pop to constant segment!
        if segment == 'constant':
            raise ValueError("Cannot pop to constant segment")

        # Segments: local, argument, this, that (pointer-based)
        if segment in ['local', 'argument', 'this', 'that']:
            pointer_map = {
                'local': 'LCL',
                'argument': 'ARG',
                'this': 'THIS',
                'that': 'THAT'
            }
            pointer = pointer_map[segment]

            return (
                f"// pop {segment} {index}\n"
                # Calculate destination address
                f"@{pointer}\n"
                "D=M\n"          # D = base address
                f"@{index}\n"
                "D=D+A\n"        # D = base + index (destination address)
                "@R13\n"
                "M=D\n"          # RAM[13] = destination address (temp storage)
                # Pop value from stack
                "@SP\n"
                "M=M-1\n"        # SP--
                "A=M\n"          # A = SP
                "D=M\n"          # D = popped value
                # Write to destination
                "@R13\n"
                "A=M\n"          # A = destination address
                "M=D\n"          # RAM[destination] = popped value
            )

        # Segment: temp (direct addressing)
        elif segment == 'temp':
            address = 5 + index
            return (
                f"// pop temp {index}\n"
                "@SP\n"
                "M=M-1\n"        # SP--
                "A=M\n"          # A = SP
                "D=M\n"          # D = popped value
                f"@{address}\n"
                "M=D\n"          # RAM[5+index] = value
            )

        # Segment: pointer (write to THIS/THAT base address)
        elif segment == 'pointer':
            pointer = 'THIS' if index == 0 else 'THAT'
            return (
                f"// pop pointer {index}\n"
                "@SP\n"
                "M=M-1\n"        # SP--
                "A=M\n"          # A = SP
                "D=M\n"          # D = popped value
                f"@{pointer}\n"
                "M=D\n"          # THIS/THAT = value
            )

        # Segment: static
        elif segment == 'static':
            static_symbol = f"{self.current_file}.{index}"
            return (
                f"// pop static {index}\n"
                "@SP\n"
                "M=M-1\n"        # SP--
                "A=M\n"          # A = SP
                "D=M\n"          # D = popped value
                f"@{static_symbol}\n"
                "M=D\n"          # RAM[symbol] = value
            )