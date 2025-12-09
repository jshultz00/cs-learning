### Project 6: Assembler - Symbol Resolution and Code Translation
**Objective**: Build a two-pass assembler that translates symbolic assembly to binary machine code

#### Journey So Far: From Hardware to Software Toolchain

You've completed an incredible journey building a complete computer from the ground up. Let's recap what you've accomplished and understand where the assembler fits:

**Phase 1: Hardware Layer (Projects 1-5)**
- **Logic Gates**: Built all Boolean operations from a single NAND primitive
- **ALU**: Created the arithmetic brain capable of 18+ operations
- **Memory**: Designed the storage hierarchy from flip-flops to 32K RAM
- **CPU**: Implemented the fetch-decode-execute cycle that runs programs
- **Complete Computer**: Assembled all components into a working Von Neumann machine

**The Problem We're Solving Now**

In Project 4 and 5, you wrote assembly programs by hand:
```assembly
@5       // A = 5
D=A      // D = 5
@sum     // Error! What is the address of 'sum'?
M=D      // RAM[???] = 5
```

Writing assembly with **symbolic names** (like `sum`, `LOOP`, `counter`) is far more readable than numeric addresses. But your CPU doesn't understand symbols—it only executes binary machine code:

```
0000000000000101  // @5
1110110000010000  // D=A
0000000000010000  // @16 (if 'sum' is at RAM[16])
1110001100001000  // M=D
```

**The assembler is the translator** that converts human-readable symbolic assembly into the binary machine code your CPU executes. This is the bridge between how humans think about programs and how machines execute them.

```
┌─────────────────────────────────────────────────────────┐
│  PHASE 1 → HARDWARE (What you built)                    │
├─────────────────────────────────────────────────────────┤
│  Logic Gates → ALU → Memory → CPU → Computer           │
│  Executes binary machine code (16-bit instructions)     │
└─────────────────────────────────────────────────────────┘
                            ↑
                            │ Binary machine code
                            │
┌─────────────────────────────────────────────────────────┐
│  THIS PROJECT → ASSEMBLER (Software toolchain)          │
├─────────────────────────────────────────────────────────┤
│  Reads: Assembly with symbols (human-readable)          │
│  Outputs: Binary machine code (CPU-executable)          │
│  Process: Two-pass symbol resolution                    │
└─────────────────────────────────────────────────────────┘
                            ↑
                            │ Assembly source code
                            │
┌─────────────────────────────────────────────────────────┐
│  FUTURE PROJECTS → HIGH-LEVEL LANGUAGES                 │
├─────────────────────────────────────────────────────────┤
│  VM Translator (Projects 7-8)                           │
│  Compiler (Projects 10-11)                              │
│  Operating System (Project 12)                          │
└─────────────────────────────────────────────────────────┘
```

#### Background Concepts

**What is an Assembler?**

An assembler is a program that translates assembly language (symbolic, human-readable) into machine code (binary, CPU-executable). It's the lowest-level translator in the software toolchain—every compiler eventually produces assembly that gets assembled into machine code.

Modern compilers (gcc, clang, rustc) all use assemblers as the final step:
```
C/C++/Rust → Compiler → Assembly → Assembler → Machine Code → CPU
```

**Why Build an Assembler?**

1. **Demystify compilation**: See exactly how source code becomes executable binary
2. **Understand symbol resolution**: Learn how labels, variables, and constants are handled
3. **Master two-pass algorithms**: A fundamental pattern in many translation tools
4. **Appreciate abstraction**: Symbols make assembly 10x more readable and maintainable
5. **Foundation for compilers**: The same techniques scale to high-level language compilers

**The Symbol Problem: Why Two Passes?**

Consider this assembly program:
```assembly
    @i          // Line 0: What address is 'i'?
    M=1         // Line 1
    @sum        // Line 2: What address is 'sum'?
    M=0         // Line 3

(LOOP)          // Line 4: Label definition
    @i          // Line 5
    D=M         // Line 6
    @100        // Line 7
    D=D-A       // Line 8
    @END        // Line 9: What address is 'END'? It's defined later!
    D;JGT       // Line 10

    @i          // Line 11
    D=M         // Line 12
    @sum        // Line 13
    M=D+M       // Line 14
    @i          // Line 15
    M=M+1       // Line 16
    @LOOP       // Line 17: Jump back to line 4
    0;JMP       // Line 18

(END)           // Line 19: Label definition
    @END        // Line 20
    0;JMP       // Line 21: Infinite loop (halt)
```

**The challenge**: When you encounter `@END` on line 9, you haven't seen the `(END)` label definition yet (line 19). You can't translate `@END` to a numeric address until you've scanned the entire program to find where labels are defined.

**The solution**: **Two-pass assembly**

**Pass 1**: Scan the entire program to build a **symbol table**
- Record the address of every label: `LOOP → 4`, `END → 19`
- Don't generate any code yet—just collect symbol definitions

**Pass 2**: Translate each instruction to binary
- Look up symbols in the table: `@END` becomes `@19`
- Generate machine code for each instruction
- Assign RAM addresses to variables: `i → 16`, `sum → 17`

This two-pass pattern is fundamental to translation:
- Compilers use it to handle forward references (calling functions defined later)
- Linkers use it to resolve symbols across multiple files
- Virtual machines use it to patch jump addresses

#### The Hack Assembly Language (Full Specification)

You've written basic assembly in Project 4. Now we define the **complete language** the assembler must handle:

**1. A-instructions (Address instructions)**

