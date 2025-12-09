# Project 7: Stack-Based Virtual Machine (Part 1)

**Objective**: Build a VM translator for stack arithmetic and memory operations

## Background Concepts

### What You've Built So Far

**Phase 1: Hardware Layer (Projects 1-5)**
- **Logic Gates**: Built all Boolean operations from NAND primitives
- **Binary Arithmetic**: Created an ALU capable of 18+ operations
- **Memory Hierarchy**: Implemented sequential logic (DFF → Register → RAM)
- **Assembly Emulator**: Understood instruction execution at the hardware level
- **Computer Architecture**: Integrated CPU, ALU, RAM, ROM into a Von Neumann computer

**Project 6: Assembler (Symbol Resolution)**
- **Two-pass translation**: Built assembler that resolves labels and variables
- **Symbol table**: Mapped symbolic names to numeric addresses
- **Machine code generation**: Translated assembly to binary instructions

Now you can write programs with **symbolic assembly**:
```assembly
@i          // Variables (no manual address tracking!)
M=1         // Initialize counter
@sum        // Another variable
M=0         // Initialize accumulator

(LOOP)      // Labels (no manual jump addresses!)
    @i
    D=M
    @100
    D=D-A
    @END
    D;JGT   // Jump if i > 100

    // ... loop body ...

    @LOOP
    0;JMP

(END)
    @END
    0;JMP   // Infinite loop (halt)
```

Your assembler automatically handles:
- ✅ Variable allocation (assigns RAM addresses)
- ✅ Label resolution (calculates instruction addresses)
- ✅ Predefined symbols (`R0`-`R15`, `SCREEN`, `KBD`, `SP`, `LCL`, etc.)

This is **powerful**—you have a complete toolchain from assembly to execution! But there's a problem...

### The Problem: Assembly is Too Low-Level

Writing complex programs in assembly is **painful**:

**Problem 1: No expressions**
```assembly
// To compute: (x + 5) * (y - 2)
@5
D=A
@x
D=D+M        // D = x + 5 (temp1)
@R13
M=D          // Store temp1 in R13
@2
D=A
@y
D=M-D        // D = y - 2 (temp2)
@R13
D=D*M        // D = temp1 * temp2 (WAIT—no multiply instruction!)
// Now we need a multiply loop...
```

**Problem 2: No function calls**
```assembly
// How do you call a function?
// - Where do you store return address?
// - How do you pass arguments?
// - How do you allocate local variables?
// - How do you return values?
// Every program solves this differently!
```

**Problem 3: No memory abstraction**
```assembly
// Managing memory manually:
@16      // Variable x lives at RAM[16]
@17      // Variable y lives at RAM[17]
@18      // Variable z lives at RAM[18]
// What if you add a variable? Renumber everything!
// What if functions need local variables? Conflicts!
```

**Problem 4: Machine-specific**
```assembly
// This assembly only runs on YOUR computer
// Want to run on ARM? Rewrite everything
// Want to run on x86? Rewrite everything
// Want to run on RISC-V? Rewrite everything
```

### The Solution: Virtual Machines

A **virtual machine (VM)** is an abstraction layer between high-level languages and hardware:

```
┌─────────────────────────────────────────┐
│    High-Level Language (Jack, Java)     │  Human-friendly
├─────────────────────────────────────────┤
│    Virtual Machine Bytecode (VM)        │  ← YOU ARE HERE
├─────────────────────────────────────────┤
│    Assembly Language                    │  ← YOU BUILT THIS
├─────────────────────────────────────────┤
│    Machine Code (binary)                │
├─────────────────────────────────────────┤
│    Hardware (CPU, RAM, etc.)            │  ← YOU BUILT THIS
└─────────────────────────────────────────┘
```

