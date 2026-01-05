class CodeGenerator:
    """Generate Hack assembly from VM commands"""

    def __init__(self, filename=None):
        self.label_counter = 0  # For unique labels in comparisons
        self.return_counter = 0  # For unique return addresses
        # Extract filename for static scope (remove path and .vm extension)
        if filename:
            self.current_file = filename.replace('.vm', '').split('/')[-1]
        else:
            self.current_file = "default"
        self.current_function = ""  # Track current function for label scoping

    def init(self):
        """Bootstrap code: initialize VM and call Sys.init"""
        asm = (
            "// ===== Bootstrap: Initialize VM State =====\n"
            "@256\n"
            "D=A\n"
            "@SP\n"
            "M=D           // SP = 256\n"
            "\n"
        )

        # Call Sys.init
        asm += (
            "// Call Sys.init\n"
            "@Sys.init$ret.bootstrap\n"
            "D=A\n"
            "@SP\n"
            "A=M\n"
            "M=D\n"
            "@SP\n"
            "M=M+1\n"
        )

        # Push dummy values for LCL, ARG, THIS, THAT
        # (Sys.init has no caller, but we maintain convention)
        for _ in range(4):
            asm += (
                "@SP\n"
                "A=M\n"
                "M=0\n"
                "@SP\n"
                "M=M+1\n"
            )

        # ARG = SP - 5 (0 arguments)
        asm += (
            "@SP\n"
            "D=M\n"
            "@5\n"
            "D=D-A\n"
            "@ARG\n"
            "M=D\n"
        )

        # LCL = SP
        asm += (
            "@SP\n"
            "D=M\n"
            "@LCL\n"
            "M=D\n"
        )

        # goto Sys.init
        asm += (
            "@Sys.init\n"
            "0;JMP\n"
            "(Sys.init$ret.bootstrap)\n"
        )

        return asm

    def generate(self, command):
        """Generate assembly for one VM command"""
        if command['type'] == 'arithmetic':
            return self.generate_arithmetic(command['operation'])
        elif command['type'] == 'push':
            return self.generate_push(command['segment'], command['index'])
        elif command['type'] == 'pop':
            return self.generate_pop(command['segment'], command['index'])
        # Program flow
        elif command['type'] == 'label':
            return self.generate_label(command['label'])
        elif command['type'] == 'goto':
            return self.generate_goto(command['label'])
        elif command['type'] == 'if-goto':
            return self.generate_if_goto(command['label'])
        # Function commands
        elif command['type'] == 'function':
            return self.generate_function(command['name'], command['nLocals'])
        elif command['type'] == 'call':
            return self.generate_call(command['name'], command['nArgs'])
        elif command['type'] == 'return':
            return self.generate_return()

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

    # ===== NEW: Program Flow Commands =====

    def generate_label(self, label):
        """Generate assembly for label command"""
        # Labels are scoped to current function to prevent collisions
        scoped_label = f"{self.current_function}${label}"
        return f"// label {label}\n({scoped_label})\n"

    def generate_goto(self, label):
        """Generate assembly for goto command"""
        scoped_label = f"{self.current_function}${label}"
        return (
            f"// goto {label}\n"
            f"@{scoped_label}\n"
            "0;JMP\n"
        )

    def generate_if_goto(self, label):
        """Generate assembly for if-goto command"""
        scoped_label = f"{self.current_function}${label}"
        return (
            f"// if-goto {label}\n"
            "@SP\n"
            "M=M-1\n"      # SP--
            "A=M\n"        # A = SP
            "D=M\n"        # D = popped value
            f"@{scoped_label}\n"
            "D;JNE\n"      # Jump if D ≠ 0
        )

    # ===== NEW: Function Commands =====

    def generate_function(self, name, n_locals):
        """Generate assembly for function declaration"""
        # Update current function context for label scoping
        self.current_function = name

        asm = f"// function {name} {n_locals}\n"
        asm += f"({name})\n"  # Entry point label

        # Initialize all local variables to 0
        for i in range(n_locals):
            asm += (
                "@SP\n"
                "A=M\n"
                "M=0\n"
                "@SP\n"
                "M=M+1\n"
            )

        return asm

    def generate_call(self, function_name, n_args):
        """Generate assembly for function call"""
        # Generate unique return address label
        return_label = f"{function_name}$ret.{self.return_counter}"
        self.return_counter += 1

        asm = f"// call {function_name} {n_args}\n"

        # Push return address
        asm += (
            f"@{return_label}\n"
            "D=A\n"
            "@SP\n"
            "A=M\n"
            "M=D\n"
            "@SP\n"
            "M=M+1\n"
        )

        # Push LCL, ARG, THIS, THAT
        for segment in ['LCL', 'ARG', 'THIS', 'THAT']:
            asm += (
                f"@{segment}\n"
                "D=M\n"
                "@SP\n"
                "A=M\n"
                "M=D\n"
                "@SP\n"
                "M=M+1\n"
            )

        # ARG = SP - nArgs - 5
        asm += (
            "@SP\n"
            "D=M\n"
            f"@{n_args + 5}\n"
            "D=D-A\n"
            "@ARG\n"
            "M=D\n"
        )

        # LCL = SP
        asm += (
            "@SP\n"
            "D=M\n"
            "@LCL\n"
            "M=D\n"
        )

        # goto function_name
        asm += (
            f"@{function_name}\n"
            "0;JMP\n"
        )

        # Return address label
        asm += f"({return_label})\n"

        return asm

    def generate_return(self):
        """Generate assembly for function return"""
        asm = "// return\n"

        # FRAME = LCL (save in R13)
        asm += (
            "@LCL\n"
            "D=M\n"
            "@R13\n"
            "M=D          // R13 = FRAME\n"
        )

        # RET = *(FRAME - 5) (save return address in R14)
        asm += (
            "@5\n"
            "A=D-A        // A = FRAME - 5\n"
            "D=M          // D = *(FRAME - 5)\n"
            "@R14\n"
            "M=D          // R14 = RET (return address)\n"
        )

        # *ARG = pop() (put return value at top of caller's stack)
        asm += (
            "@SP\n"
            "M=M-1\n"
            "A=M\n"
            "D=M          // D = return value\n"
            "@ARG\n"
            "A=M\n"
            "M=D          // *ARG = return value\n"
        )

        # SP = ARG + 1 (restore caller's SP)
        asm += (
            "@ARG\n"
            "D=M+1\n"
            "@SP\n"
            "M=D\n"
        )

        # Restore THAT, THIS, ARG, LCL
        for offset, segment in [(1, 'THAT'), (2, 'THIS'), (3, 'ARG'), (4, 'LCL')]:
            asm += (
                "@R13\n"
                "D=M\n"
                f"@{offset}\n"
                "A=D-A\n"
                "D=M\n"
                f"@{segment}\n"
                "M=D\n"
            )

        # goto RET
        asm += (
            "@R14\n"
            "A=M\n"
            "0;JMP\n"
        )

        return asm