Three forms exist:

```assembly
@value      // Numeric constant: @100 → load 100 into A register
@symbol     // Variable reference: @sum → load address of 'sum'
@LABEL      // Label reference: @LOOP → load address of label
```

**Translation rules**:
- **Numeric**: `@value` → `0vvvvvvvvvvvvvvv` (15-bit binary value)
- **Symbol**: First occurrence allocates RAM starting at address 16
  - `@sum` (first time) → assigns RAM[16] → `0000000000010000`
  - `@count` (first time) → assigns RAM[17] → `0000000000010001`
  - Subsequent uses reference the same address
- **Label**: Replace with the instruction number where label is defined
  - `(LOOP)` at line 10 → `@LOOP` becomes `@10` → `0000000000001010`

**2. C-instructions (Compute instructions)**

Format: `dest=comp;jump` (both dest and jump are optional)

Valid forms:
```assembly
D=D+1       // dest=comp (no jump)
D;JGT       // comp;jump (no dest, compare D and jump)
M=D+1;JEQ   // dest=comp;jump (all three parts)
0;JMP       // Unconditional jump (dest is null)
D+1         // Just compute (no store, no jump) - rare but valid
```

**Translation**: `111accccccdddjjj` (same as Project 4)
- See Project 4 documentation for complete comp/dest/jump encoding tables

**3. Labels (Pseudo-commands)**

Labels mark positions in the program but don't generate code:

```assembly
(LABEL_NAME)    // Marks this location; next instruction is at this address
```

**Rules**:
- Labels don't consume instruction addresses (they're not executable)
- Label address = instruction number of the **next** instruction
- Can only be referenced (via `@LABEL`), never executed

Example:
```assembly
    @i          // Instruction 0
    M=1         // Instruction 1
(LOOP)          // Not an instruction! Label points to next line
    @i          // Instruction 2 (LOOP → 2)
    D=M         // Instruction 3
```

**4. Comments and Whitespace**

```assembly
// This is a comment
    @sum    // This is an inline comment
    M=D     // Comments after instructions

    // Blank lines are ignored

    @value  // Leading/trailing spaces ignored
```

**Rules**:
- `//` starts a comment (everything after is ignored)
- Blank lines are skipped
- Leading and trailing whitespace is trimmed

**5. Predefined Symbols**

The assembler provides built-in symbols for common registers and memory locations:

**Virtual registers** (RAM addresses 0-15):
```
R0  → RAM[0]
R1  → RAM[1]
R2  → RAM[2]
...
R15 → RAM[15]
```

**Special pointers** (following convention):
```
SP     → RAM[0]   (Stack pointer)
LCL    → RAM[1]   (Local segment base)
ARG    → RAM[2]   (Argument segment base)
THIS   → RAM[3]   (This pointer)
THAT   → RAM[4]   (That pointer)
```

**I/O memory maps** (hardware registers):
```
SCREEN → RAM[16384]  (Memory-mapped screen buffer start)
KBD    → RAM[24576]  (Keyboard memory map)
```

**Usage example**:
```assembly
@SP     // Same as @0
D=M     // D = RAM[0] (stack pointer value)

@R5     // Same as @5
M=D     // RAM[5] = D

@SCREEN // Same as @16384
M=-1    // Set first screen word to all black pixels
```

**6. Symbol Naming Rules**

User-defined symbols (variables and labels) must follow these rules:
- **Characters allowed**: Letters (a-z, A-Z), digits (0-9), underscore (_), dot (.), dollar sign ($), colon (:)
- **Cannot start with**: Digit (0-9)
- **Case-sensitive**: `sum`, `Sum`, `SUM` are three different symbols
- **Cannot conflict**: Don't reuse predefined symbols (R0-R15, SP, LCL, etc.)

**Valid**:
```assembly
@sum
@my_variable
@counter.1
@$temp
@LOOP:START
```

**Invalid**:
```assembly
@123abc     // Starts with digit
@my-var     // Hyphen not allowed
@SP         // Conflicts with predefined symbol (though assembler may allow)
```

#### The Two-Pass Algorithm (Detailed)

**Pass 1: Build Symbol Table**

**Purpose**: Collect all label definitions and assign them instruction addresses

**Algorithm**:
```python
symbol_table = initialize_predefined_symbols()  # R0-R15, SP, SCREEN, etc.
instruction_address = 0

for each line in source_file:
    remove_comments_and_whitespace(line)

    if line is empty:
        continue

    if line is label_definition:  # (LABEL)
        label_name = extract_label_name(line)

        if label_name in symbol_table:
            error("Duplicate label definition")

        symbol_table[label_name] = instruction_address
        # Don't increment instruction_address (labels don't consume addresses)

    else:  # A-instruction or C-instruction
        instruction_address += 1
```

**Key insight**: Labels map to instruction numbers, not RAM addresses. `(LOOP)` might be at instruction 10, meaning ROM[10], not RAM[10].

**Example**:

Input assembly:
```assembly
    @i          // Instruction 0
    M=1         // Instruction 1
(LOOP)          // Label (no instruction)
    @i          // Instruction 2
    D=M         // Instruction 3
(END)           // Label (no instruction)
    @END        // Instruction 4
    0;JMP       // Instruction 5
```

Symbol table after Pass 1:
```python
{
    # Predefined symbols
    'R0': 0, 'R1': 1, ..., 'R15': 15,
    'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
    'SCREEN': 16384, 'KBD': 24576,

    # User-defined labels
    'LOOP': 2,   # Points to instruction 2
    'END': 4     # Points to instruction 4
}
```