**Key insight**: Instead of compiling directly to assembly, high-level languages compile to **VM bytecode**. Then a **VM translator** (which you'll build in this project) converts VM code to assembly.

**Why this is brilliant**:

1. **Portability**: Write VM translator once per platform, all languages work everywhere
   - VM code is the same on ARM, x86, RISC-V, etc.
   - Only the VM translator needs to be rewritten per platform

2. **Simpler compilers**: Compiler targets abstract stack machine, not specific CPU
   - Don't need to know about registers, instruction encodings, etc.
   - Same compiler works for all hardware platforms

3. **Higher-level abstractions**: VM provides features assembly lacks
   - Function calls with automatic stack management
   - Memory segments (local, argument, static, etc.)
   - Structured control flow

4. **Real-world pattern**: This is how Java, Python, C#, and many languages work
   - Java → JVM bytecode → native code (via JIT compiler)
   - Python → CPython bytecode → interpreted
   - C# → CLR bytecode → native code

### Stack-Based Architecture

Your hardware computer uses **registers** (A, D, PC). The VM uses a **stack** instead.

**Stack: Last-In-First-Out (LIFO) data structure**

```
Initial state:           Push 5:              Push 3:              Add:
┌─────┐                ┌─────┐              ┌─────┐              ┌─────┐
│     │                │     │              │  3  │ ← SP         │  8  │ ← SP
│     │                │  5  │ ← SP         │  5  │              │     │
└─────┘                └─────┘              └─────┘              └─────┘
  SP
(empty)
```

**Stack operations**:
- `push constant 5`: Push value 5 onto stack, increment SP
- `push constant 3`: Push value 3 onto stack, increment SP
- `add`: Pop two values (3, 5), compute 5+3, push result (8)

**Why stack-based?**

1. **No register allocation**: Compiler doesn't need to track which registers are free
2. **Simple instruction encoding**: Operations are implicit (add pops two values)
3. **Natural expression evaluation**: Directly matches how expressions are computed
4. **Unlimited virtual registers**: Stack can grow arbitrarily (unlike fixed register count)

**Example: Translate expression to stack code**

Expression: `(x + 5) * (y - 2)`

Stack code:
```
push local 0    // Push x onto stack
push constant 5 // Push 5 onto stack
add             // Pop two values, compute x+5, push result
push local 1    // Push y onto stack
push constant 2 // Push 2 onto stack
sub             // Pop two values, compute y-2, push result
call Math.multiply 2  // Call multiply function (two arguments)
```

This is **dramatically simpler** than the assembly version we attempted earlier!

🎓 **Key insight**: The stack is a **temporary workspace** for computation. Arguments flow in via pushes, operations consume them, results flow out via pops.

### Memory Segments

The VM organizes memory into **logical segments**, not raw addresses:

```
Memory Map (Conceptual):
┌──────────────────────────────────────┐
│  Stack (256-2047)                    │  Dynamic workspace
├──────────────────────────────────────┤
│  Local (variable positions)          │  Current function's local variables
├──────────────────────────────────────┤
│  Argument (variable positions)       │  Function arguments
├──────────────────────────────────────┤
│  This (heap pointer)                 │  Object reference
├──────────────────────────────────────┤
│  That (heap pointer)                 │  Array/object base
├──────────────────────────────────────┤
│  Temp (5-12)                         │  Scratch space
├──────────────────────────────────────┤
│  Pointer (THIS, THAT base addresses) │  Segment pointers
├──────────────────────────────────────┤
│  Static (16-255)                     │  Global variables (per file)
└──────────────────────────────────────┘
```

**Eight memory segments**:

1. **constant**: Virtual segment (0-32767), read-only, used for constants
2. **local**: Function's local variables (LCL pointer-based)
3. **argument**: Function's arguments (ARG pointer-based)
4. **this**: Current object/array (THIS pointer-based)
5. **that**: Another object/array (THAT pointer-based)
6. **temp**: Temporary storage (RAM[5-12], only 8 slots!)
7. **pointer**: Access THIS (pointer 0) or THAT (pointer 1) base addresses
8. **static**: Global variables (RAM[16-255], unique per .vm file)

**Segment operations**:
```
push local 2       // Push value from local[2] onto stack
pop argument 0     // Pop value from stack into argument[0]
push constant 42   // Push constant 42 onto stack
push temp 5        // Push value from temp[5] onto stack
push pointer 0     // Push THIS base address onto stack
push static 3      // Push value from static[3] onto stack
```

🎓 **Key insight**: Segments provide **memory abstraction**. Compilers don't manage raw addresses—they use symbolic segment names. The VM translator handles the mapping to actual RAM addresses.

### VM-to-Assembly Translation Strategy

Your job: Translate VM commands to Hack assembly.

**Example 1: Simple arithmetic**

VM code:
```
push constant 7
push constant 8
add
```

Assembly translation:
```assembly
// push constant 7
@7
D=A           // D = 7
@SP
A=M           // A = *SP (current stack top)
M=D           // RAM[SP] = 7
@SP
M=M+1         // SP++

// push constant 8
@8
D=A           // D = 8
@SP
A=M           // A = *SP
M=D           // RAM[SP] = 8
@SP
M=M+1         // SP++

// add
@SP
M=M-1         // SP--
A=M           // A = SP (now points to second operand)
D=M           // D = second operand (8)
@SP
M=M-1         // SP--
A=M           // A = SP (now points to first operand)
M=M+D         // RAM[SP] = first + second (7 + 8 = 15)
@SP
M=M+1         // SP++ (result is now on top of stack)
```

**Pattern**: All arithmetic operations follow this structure:
1. Pop operand(s) from stack
2. Perform computation
3. Push result back onto stack

**Example 2: Memory segment access**

VM code:
```
push local 2
```

Assembly translation:
```assembly
// push local 2
@2            // Offset within segment
D=A           // D = 2
@LCL          // LCL is base address of local segment
A=M+D         // A = base + offset = address of local[2]
D=M           // D = RAM[local[2]] (the value)
@SP
A=M           // A = *SP
M=D           // RAM[SP] = value
@SP
M=M+1         // SP++
```

**Pattern for segment access**:
- **Push**: `address = segment_base + offset`, then `push RAM[address]`
- **Pop**: `address = segment_base + offset`, then `RAM[address] = pop()`

### The VM Instruction Set (Project 7 Subset)

**Arithmetic/Logical Commands** (9 operations):

```
add        // Pop y, pop x, push x+y
sub        // Pop y, pop x, push x-y
neg        // Pop x, push -x
eq         // Pop y, pop x, push (x==y ? -1 : 0)
gt         // Pop y, pop x, push (x>y ? -1 : 0)
lt         // Pop y, pop x, push (x<y ? -1 : 0)
and        // Pop y, pop x, push x&y (bitwise AND)
or         // Pop y, pop x, push x|y (bitwise OR)
not        // Pop x, push !x (bitwise NOT)
```

**Boolean representation**: True = -1 (0xFFFF), False = 0 (0x0000)
- Why -1? All bits set makes bitwise operations natural
- `and`, `or`, `not` work as logical AND, OR, NOT

**Memory Access Commands** (2 operations):

```
push <segment> <index>    // Push RAM[segment[index]] onto stack
pop <segment> <index>     // Pop stack into RAM[segment[index]]
```

**Segments**: `constant`, `local`, `argument`, `this`, `that`, `temp`, `pointer`, `static`

**Important**: `push constant <value>` pushes the literal value, not a memory lookup!

### VM Translator Architecture

Your translator follows this flow:

```
┌──────────────────┐
│  VM File (.vm)   │  Input: VM commands as text
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    Parser        │  Parse each line into command type + arguments
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Code Generator  │  Generate assembly for each VM command
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Assembly (.asm)  │  Output: Hack assembly language
└──────────────────┘
```

**Three main components**:

1. **Parser**: Read VM file, tokenize commands
   - Skip whitespace and comments
   - Identify command type (push/pop/add/sub/etc.)
   - Extract arguments (segment, index)

2. **Code Generator**: Emit assembly for each command
   - Maintain assembly snippet templates
   - Generate unique labels for comparisons
   - Handle segment-to-RAM address mapping

3. **Main Loop**: Coordinate parsing and code generation
   - Read VM command
   - Generate assembly
   - Write to output file

## Learning Path

### Step 1: Set Up Project Structure (30 minutes)

Create a clean architecture for your VM translator:

```
07_vm_part1/
├── vm_translator.py       # Main translator class
├── parser.py              # VM command parser
├── code_generator.py      # Assembly code generation
├── test_vm_translator.py  # Unit tests
├── examples/              # Test VM programs
│   ├── simple_add.vm      # Basic arithmetic
│   ├── stack_test.vm      # All arithmetic operations
│   ├── basic_test.vm      # Memory segment operations
│   └── pointer_test.vm    # Pointer segment
└── README.md              # Documentation
```

**Starter code structure**:

```python
# vm_translator.py
class VMTranslator:
    """Main VM-to-Assembly translator"""

    def __init__(self, input_file):
        self.input_file = input_file
        self.output_file = input_file.replace('.vm', '.asm')
        self.parser = Parser(input_file)
        self.code_gen = CodeGenerator()

    def translate(self):
        """Translate entire VM file to assembly"""
        with open(self.output_file, 'w') as out:
            # Write bootstrap code
            out.write(self.code_gen.init())

            # Translate each VM command
            while self.parser.has_more_commands():
                self.parser.advance()
                asm = self.code_gen.generate(self.parser.current_command)
                out.write(asm)
```

```python
# parser.py
class Parser:
    """Parse VM commands from input file"""

    def __init__(self, input_file):
        with open(input_file, 'r') as f:
            self.lines = f.readlines()
        self.current_line = 0
        self.current_command = None

    def has_more_commands(self):
        """Are there more commands to parse?"""
        return self.current_line < len(self.lines)

    def advance(self):
        """Read next command, parse into components"""
        while self.has_more_commands():
            line = self.lines[self.current_line].strip()
            self.current_line += 1

            # Skip blank lines and comments
            if not line or line.startswith('//'):
                continue

            # Remove inline comments
            line = line.split('//')[0].strip()

            # Parse command
            self.current_command = self.parse_command(line)
            break

    def parse_command(self, line):
        """Parse command into {type, arg1, arg2}"""
        parts = line.split()
        cmd_type = parts[0]

        if cmd_type in ['add', 'sub', 'neg', 'eq', 'gt', 'lt',
                        'and', 'or', 'not']:
            return {'type': 'arithmetic', 'operation': cmd_type}

        elif cmd_type == 'push':
            return {'type': 'push', 'segment': parts[1], 'index': int(parts[2])}

        elif cmd_type == 'pop':
            return {'type': 'pop', 'segment': parts[1], 'index': int(parts[2])}

        else:
            raise ValueError(f"Unknown command: {cmd_type}")
```

```python
# code_generator.py
class CodeGenerator:
    """Generate Hack assembly from VM commands"""

    def __init__(self):
        self.label_counter = 0  # For unique labels in comparisons

    def init(self):
        """Bootstrap code: initialize stack pointer"""
        return (
            "// Bootstrap: Initialize SP to 256\n"
            "@256\n"
            "D=A\n"
            "@SP\n"
            "M=D\n"
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
        # TODO: Implement in Step 2
        pass

    def generate_push(self, segment, index):
        """Generate assembly for push commands"""
        # TODO: Implement in Step 3
        pass

    def generate_pop(self, segment, index):
        """Generate assembly for pop commands"""
        # TODO: Implement in Step 3
        pass
```

**What to understand**:
- **Separation of concerns**: Parser reads, CodeGenerator writes, VMTranslator orchestrates
- **Stateless parser**: Each command is parsed independently
- **Stateful code generator**: Needs unique labels for comparisons

### Step 2: Implement Arithmetic Operations (3-4 hours)

Arithmetic operations are the core of stack computation. Implement all nine operations.

**Two patterns**:

**Pattern 1: Binary operations** (add, sub, and, or)
```python
def generate_arithmetic(self, operation):
    """Generate assembly for arithmetic operations"""

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
            asm += "M=M+D\n"    # RAM[SP] = x + y
        elif operation == 'sub':
            asm += "M=M-D\n"    # RAM[SP] = x - y
        elif operation == 'and':
            asm += "M=M&D\n"    # RAM[SP] = x & y
        elif operation == 'or':
            asm += "M=M|D\n"    # RAM[SP] = x | y

        asm += (
            "@SP\n"
            "M=M+1\n"      # SP++
        )

        return asm
```

**Pattern 2: Unary operations** (neg, not)
```python
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
```

**Pattern 3: Comparison operations** (eq, gt, lt)

These are **tricky** because they need conditional jumps and unique labels:

```python
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
```

🎓 **Key insight**: Comparisons use the ALU's status flags indirectly. We compute `x - y` and jump based on the result's sign. This mirrors how real CPUs implement comparisons!

**Testing arithmetic operations**:

Create `examples/simple_add.vm`:
```
// Simple addition: 7 + 8 = 15
push constant 7
push constant 8
add
```

Create `examples/stack_test.vm`:
```
// Test all arithmetic operations
push constant 17
push constant 17
eq            // true (-1)

push constant 17
push constant 16
eq            // false (0)

push constant 16
push constant 17
gt            // false (0)

push constant 17
push constant 16
gt            // true (-1)

push constant 16
push constant 17
lt            // true (-1)

push constant 17
push constant 16
lt            // false (0)

push constant 892
push constant 891
lt            // false (0)

push constant 891
push constant 892
lt            // true (-1)

push constant 32767
push constant 32766
gt            // true (-1)

push constant 32766
push constant 32767
gt            // false (0)

push constant 32766
push constant 32767
lt            // true (-1)

push constant 32767
push constant 32766
lt            // false (0)

push constant 57
push constant 31
push constant 53
add
push constant 112
sub
neg
and
push constant 82
or
not
```

**Run tests**:
```python
# test_vm_translator.py
import unittest
from vm_translator import VMTranslator
from computer_architecture import CPU, Assembler

class TestArithmetic(unittest.TestCase):
    def test_simple_add(self):
        """Test 7 + 8 = 15"""
        translator = VMTranslator('examples/simple_add.vm')
        translator.translate()

        # Load and run generated assembly
        cpu = CPU()
        asm = Assembler()
        with open('examples/simple_add.asm', 'r') as f:
            program = [line.strip() for line in f if line.strip() and not line.startswith('//')]
        binary = asm.assemble(program)
        cpu.load_program(binary)
        cpu.run(max_cycles=1000)

        # Check result: should be at stack top (SP-1)
        sp = cpu.ram[0]  # SP is at RAM[0]
        result = cpu.ram[sp - 1]
        self.assertEqual(result, 15)

    def test_stack_operations(self):
        """Test all arithmetic operations"""
        translator = VMTranslator('examples/stack_test.vm')
        translator.translate()

        cpu = CPU()
        asm = Assembler()
        with open('examples/stack_test.asm', 'r') as f:
            program = [line.strip() for line in f if line.strip() and not line.startswith('//')]
        binary = asm.assemble(program)
        cpu.load_program(binary)
        cpu.run(max_cycles=10000)

        # Check final stack state
        sp = cpu.ram[0]
        # After all operations, stack should have specific values
        # (exact values depend on test case expectations)
        self.assertTrue(sp > 256)  # Stack has grown
```

### Step 3: Implement Memory Segments (4-5 hours)

Memory segments map VM abstraction to physical RAM. Each segment has different translation rules.

**Segment address mapping**:

| Segment   | Base Address | Access Method | Range |
|-----------|-------------|---------------|-------|
| `local`   | RAM[LCL]    | Pointer-based | Dynamic |
| `argument`| RAM[ARG]    | Pointer-based | Dynamic |
| `this`    | RAM[THIS]   | Pointer-based | Dynamic |
| `that`    | RAM[THAT]   | Pointer-based | Dynamic |
| `constant`| N/A         | Immediate     | 0-32767 |
| `static`  | RAM[16+]    | Direct        | 16-255 |
| `temp`    | RAM[5-12]   | Direct        | 5-12 |
| `pointer` | RAM[3-4]    | Direct        | 3=THIS, 4=THAT |

**Implementation**:

```python
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
            f"@{index}\n"
            "D=A\n"          # D = index
            f"@{pointer}\n"
            "A=M+D\n"        # A = base + index
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
```

**Pop implementation**:

Pop is trickier because you can't directly write to computed addresses in Hack assembly. Strategy: compute address first, save in temp, then pop to it.

```python
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
            f"@{index}\n"
            "D=A\n"          # D = index
            f"@{pointer}\n"
            "D=M+D\n"        # D = base + index (destination address)
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
```

🎓 **Key insight**: The `R13` temporary register trick is necessary because Hack assembly can't express "write D to the address stored in memory location X" in one instruction. We need to: (1) compute address, (2) save it temporarily, (3) pop value, (4) write value to saved address.

**Testing memory segments**:

Create `examples/basic_test.vm`:
```
// Test basic memory access
push constant 10
pop local 0       // local[0] = 10
push constant 21
push constant 22
pop argument 2    // argument[2] = 22
pop argument 1    // argument[1] = 21
push constant 36
pop this 6        // this[6] = 36
push constant 42
push constant 45
pop that 5        // that[5] = 45
pop that 2        // that[2] = 42
push constant 510
pop temp 6        // temp[6] = 510
push local 0      // Push local[0] (10)
push that 5       // Push that[5] (45)
add               // 10 + 45 = 55
push argument 1   // Push argument[1] (21)
sub               // 55 - 21 = 34
push this 6       // Push this[6] (36)
push this 6       // Push this[6] (36)
add               // 36 + 36 = 72
sub               // 34 - 72 = -38
push temp 6       // Push temp[6] (510)
add               // -38 + 510 = 472
```

Create `examples/pointer_test.vm`:
```
// Test pointer segment (THIS/THAT manipulation)
push constant 3030
pop pointer 0     // THIS = 3030
push constant 3040
pop pointer 1     // THAT = 3040
push constant 32
pop this 2        // RAM[3032] = 32
push constant 46
pop that 6        // RAM[3046] = 46
push pointer 0    // Push THIS (3030)
push pointer 1    // Push THAT (3040)
add               // 3030 + 3040 = 6070
push this 2       // Push RAM[3032] (32)
sub               // 6070 - 32 = 6038
push that 6       // Push RAM[3046] (46)
add               // 6038 + 46 = 6084
```

### Step 4: Handle Static Variables (1 hour)

Static variables need **file-scoped symbols** to avoid conflicts when multiple VM files are translated.

**Problem**: If two VM files both use `static 0`, they'd collide in RAM!

**Solution**: Prefix static variables with filename:
- File `Main.vm`, `static 3` → symbol `Main.3`
- File `Helper.vm`, `static 3` → symbol `Helper.3`

**Update CodeGenerator**:

```python
class CodeGenerator:
    def __init__(self, filename):
        self.label_counter = 0
        self.current_file = filename.replace('.vm', '').split('/')[-1]

    # ... existing methods ...
```

**Update VMTranslator**:

```python
class VMTranslator:
    def __init__(self, input_file):
        self.input_file = input_file
        self.output_file = input_file.replace('.vm', '.asm')
        self.parser = Parser(input_file)

        # Extract filename for static scope
        filename = input_file.split('/')[-1]
        self.code_gen = CodeGenerator(filename)
```

Create `examples/static_test.vm`:
```
// Test static variables
push constant 111
push constant 333
push constant 888
pop static 8      // static[8] = 888
pop static 3      // static[3] = 333
pop static 1      // static[1] = 111
push static 3     // Push 333
push static 1     // Push 111
sub               // 333 - 111 = 222
push static 8     // Push 888
add               // 222 + 888 = 1110
```

### Step 5: Add Bootstrap Code (30 minutes)

Bootstrap code initializes the VM environment before executing the program.

**Initialization requirements**:
- Set SP (stack pointer) to 256
- Other pointers (LCL, ARG, THIS, THAT) will be set by function calls in Project 8

**Update CodeGenerator.init()**:

```python
def init(self):
    """Bootstrap code: initialize VM state"""
    return (
        "// ===== Bootstrap: Initialize VM State =====\n"
        "@256\n"
        "D=A\n"
        "@SP\n"
        "M=D           // SP = 256 (stack starts at RAM[256])\n"
        "\n"
    )
```

**Stack memory layout**:
```
RAM[0-15]:    Pointers (SP, LCL, ARG, THIS, THAT, etc.)
RAM[16-255]:  Static variables
RAM[256-2047]: Stack (grows upward)
RAM[2048+]:   Heap (for objects/arrays)
```

🎓 **Key insight**: Memory layout conventions are **critical** for VM portability. All VM implementations must use the same layout so compiled code works everywhere.

### Step 6: Build Command-Line Interface (30 minutes)

Make your translator usable from the terminal:

```python
# vm_translator.py (add at bottom)
def main():
    """Command-line interface for VM translator"""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python vm_translator.py <file.vm>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not input_file.endswith('.vm'):
        print("Error: Input file must have .vm extension")
        sys.exit(1)

    print(f"Translating {input_file}...")
    translator = VMTranslator(input_file)
    translator.translate()
    print(f"Generated {translator.output_file}")

if __name__ == '__main__':
    main()
```

**Usage**:
```bash
# Translate single file
python vm_translator.py examples/simple_add.vm

# Output: examples/simple_add.asm
```

### Step 7: Write Comprehensive Tests (2-3 hours)

Test each component and the full translator:

```python
# test_vm_translator.py
import unittest
import os
from vm_translator import VMTranslator
from computer_architecture import CPU, Assembler

class TestVMTranslator(unittest.TestCase):
    def setUp(self):
        """Create CPU and assembler for tests"""
        self.cpu = CPU()
        self.asm = Assembler()

    def run_vm_program(self, vm_file, max_cycles=10000):
        """Translate and execute VM program, return CPU state"""
        # Translate VM to assembly
        translator = VMTranslator(vm_file)
        translator.translate()
        asm_file = vm_file.replace('.vm', '.asm')

        # Load and run assembly
        with open(asm_file, 'r') as f:
            lines = f.readlines()

        # Filter out comments and blank lines
        program = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//'):
                program.append(line)

        # Assemble and execute
        binary = self.asm.assemble(program)
        self.cpu.reset()
        self.cpu.load_program(binary)
        self.cpu.run(max_cycles=max_cycles)

        return self.cpu

    def get_stack_contents(self, cpu):
        """Return list of values currently on stack"""
        sp = cpu.ram[0]  # SP is at RAM[0]
        return [cpu.ram[i] for i in range(256, sp)]

    def test_simple_add(self):
        """Test: push 7, push 8, add → result 15"""
        cpu = self.run_vm_program('examples/simple_add.vm')
        stack = self.get_stack_contents(cpu)
        self.assertEqual(stack, [15])

    def test_all_arithmetic(self):
        """Test all arithmetic/logical operations"""
        cpu = self.run_vm_program('examples/stack_test.vm')
        stack = self.get_stack_contents(cpu)

        # Expected results (based on stack_test.vm operations)
        # First compare pairs of 17: eq should give -1 (true)
        # Then 17 vs 16: eq should give 0 (false)
        # ... and so on
        # Final result depends on exact test program
        self.assertIsNotNone(stack)
        self.assertTrue(len(stack) > 0)

    def test_basic_memory(self):
        """Test local, argument, this, that, temp segments"""
        cpu = self.run_vm_program('examples/basic_test.vm')
        stack = self.get_stack_contents(cpu)

        # Final result: 472 (based on basic_test.vm)
        self.assertEqual(stack[-1], 472)

    def test_pointer_segment(self):
        """Test pointer segment (THIS/THAT manipulation)"""
        cpu = self.run_vm_program('examples/pointer_test.vm')
        stack = self.get_stack_contents(cpu)

        # Final result: 6084 (based on pointer_test.vm)
        self.assertEqual(stack[-1], 6084)

        # Verify THIS and THAT were set correctly
        self.assertEqual(cpu.ram[3], 3030)  # THIS
        self.assertEqual(cpu.ram[4], 3040)  # THAT

    def test_static_variables(self):
        """Test static segment (file-scoped globals)"""
        cpu = self.run_vm_program('examples/static_test.vm')
        stack = self.get_stack_contents(cpu)

        # Final result: 1110 (based on static_test.vm)
        self.assertEqual(stack[-1], 1110)

if __name__ == '__main__':
    unittest.main()
```

**Run tests**:
```bash
python -m pytest test_vm_translator.py -v
```

### Step 8: Debugging and Optimization (2-3 hours)

**Common bugs**:

1. **Stack pointer not updated**: Forgetting `SP++` after push or `SP--` before pop
2. **Wrong segment base**: Using wrong pointer (LCL vs ARG vs THIS vs THAT)
3. **Off-by-one in temp**: temp[0] = RAM[5], not RAM[6]!
4. **Label collisions**: Not incrementing label counter in comparisons
5. **Static scope**: Forgetting to prefix static variables with filename

**Debugging strategy**:

```python
# Add debug output to code generator
class CodeGenerator:
    def __init__(self, filename, debug=False):
        self.debug = debug
        # ... existing init ...

    def generate(self, command):
        """Generate assembly with optional debug info"""
        asm = ""

        if self.debug:
            asm += f"// ===== Command: {command} =====\n"

        # ... existing generation logic ...

        if self.debug:
            asm += self.generate_stack_trace()

        return asm

    def generate_stack_trace(self):
        """Generate assembly to print current stack state"""
        return (
            "// [DEBUG] Stack trace:\n"
            "// SP = (current SP value)\n"
            "// Stack top = (value at SP-1)\n"
        )
```

**Performance optimization**:

Your initial implementation prioritizes **correctness and clarity**. After tests pass, you can optimize:

**Optimization 1: Reduce redundant SP loading**
```python
# BEFORE (loads @SP multiple times):
"@SP\n"
"M=M-1\n"
"@SP\n"
"A=M\n"

# AFTER (load once, reuse):
"@SP\n"
"AM=M-1\n"  # Decrement M and set A=M simultaneously
```

**Optimization 2: Inline simple operations**
```python
# BEFORE (separate instructions):
"@SP\n"
"A=M\n"
"M=D\n"

# AFTER (combined):
"@SP\n"
"A=M\n"
"M=D\n"  # Already optimal—Hack has limited instruction combining
```

**Optimization 3: Constant folding** (advanced)
```python
# Detect patterns like:
#   push constant 5
#   push constant 3
#   add
# and emit:
#   push constant 8
# (Only safe if no side effects between operations)
```

🎓 **Key insight**: Optimize **after** achieving correctness. Premature optimization makes debugging harder. Your generated assembly will be ~5x larger than hand-written code, but that's okay—clarity matters more at this stage.

## What You Should Understand After This Project

- ✅ **Virtual machines provide abstraction**: Hide hardware details, enable portability
- ✅ **Stack-based computation**: Natural mapping from expressions to operations
- ✅ **Memory segments**: Logical addressing vs physical RAM locations
- ✅ **Translation patterns**: VM commands → assembly code templates
- ✅ **Bootstrap initialization**: Setting up VM environment before execution
- ✅ **Label management**: Unique labels prevent assembly conflicts
- ✅ **Two-stage compilation**: High-level → VM → Assembly → Machine code
- ✅ **Real-world VMs**: Java JVM, Python bytecode, .NET CLR use similar principles

## Common Pitfalls

**1. Forgetting stack pointer management**
```python
# WRONG (doesn't update SP):
"@SP\n"
"A=M\n"
"M=D\n"  # Push value but don't increment SP!

# RIGHT:
"@SP\n"
"A=M\n"
"M=D\n"
"@SP\n"
"M=M+1\n"  # Now SP points to next free slot
```

**2. Pop sequence errors**
```python
# WRONG (pops before getting value):
"@SP\n"
"M=M-1\n"
"D=M\n"  # D gets value at *new* SP, which is the item we want

# ACTUALLY CORRECT! After SP--, SP points at the item we want to pop.
# The confusion comes from thinking SP points *at* the top item,
# but it actually points to the *next free slot*.
```

**3. Segment index confusion**
```python
# WRONG (adds index to pointer symbol):
f"@LCL+{index}\n"  # Syntax error! Can't do arithmetic in @-address

# RIGHT (compute address in register):
f"@{index}\n"
"D=A\n"
"@LCL\n"
"A=M+D\n"  # A = base + index
```

**4. Temp segment off-by-one**
```python
# WRONG:
address = 6 + index  # temp[0] would be RAM[6]!

# RIGHT:
address = 5 + index  # temp[0] is RAM[5]
```

**5. Comparison label reuse**
```python
# WRONG (same labels for all comparisons):
"@TRUE\n"
"D;JEQ\n"
"@FALSE\n"
# Next comparison will overwrite these labels!

# RIGHT (unique labels):
label_true = f"TRUE_{self.label_counter}"
label_false = f"FALSE_{self.label_counter}"
self.label_counter += 1
```

**6. Not handling inline comments**
```python
# WRONG (parser crashes on inline comments):
line = "push constant 5 // Load five"
parts = line.split()  # ['push', 'constant', '5', '//', 'Load', 'five']
index = int(parts[2])  # Error: int('5') works, but what if comment parsing breaks?

# RIGHT (strip comments first):
line = line.split('//')[0].strip()  # "push constant 5"
parts = line.split()  # ['push', 'constant', '5']
```

## Extension Ideas

**Level 1: Enhance the Translator**
- Add verbose mode that shows VM command → assembly mapping
- Implement assembly optimization (peephole optimization)
- Add error checking (invalid segments, out-of-range indices)
- Generate symbol table for debugging (map VM lines to assembly addresses)

**Level 2: Build Development Tools**
- VM debugger (step through VM commands, inspect stack)
- Stack visualizer (graphical display of stack growth)
- Profiler (track which VM commands are slowest)
- Disassembler (assembly → VM for reverse engineering)

**Level 3: Optimize Generated Code**
- Constant folding (`push 5; push 3; add` → `push 8`)
- Dead code elimination (remove unreachable VM commands)
- Register allocation (use D register more efficiently)
- Instruction scheduling (reorder for fewer RAM accesses)

**Level 4: VM Enhancements**
- Add bitwise shift operations (`shl`, `shr`)
- Add multiplication and division operations
- Implement VM interpreter (execute VM directly without assembly)
- Add profiling hooks (track instruction counts)

**Level 5: Real-World Features**
- Just-In-Time (JIT) compilation (detect hot loops, compile aggressively)
- Garbage collection hooks (track heap allocations)
- Debugging metadata (source line numbers, variable names)
- Multi-threaded VM (concurrent execution)

## Real-World Connection

**Your VM is similar to**:

**Java Virtual Machine (JVM)**:
- Stack-based architecture ✓
- Bytecode intermediate representation ✓
- Platform independence ✓
- Difference: JVM has objects, exceptions, garbage collection

**Python Bytecode**:
- Stack-based operations ✓
- High-level memory abstraction ✓
- Interpreted execution ✓
- Difference: Python is dynamically typed, has runtime eval

**WebAssembly (WASM)**:
- Stack machine ✓
- Portable binary format ✓
- Near-native performance ✓
- Difference: WASM has structured control flow, type system

**LLVM IR**:
- Intermediate representation ✓
- Multiple front-ends → IR → multiple back-ends ✓
- Difference: LLVM uses SSA form (Static Single Assignment), not stack

**Why virtual machines are everywhere**:
1. **Write once, run anywhere**: Java's original promise
2. **Security**: Sandboxed execution environment
3. **Optimization**: JIT compilers optimize hot code paths at runtime
4. **Language interop**: Multiple languages target same VM (JVM has Scala, Kotlin, Clojure)

## Success Criteria

You've mastered this project when you can:

1. **Translate VM to assembly**: Convert any VM program to working assembly code
2. **Explain stack operations**: Describe how push/pop/add work at both VM and assembly levels
3. **Debug translation**: Trace VM command → assembly → execution on hardware
4. **Design new VM commands**: Add operations by defining translation rules
5. **Optimize generated code**: Identify inefficiencies and improve assembly output
6. **Understand memory layout**: Explain segment-to-RAM mapping for all eight segments

## Next Steps

**Project 8: VM Part 2 (Program Flow and Functions)**

You'll extend your translator to support:
- **Program flow**: `label`, `goto`, `if-goto` for loops and conditionals
- **Function calls**: `function`, `call`, `return` for subroutines
- **Stack frames**: Automatic management of local variables and arguments
- **Recursion**: Self-calling functions with proper stack unwinding

This completes the VM, enabling you to compile complex programs with functions, recursion, and arbitrary control flow.

**Project 9-12: The Compiler and OS**

With a complete VM, you'll build:
- **Compiler front-end**: Lexer, parser, syntax tree for high-level language
- **Compiler back-end**: Code generator (high-level → VM)
- **Operating system**: Memory management, I/O, graphics, keyboard, strings

By the end, you'll write programs in a high-level OOP language that compile to VM code, translate to assembly, and run on the computer you built in Phase 1!

---

**Congratulations!** You've entered Phase 2—the software layer. You're now building the abstractions that make programming practical. The stack machine you've built is the foundation for **every high-level language feature** you'll implement next.

The journey from hardware to software is complete when you can type:

```java
class Main {
    function void main() {
        do Output.printString("Hello, World!");
        return;
    }
}
```

And watch it run on your computer, built from NAND gates. You're closer than you think! 🎉