**Pass 2: Generate Machine Code**

**Purpose**: Translate each instruction to binary, resolving symbols

**Algorithm**:
```python
next_variable_address = 16  # Variables start at RAM[16]
output_binary = []

for each line in source_file:
    remove_comments_and_whitespace(line)

    if line is empty or line is label:
        continue  # Skip non-instructions

    if line is A_instruction:  # @value or @symbol
        value_or_symbol = line[1:]  # Remove '@'

        if value_or_symbol.isdigit():  # Numeric constant
            address = int(value_or_symbol)

        elif value_or_symbol in symbol_table:  # Known symbol
            address = symbol_table[value_or_symbol]

        else:  # New variable
            symbol_table[value_or_symbol] = next_variable_address
            address = next_variable_address
            next_variable_address += 1

        binary = format_a_instruction(address)  # 0vvvvvvvvvvvvvvv
        output_binary.append(binary)

    elif line is C_instruction:  # dest=comp;jump
        dest, comp, jump = parse_c_instruction(line)
        binary = format_c_instruction(dest, comp, jump)  # 111accccccdddjjj
        output_binary.append(binary)

return output_binary
```

**Key behaviors**:

1. **Variable allocation on first reference**:
   ```assembly
   @sum    // First time: allocate RAM[16], store in symbol table
   M=0     // RAM[16] = 0
   @sum    // Second time: look up in table → 16
   M=M+1   // RAM[16] = RAM[16] + 1
   ```

2. **Label resolution from Pass 1**:
   ```assembly
   @LOOP   // Look up 'LOOP' in symbol table → 2
   0;JMP   // Jump to instruction 2
   ```

3. **Numeric constants pass through**:
   ```assembly
   @100    // No symbol table lookup, just convert 100 → binary
   D=A     // D = 100
   ```

**Complete example**:

Input assembly:
```assembly
    @sum        // Variable (first reference)
    M=0         // Initialize sum
    @i          // Variable (first reference)
    M=1         // Initialize counter
(LOOP)          // Label
    @i
    D=M
    @10
    D=D-A       // Check if i > 10
    @END
    D;JGT       // Exit loop if i > 10
    @i
    D=M
    @sum
    M=D+M       // sum += i
    @i
    M=M+1       // i++
    @LOOP
    0;JMP       // Repeat
(END)
    @END
    0;JMP       // Halt
```

**Pass 1** builds symbol table:
```python
{
    'LOOP': 4,
    'END': 14,
    # (Predefined symbols omitted for brevity)
}
```

**Pass 2** generates binary:
```assembly
@sum        → @16   → 0000000000010000  (new variable at RAM[16])
M=0         →         1110101010001000  (comp=0, dest=M)
@i          → @17   → 0000000000010001  (new variable at RAM[17])
M=1         →         1110111111001000  (comp=1, dest=M)
(LOOP)      →         (skip, not an instruction)
@i          → @17   → 0000000000010001  (lookup variable)
D=M         →         1111110000010000  (comp=M, dest=D)
@10         →         0000000000001010  (numeric constant)
D=D-A       →         1110010011010000  (comp=D-A, dest=D)
@END        → @14   → 0000000000001110  (lookup label)
D;JGT       →         1110001100000001  (comp=D, jump=JGT)
@i          → @17   → 0000000000010001
D=M         →         1111110000010000
@sum        → @16   → 0000000000010000  (lookup variable)
M=D+M       →         1111000010001000  (comp=D+M, dest=M)
@i          → @17   → 0000000000010001
M=M+1       →         1111110111001000  (comp=M+1, dest=M)
@LOOP       → @4    → 0000000000000100  (lookup label)
0;JMP       →         1110101010000111  (comp=0, jump=JMP)
(END)       →         (skip, not an instruction)
@END        → @14   → 0000000000001110
0;JMP       →         1110101010000111
```

🎓 **Why this matters**: The two-pass algorithm is a fundamental pattern in computer science. Compilers use multiple passes to handle complex dependencies. Linkers use passes to combine object files. Understanding this pattern prepares you for building more sophisticated translation tools.

#### Learning Path

**Step 1: Design the Symbol Table** (1 hour)

The symbol table is the core data structure mapping names to addresses.

**What is a Symbol Table?**

A symbol table is a **dictionary (hash map)** that associates symbolic names with numeric addresses. It's one of the most fundamental data structures in all of computer science—used in assemblers, compilers, linkers, debuggers, and even runtime environments.

**Why do we need it?**

Without a symbol table, you'd have to write:
```assembly
@16      // What is at address 16? Who knows!
M=0
@17      // What is at address 17? No idea!
M=1
```

With a symbol table, you can write:
```assembly
@sum     // Ah, sum is our accumulator
M=0
@count   // Ah, count is our loop counter
M=1
```

The assembler maintains the mapping: `sum → 16`, `count → 17`, and automatically translates symbolic references to numeric addresses.

**Three Types of Symbols**

The symbol table manages three distinct categories of symbols:

**1. Virtual Registers (R0-R15)** - General-Purpose RAM Locations

These are **predefined symbols** that provide convenient aliases for the first 16 RAM addresses:

```assembly
@R0      // Same as @0
@R5      // Same as @5
@R15     // Same as @15
```

**Why they exist:**
- **Readability**: `@R5` is more meaningful than `@5` when used as a temporary variable
- **Convention**: Programming conventions often assign specific purposes to these registers
- **Compatibility**: Future projects (VM translator, compiler) will use these as a standard interface

**Common usage patterns:**
```assembly
// Using R13-R15 as temporary variables in a function
@R13
M=D      // Save D in temp register
@R14
M=A      // Save A in temp register
// ... do calculations ...
@R13
D=M      // Restore D
```

🎓 **Real-world connection**: Modern CPUs have actual hardware registers (x86 has RAX, RBX, RCX, etc.; ARM has R0-R15). Our "virtual registers" are actually RAM locations, but they serve a similar purpose for temporary storage.

**2. Special Pointers (SP, LCL, ARG, THIS, THAT)** - VM Translator Interface

These predefined symbols establish a **contract** between the assembler and higher-level software layers you'll build in Projects 7-8:

```assembly
SP   → RAM[0]   // Stack Pointer
LCL  → RAM[1]   // Local segment base pointer
ARG  → RAM[2]   // Argument segment base pointer
THIS → RAM[3]   // This pointer (object base address)
THAT → RAM[4]   // That pointer (array base address)
```

**Why they exist:**
- **Stack-based VM**: Projects 7-8 implement a stack-based virtual machine that needs a stack pointer
- **Function calls**: `LCL` and `ARG` point to the base of local variables and function arguments
- **Memory segments**: `THIS` and `THAT` enable dynamic memory access (arrays, objects)
- **Standard interface**: These symbols create a consistent interface that all software layers understand

**Example usage** (you'll see this in Project 7):
```assembly
// Push constant 17 onto the stack
@17
D=A
@SP       // Stack pointer is at RAM[0]
A=M       // A = address where stack pointer points
M=D       // RAM[stack_top] = 17
@SP
M=M+1     // Increment stack pointer
```

**Why RAM[0-4] specifically?**
- They're at the **beginning of RAM**, making them fast to access
- They're **always in use**, so dedicating prime real estate makes sense
- They create a **zero-overhead abstraction**—no performance cost for using names instead of numbers

🎓 **Real-world connection**: Operating systems use a similar pattern. In x86 assembly, special registers like `ESP` (stack pointer) and `EBP` (base pointer) serve the same role. We're implementing the concept in software using RAM addresses.

**3. I/O Memory Maps (SCREEN, KBD)** - Hardware Interface

These symbols define the **memory-mapped I/O** addresses where hardware devices are accessed:

```assembly
SCREEN → RAM[16384]   // 0x4000 - Start of screen buffer
KBD    → RAM[24576]   // 0x6000 - Keyboard memory-mapped register
```

**Why they exist:**
- **Hardware abstraction**: The screen and keyboard are accessed by reading/writing special RAM addresses
- **No special I/O instructions**: The Hack architecture uses **memory-mapped I/O** instead of dedicated I/O ports
- **Uniform access**: Reading keyboard input looks identical to reading RAM—it's just a different address

**How memory-mapped I/O works:**

The Hack computer has a 512×256 pixel black-and-white screen. Each pixel is one bit, so the entire screen requires:
```
512 × 256 pixels ÷ 16 bits/word = 8,192 words
```

The screen buffer occupies RAM[16384] through RAM[24575]. When you write to these addresses, the pixels change:

```assembly
@SCREEN     // RAM[16384] - first word of screen
M=-1        // Set all 16 pixels to black (binary 1111111111111111)

@SCREEN
D=A
@32         // Move down 32 words (one row)
A=D+A
M=-1        // Draw 16 black pixels on second row
```

The keyboard register (RAM[24576]) is **read-only**. When you read it, you get the ASCII code of the currently pressed key:

```assembly
@KBD        // RAM[24576]
D=M         // D = ASCII code of pressed key (or 0 if none)
@SPACE
D;JEQ       // Jump if spacebar (ASCII 32) is pressed
```

**Why these specific addresses?**
- **SCREEN (16384 = 0x4000)**: Positioned after the first 16K of RAM, leaving room for program variables
- **KBD (24576 = 0x6000)**: Positioned immediately after the 8K screen buffer
- **Clean boundaries**: Using powers of 2 makes address decoding simple in hardware

🎓 **Real-world connection**: Many embedded systems and older computers use memory-mapped I/O. For example:
- **Original IBM PC**: VGA text mode screen buffer at 0xB8000
- **Commodore 64**: Screen memory at 0x0400, color memory at 0xD800
- **Game Boy**: Tile data at 0x8000-0x97FF
- **Modern systems**: Even PCIe devices use memory-mapped configuration spaces

**Implementation strategy**:

```python
class SymbolTable:
    """Manages symbol-to-address mappings"""

    def __init__(self):
        # Initialize with predefined symbols
        self.symbols = {
            # Virtual registers (R0-R15)
            # These are aliases for RAM[0-15], used as general-purpose temp storage
            'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4,
            'R5': 5, 'R6': 6, 'R7': 7, 'R8': 8, 'R9': 9,
            'R10': 10, 'R11': 11, 'R12': 12, 'R13': 13,
            'R14': 14, 'R15': 15,

            # Special pointers (VM interface)
            # These establish the contract with the VM translator (Projects 7-8)
            'SP': 0,     # Stack pointer - points to next free stack slot
            'LCL': 1,    # Local segment base - points to function's local variables
            'ARG': 2,    # Argument segment base - points to function's arguments
            'THIS': 3,   # This pointer - points to current object (heap)
            'THAT': 4,   # That pointer - points to current array (heap)

            # I/O memory-mapped addresses (hardware interface)
            # These define where hardware devices appear in the address space
            'SCREEN': 16384,  # 0x4000 - Start of 512×256 pixel screen buffer (8K words)
            'KBD': 24576      # 0x6000 - Keyboard register (read-only, ASCII code)
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
```

**Test your symbol table**:
```python
st = SymbolTable()

# Test predefined symbols
assert st.get_address('R5') == 5
assert st.get_address('SP') == 0
assert st.get_address('SCREEN') == 16384

# Test label addition
st.add_label('LOOP', 10)
assert st.get_address('LOOP') == 10

# Test variable addition
addr = st.add_variable('sum', 16)
assert addr == 16
assert st.get_address('sum') == 16

print("Symbol table tests passed!")
```

**Step 2: Build the Parser** (2 hours)

The parser reads assembly source and extracts instruction components.

**Implementation**:

```python
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
```

**Test your parser**:
```python
# Create test file
with open('test.asm', 'w') as f:
    f.write("""
    @100
    D=A
    @sum
    M=D
    (LOOP)
    @LOOP
    0;JMP  // Infinite loop
    """)

parser = Parser('test.asm')

# Test parsing
while parser.has_more_lines():
    instruction = parser.current_instruction()

    if not instruction:  # Skip empty lines
        parser.advance()
        continue

    inst_type = parser.instruction_type()

    if inst_type == 'A':
        print(f"A-instruction: @{parser.symbol()}")
    elif inst_type == 'C':
        print(f"C-instruction: dest={parser.dest()}, comp={parser.comp()}, jump={parser.jump()}")
    elif inst_type == 'L':
        print(f"Label: ({parser.symbol()})")

    parser.advance()
```

Expected output:
```
A-instruction: @100
C-instruction: dest=D, comp=A, jump=
A-instruction: @sum
C-instruction: dest=M, comp=D, jump=
Label: (LOOP)
A-instruction: @LOOP
C-instruction: dest=, comp=0, jump=JMP
```

**Step 3: Build the Code Generator** (2 hours)

The code generator translates parsed instructions to binary.

**Implementation**:

```python
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
```

**Test your code generator**:
```python
cg = CodeGenerator()

# Test A-instructions
assert cg.generate_a_instruction(0) == '0000000000000000'
assert cg.generate_a_instruction(100) == '0000000001100100'
assert cg.generate_a_instruction(16384) == '0100000000000000'

# Test C-instructions
assert cg.generate_c_instruction('D', 'A', '') == '1110110000010000'  # D=A
assert cg.generate_c_instruction('M', 'D', '') == '1110001100001000'  # M=D
assert cg.generate_c_instruction('', 'D', 'JGT') == '1110001100000001'  # D;JGT
assert cg.generate_c_instruction('', '0', 'JMP') == '1110101010000111'  # 0;JMP

print("Code generator tests passed!")
```

**Step 4: Implement the Assembler (Two-Pass Algorithm)** (3-4 hours)

Now combine all components into the complete two-pass assembler.

**Implementation**:

```python
class Assembler:
    """Full two-pass assembler"""

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.code_gen = CodeGenerator()

    def assemble(self, input_filename, output_filename):
        """Assemble .asm file to .hack binary file"""

        # Pass 1: Build symbol table with labels
        self._first_pass(input_filename)

        # Pass 2: Generate machine code
        binary_code = self._second_pass(input_filename)

        # Write output
        with open(output_filename, 'w') as f:
            for instruction in binary_code:
                f.write(instruction + '\n')

        return binary_code

    def _first_pass(self, filename):
        """Pass 1: Collect label definitions"""
        parser = Parser(filename)
        instruction_address = 0

        while parser.has_more_lines():
            instruction = parser.current_instruction()

            if not instruction:  # Empty line
                parser.advance()
                continue

            inst_type = parser.instruction_type()

            if inst_type == 'L':  # Label definition
                label = parser.symbol()
                self.symbol_table.add_label(label, instruction_address)
                # Don't increment address (labels don't generate code)

            else:  # A or C instruction
                instruction_address += 1

            parser.advance()

    def _second_pass(self, filename):
        """Pass 2: Generate machine code"""
        parser = Parser(filename)
        binary_code = []
        next_variable_address = 16  # Variables start at RAM[16]

        while parser.has_more_lines():
            instruction = parser.current_instruction()

            if not instruction:  # Empty line
                parser.advance()
                continue

            inst_type = parser.instruction_type()

            if inst_type == 'A':
                symbol = parser.symbol()

                # Check if numeric constant
                if symbol.isdigit():
                    address = int(symbol)

                # Check if existing symbol
                elif self.symbol_table.contains(symbol):
                    address = self.symbol_table.get_address(symbol)

                # New variable - allocate address
                else:
                    address = self.symbol_table.add_variable(symbol, next_variable_address)
                    next_variable_address += 1

                binary = self.code_gen.generate_a_instruction(address)
                binary_code.append(binary)

            elif inst_type == 'C':
                dest = parser.dest()
                comp = parser.comp()
                jump = parser.jump()

                binary = self.code_gen.generate_c_instruction(dest, comp, jump)
                binary_code.append(binary)

            # Skip labels (already processed in first pass)

            parser.advance()

        return binary_code
```

**Test the complete assembler**:

Create `sum.asm`:
```assembly
// Computes sum = 1 + 2 + ... + 10
    @sum
    M=0         // sum = 0
    @i
    M=1         // i = 1
(LOOP)
    @i
    D=M         // D = i
    @10
    D=D-A       // D = i - 10
    @END
    D;JGT       // if (i - 10) > 0 goto END
    @i
    D=M
    @sum
    M=D+M       // sum += i
    @i
    M=M+1       // i++
    @LOOP
    0;JMP       // goto LOOP
(END)
    @END
    0;JMP       // infinite loop
```

Run assembler:
```python
assembler = Assembler()
binary = assembler.assemble('sum.asm', 'sum.hack')

# Print results
for i, instruction in enumerate(binary):
    print(f"{i:03d}: {instruction}")
```

Expected output (`sum.hack`):
```
000: 0000000000010000  // @16 (sum)
001: 1110101010001000  // M=0
002: 0000000000010001  // @17 (i)
003: 1110111111001000  // M=1
004: 0000000000010001  // @17 (i)
005: 1111110000010000  // D=M
006: 0000000000001010  // @10
007: 1110010011010000  // D=D-A
008: 0000000000001010  // @10 (END label)
009: 1110001100000001  // D;JGT
010: 0000000000010001  // @17 (i)
011: 1111110000010000  // D=M
012: 0000000000010000  // @16 (sum)
013: 1111000010001000  // M=D+M
014: 0000000000010001  // @17 (i)
015: 1111110111001000  // M=M+1
016: 0000000000000100  // @4 (LOOP label)
017: 1110101010000111  // 0;JMP
018: 0000000000001010  // @10 (END)
019: 1110101010000111  // 0;JMP
```

**Step 5: Add Error Handling and Debugging** (2 hours)

Production assemblers provide helpful error messages.

**Enhanced assembler with error reporting**:

```python
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
```

**Test error handling**:

```python
# Test invalid label
with open('test_error.asm', 'w') as f:
    f.write("""
    @sum
    M=0
(LOOP)
    @LOOP
    0;JMP
(LOOP)  // Duplicate label!
    @END
    0;JMP
    """)

assembler = Assembler()
try:
    assembler.assemble('test_error.asm', 'test.hack', debug=True)
except AssemblerError as e:
    print(f"Expected error caught: {e}")
```

**Step 6: Build Real-World Programs** (3-4 hours)

Test your assembler with progressively complex programs.

**Program 1: Array maximum**

Find the largest value in an array:

```assembly
// Finds max value in array of 10 numbers
// Array starts at RAM[100]
// Result stored in RAM[50]

    @100        // Array base address
    D=A
    @arr
    M=D         // arr = 100

    @10         // Array length
    D=A
    @n
    M=D         // n = 10

    @arr
    A=M
    D=M
    @max
    M=D         // max = arr[0]

    @i
    M=1         // i = 1

(LOOP)
    @i
    D=M
    @n
    D=D-M
    @END
    D;JGE       // if i >= n goto END

    @arr
    D=M
    @i
    A=D+M       // A = arr + i
    D=M         // D = arr[i]

    @max
    D=D-M       // D = arr[i] - max
    @SKIP
    D;JLE       // if arr[i] <= max goto SKIP

    @arr
    D=M
    @i
    A=D+M
    D=M
    @max
    M=D         // max = arr[i]

(SKIP)
    @i
    M=M+1       // i++
    @LOOP
    0;JMP

(END)
    @max
    D=M
    @50
    M=D         // RAM[50] = max

    @END
    0;JMP
```

🎓 **Key lesson**: Array indexing requires address arithmetic (`arr + i`). The A register holds the computed address.

**Program 2: String comparison**

Compare two null-terminated strings:

```assembly
// Compare strings at RAM[100] and RAM[200]
// Result: RAM[50] = -1 (str1 < str2), 0 (equal), 1 (str1 > str2)

    @100
    D=A
    @str1
    M=D         // str1 = 100

    @200
    D=A
    @str2
    M=D         // str2 = 200

    @i
    M=0         // i = 0

(LOOP)
    @str1
    D=M
    @i
    A=D+M
    D=M
    @char1
    M=D         // char1 = str1[i]

    @str2
    D=M
    @i
    A=D+M
    D=M
    @char2
    M=D         // char2 = str2[i]

    @char1
    D=M
    @LESS
    D;JEQ       // if char1 == 0, str1 ended first

    @char2
    D=M
    @GREATER
    D;JEQ       // if char2 == 0, str2 ended first

    @char1
    D=M
    @char2
    D=D-M       // D = char1 - char2
    @LESS
    D;JLT       // if char1 < char2
    @GREATER
    D;JGT       // if char1 > char2

    @i
    M=M+1       // i++
    @LOOP
    0;JMP

(LESS)
    @50
    M=-1        // result = -1
    @END
    0;JMP

(GREATER)
    @50
    M=1         // result = 1
    @END
    0;JMP

(EQUAL)
    @50
    M=0         // result = 0

(END)
    @END
    0;JMP
```

**Step 7: Create an Assembler Driver Script** (1 hour)

Make a command-line interface for your assembler:

```python
#!/usr/bin/env python3
"""
Hack Assembler - Command-line driver
Usage: ./assembler.py input.asm [output.hack] [--debug]
"""

import sys
from assembler import Assembler

def main():
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: assembler.py input.asm [output.hack] [--debug]")
        sys.exit(1)

    input_file = sys.argv[1]

    # Default output filename
    output_file = input_file.replace('.asm', '.hack')

    # Check for custom output filename
    debug = False
    if len(sys.argv) >= 3:
        if sys.argv[2] == '--debug':
            debug = True
        else:
            output_file = sys.argv[2]

    if len(sys.argv) >= 4 and sys.argv[3] == '--debug':
        debug = True

    # Assemble
    print(f"Assembling {input_file}...")

    assembler = Assembler()
    try:
        assembler.assemble(input_file, output_file, debug=debug)
        print(f"Output written to {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

**Usage**:
```bash
# Make executable
chmod +x assembler.py

# Assemble a program
./assembler.py sum.asm

# Custom output file
./assembler.py sum.asm output.hack

# Debug mode
./assembler.py sum.asm --debug
```

#### What You Should Understand After This Project

- ✅ **Two-pass algorithms**: Why forward references require multiple passes
- ✅ **Symbol tables**: How names map to addresses (the foundation of all high-level languages)
- ✅ **Lexical analysis**: Parsing text into structured tokens
- ✅ **Code generation**: Translating symbolic instructions to binary
- ✅ **Variable allocation**: How compilers assign memory addresses
- ✅ **Label resolution**: How jumps work without hardcoded addresses
- ✅ **Error handling**: Providing useful diagnostics for invalid input
- ✅ **Separation of concerns**: Parser, symbol table, code generator as independent modules

#### Common Pitfalls

**1. Forgetting labels don't consume addresses**
```assembly
    @i          // Instruction 0
    M=1         // Instruction 1
(LOOP)          // NOT instruction 2!
    @i          // Instruction 2 (LOOP points here)
```

**2. Variable vs label confusion**
```assembly
@LOOP   // Label reference → instruction address
@sum    // Variable reference → RAM address
```
Labels point to ROM (instructions), variables point to RAM (data).

**3. Off-by-one in symbol allocation**
```python
# WRONG: Allocates same address twice
address = 16
symbol_table['sum'] = address
symbol_table['i'] = address  # BUG!

# RIGHT: Increment after each allocation
next_address = 16
symbol_table['sum'] = next_address
next_address += 1
symbol_table['i'] = next_address
next_address += 1
```

**4. Not handling whitespace variations**
```assembly
D=M+1       // No spaces
D = M + 1   // Spaces around operators
D=  M+1     // Irregular spacing
```
Your parser must strip whitespace consistently.

**5. Predefined symbol conflicts**
```assembly
@R5         // Predefined: RAM[5]
@SP         // Predefined: RAM[0]
@SCREEN     // Predefined: RAM[16384]
```
Don't allow users to redefine these.

**6. Invalid symbol names**
```assembly
@123var     // Invalid: starts with digit
@my-var     // Invalid: hyphen not allowed
@_temp      // Valid
@var.1      // Valid
```

#### Extension Ideas

**1. Macro support**
```assembly
// Define macro
$MACRO PUSH
    @SP
    A=M
    M=D
    @SP
    M=M+1
$END

// Use macro
    @value
    D=M
    PUSH    // Expands to macro body
```

**2. Disassembler**

Reverse the process—convert binary to assembly:
```python
def disassemble(binary_file):
    with open(binary_file, 'r') as f:
        for line in f:
            instruction = int(line.strip(), 2)

            if instruction & 0x8000:  # C-instruction
                print(decode_c_instruction(instruction))
            else:  # A-instruction
                value = instruction & 0x7FFF
                print(f"@{value}")
```

**3. Optimization pass**

Detect and eliminate redundant instructions:
```assembly
// Before optimization
@5
D=A
@5      // Redundant! A already = 5
M=D

// After optimization
@5
D=A
M=D     // Removed redundant @5
```

**4. Listing file generation**

Create annotated output showing source and binary side-by-side:
```
Address | Binary           | Source
--------|------------------|------------------
000     | 0000000000010000 | @sum
001     | 1110101010001000 | M=0
002     | 0000000000010001 | @i
003     | 1110111111001000 | M=1
004     | 0000000000010001 | (LOOP) @i
```

**5. Symbol cross-reference table**

Show where each symbol is defined and used:
```
Symbol | Type     | Address | Defined | Used
-------|----------|---------|---------|------------------
sum    | Variable | 16      | Line 1  | Lines 1, 3, 12
LOOP   | Label    | 4       | Line 4  | Lines 17
i      | Variable | 17      | Line 2  | Lines 2, 5, 11, 15
```

**6. Include directive**

Support splitting large programs across files:
```assembly
// main.asm
#include "macros.asm"
#include "functions.asm"

    @main
    0;JMP
```

**7. Expression evaluation in constants**

Allow arithmetic in A-instructions:
```assembly
@SCREEN+100     // Evaluate to 16384+100 = 16484
@R5+10          // Evaluate to 5+10 = 15
```

**8. Conditional assembly**

Compile different code based on flags:
```assembly
#define DEBUG 1

#if DEBUG
    @debug_output
    M=D
#endif
```

#### Real-World Connection

**Modern assemblers** (like GAS, NASM, MASM) use the same principles:

**Two-pass assembly**:
- GAS (GNU Assembler) for x86/ARM uses multiple passes
- First pass collects symbol definitions
- Subsequent passes resolve references and optimize

**Symbol tables**:
- Linkers combine symbol tables from multiple object files
- Debuggers use symbol tables to map addresses to variable names
- Profilers use symbol tables to attribute performance to functions

**Macro expansion**:
- Most assemblers support sophisticated macro systems
- C preprocessor is essentially a macro assembler for text

**Error reporting**:
- Professional assemblers provide line numbers, column numbers, and context
- Some highlight the exact error position in color

**Optimization**:
- Assemblers can perform peephole optimization (replacing instruction sequences)
- Some reorder instructions to avoid pipeline stalls

**Output formats**:
- Assemblers generate object files (.o, .obj) with relocatable code
- Linkers combine object files into executables (.exe, .elf)

**x86 assembler example**:
```nasm
section .data
    message db 'Hello, World!', 0

section .text
    global _start

_start:
    mov eax, 4          ; sys_write
    mov ebx, 1          ; stdout
    mov ecx, message    ; buffer
    mov edx, 13         ; length
    int 0x80            ; syscall

    mov eax, 1          ; sys_exit
    xor ebx, ebx        ; status 0
    int 0x80
```

The principles are identical to your Hack assembler:
- Symbols (`message`, `_start`)
- Labels (section markers)
- Instruction encoding (though far more complex)
- Two-pass resolution

#### Testing Your Assembler

**Test suite**:

```python
import unittest
from assembler import Assembler
import os

class TestAssembler(unittest.TestCase):
    def setUp(self):
        self.assembler = Assembler()

    def test_predefined_symbols(self):
        """Test predefined symbol resolution"""
        with open('test.asm', 'w') as f:
            f.write("@R5\nD=A\n@SP\nM=D")

        binary = self.assembler.assemble('test.asm', 'test.hack')

        self.assertEqual(binary[0], '0000000000000101')  # @5
        self.assertEqual(binary[2], '0000000000000000')  # @0

    def test_label_resolution(self):
        """Test forward and backward label references"""
        with open('test.asm', 'w') as f:
            f.write("@END\n0;JMP\n(END)\n@END\n0;JMP")

        binary = self.assembler.assemble('test.asm', 'test.hack')

        # Both @END should resolve to instruction 2
        self.assertEqual(binary[0], '0000000000000010')
        self.assertEqual(binary[2], '0000000000000010')

    def test_variable_allocation(self):
        """Test variable allocation starting at RAM[16]"""
        with open('test.asm', 'w') as f:
            f.write("@sum\nM=0\n@count\nM=0")

        binary = self.assembler.assemble('test.asm', 'test.hack')

        self.assertEqual(binary[0], '0000000000010000')  # sum → 16
        self.assertEqual(binary[2], '0000000000010001')  # count → 17

    def test_duplicate_label_error(self):
        """Test error on duplicate label"""
        with open('test.asm', 'w') as f:
            f.write("(LOOP)\n@LOOP\n0;JMP\n(LOOP)\n@END\n0;JMP")

        with self.assertRaises(Exception):
            self.assembler.assemble('test.asm', 'test.hack')

    def test_comments_and_whitespace(self):
        """Test comment and whitespace handling"""
        with open('test.asm', 'w') as f:
            f.write("""
            // This is a comment
            @sum    // Initialize sum
            M=0

                @i  // Leading spaces
            M=1     // Another comment
            """)

        binary = self.assembler.assemble('test.asm', 'test.hack')

        self.assertEqual(len(binary), 4)  # Only 4 instructions

    def tearDown(self):
        # Clean up test files
        for f in ['test.asm', 'test.hack']:
            if os.path.exists(f):
                os.remove(f)

if __name__ == '__main__':
    unittest.main()
```

Run tests:
```bash
python3 test_assembler.py
```

#### Integration with Your CPU (Project 5)

Your assembler now produces binary code that your CPU from Project 5 can execute!

**Complete workflow**:

```python
# Import your CPU from Project 5
import sys
sys.path.append('../05_computer_architecture')
from computer_architecture import CPU

# Import your assembler from Project 6
from assembler import Assembler

# Write assembly program
with open('program.asm', 'w') as f:
    f.write("""
    @5
    D=A
    @10
    D=D+A
    @0
    M=D
    @6
    0;JMP
    """)

# Assemble to binary
assembler = Assembler()
binary = assembler.assemble('program.asm', 'program.hack')

# Load into CPU
cpu = CPU()
cpu.load_program(binary)

# Execute
cpu.run(max_cycles=10)

# Check result
print(f"RAM[0] = {cpu.RAM[0]}")  # Should be 15 (5 + 10)
```

🎓 **You've now closed the loop**: You can write assembly, assemble it to binary, and execute it on the CPU you built. This is a complete computer system from gates to running programs!

#### Next Steps

**Project 7-8: Virtual Machine Translator**

The assembler translates symbolic assembly to binary. The VM translator will translate an even higher-level language (stack-based VM code) to assembly. You'll build:

- Stack operations (push, pop)
- Arithmetic operations (add, sub, mul)
- Control flow (if-goto, goto)
- Function calls (call, return)

**Project 10-11: Compiler**

The compiler translates a high-level language (Jack, similar to Java) to VM code. You'll build:

- Lexical analyzer (tokenizer)
- Parser (syntax analysis)
- Code generator (VM code emission)

**Project 12: Operating System**

Implement OS services in Jack:
- Memory management (malloc, free)
- String operations
- I/O (keyboard, screen)
- Math library (multiply, divide, sqrt)

**The Full Software Stack**:
```
Jack program → Compiler → VM code → VM Translator → Assembly → Assembler → Binary → CPU
```

Every layer builds on the previous, and you'll have built every translator in the chain!

---

**Congratulations!** You've built a complete assembler—a real software development tool. This is the foundation of all modern compilation. Every time you compile a C program, write Rust code, or build a Python extension, an assembler like the one you just built is working behind the scenes to generate executable machine code.
