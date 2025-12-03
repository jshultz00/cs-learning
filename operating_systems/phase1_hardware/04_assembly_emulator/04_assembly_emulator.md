### Project 4: Assembly Language Emulator
**Objective**: Understand machine language and low-level programming

#### Journey So Far: Building a Computer from First Principles

Before diving into assembly language, let's connect the dots from everything you've built in the previous projects. You've been constructing a computer layer by layer, from the physical circuits up to the software abstraction:

**Project 1: Logic Gates** - You started with the most fundamental building blocks:
- Built AND, OR, NOT, NAND gates from first principles
- Learned that all computation reduces to manipulating binary signals (0s and 1s)
- Created the foundation: every circuit in a computer is built from these basic gates

**Project 2: ALU (Arithmetic Logic Unit)** - You constructed the "brain" that performs calculations:
- Combined logic gates into adders (half-adder → full-adder → 16-bit adder)
- Built the ALU that can perform 18 different operations (add, subtract, AND, OR, NOT, etc.)
- Realized this is the same ALU component we'll use in this project's CPU

**Project 3: Memory & Registers** - You created the computer's "working memory":
- Built flip-flops and latches to store state (the foundation of all memory)
- Created registers (1-bit → 16-bit) that hold values between clock cycles
- Designed RAM using address decoders to access thousands of memory locations
- Learned about the **memory hierarchy**: registers → L1 cache → L2 cache → L3 cache → RAM → SSD → HDD
- Understood **cache architecture**: direct-mapped, fully associative, and set-associative caches
- Explored **locality principles**: temporal (access data again soon) and spatial (access nearby data)
- These are the exact **A, D, and RAM** components we'll simulate in this emulator

**The Memory Hierarchy Bridge**

In Project 3, you learned that modern computers don't just have "memory"—they have a **memory hierarchy** optimized for speed and capacity:

```
CPU Registers (A, D)  ← ~1 ns    ← What you'll program in assembly
     ↓
L1 Cache              ← ~2 ns    ← Hardware automatically manages
     ↓
L2 Cache              ← ~10 ns
     ↓
L3 Cache              ← ~20 ns
     ↓
Main RAM (M)          ← ~100 ns  ← What you'll access via @address
     ↓
SSD/Disk              ← ~100 µs
```

When you write assembly code like `D=M` (load from memory), the hardware automatically checks the cache hierarchy before going to main RAM. **This is invisible to the programmer**—your assembly code works the same whether caches exist or not, but caches make it 10-100x faster!

Key insights connecting to assembly programming:
- **Registers (A, D) are fastest**: Keep frequently-used values in registers, not memory
- **Memory access is slow**: Minimize `M=...` and `D=M` operations
- **Locality matters**: Access memory sequentially when possible (arrays, loops)
- **Cache-friendly code**: Sequential memory access (addresses 100, 101, 102...) is much faster than random access (100, 5000, 200, 8000...) due to **cache lines** loading 64 bytes at once

Example of cache-aware assembly:
```assembly
// BAD: Random access pattern (cache unfriendly)
@100
D=M      // Cache miss - loads addresses 64-127
@5000
D=M      // Cache miss - loads addresses 4992-5055
@200
D=M      // Cache miss - loads addresses 192-255

// GOOD: Sequential access pattern (cache friendly)
@100
D=M      // Cache miss - loads addresses 64-127
@101
D=M      // Cache HIT! (already loaded in line)
@102
D=M      // Cache HIT! (already loaded in line)
```

This hierarchy explains why seemingly identical programs can have wildly different performance based on their memory access patterns—a concept you'll encounter when optimizing real-world code.

**Now: Tying It All Together**

In the previous projects, you built the **hardware components**. Now you're moving to the **instruction layer** - the interface between hardware and software. This is where those physical circuits become a programmable computer.

Here's how everything connects:

```
┌─────────────────────────────────────────────────────────┐
│  PREVIOUS PROJECTS → HARDWARE COMPONENTS                │
├─────────────────────────────────────────────────────────┤
│  Logic Gates (P1)  →  Foundation for all circuits       │
│  ALU (P2)          →  Performs computations (comp bits) │
│  Registers (P3)    →  A and D registers we'll use       │
│  RAM (P3)          →  M (memory) accessed via A         │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  THIS PROJECT → INSTRUCTION SET ARCHITECTURE (ISA)      │
├─────────────────────────────────────────────────────────┤
│  Assembly Language →  Human-readable instructions       │
│  Machine Code      →  Binary patterns the hardware reads│
│  Assembler         →  Translator (assembly → binary)    │
│  Emulator/CPU      →  Executes the binary instructions  │
└─────────────────────────────────────────────────────────┘
```

**The Missing Link: How Does Hardware Execute Instructions?**

You've built an ALU that can add, subtract, and perform logic operations. But how does it "know" which operation to perform? That's what **instructions** do - they're control signals encoded as bit patterns.

When you write `D=D+1` in assembly:
1. **Assembler** converts it to binary: `1110011111010000`
2. **CPU** decodes this bit pattern:
   - Bits 0-2 (jump): `000` = no jump
   - Bits 3-5 (dest): `010` = store in D register
   - Bits 6-11 (comp): `011111` = D+1 operation
   - Bit 12 (a): `0` = use A register (not used here)
   - Bits 13-15: `111` = C-instruction marker
3. **ALU** (from Project 2) performs the D+1 operation
4. **D Register** (from Project 3) stores the result
5. **Program Counter** increments to fetch the next instruction

Every component you built is being orchestrated by these instruction bits!

#### Background Concepts

Assembly language is the human-readable form of machine code. Each instruction is a pattern of bits that tells the CPU what to do. This project teaches you how instructions are encoded and executed by building a complete toolchain from scratch—an assembler that translates human-readable assembly to binary machine code, and an emulator that executes that binary code instruction by instruction.

**The Bridge Between Hardware and Software**

In Projects 1-3, you built the hardware. Now you're building the software layer that **controls** that hardware. The instruction set is the contract:
- Hardware designers (you in Projects 1-3) implement the circuits
- Software developers (you in this project) write programs that control those circuits
- The ISA (Instruction Set Architecture) is the specification both sides agree on

**Why Build an Emulator?**

When you write high-level code in Python, JavaScript, or C++, layers of abstraction hide what's actually happening. The compiler translates your code into assembly, the assembler converts that to machine code, and the CPU executes those binary instructions. By building this entire pipeline yourself, you'll:

1. **Demystify the compilation process**: See exactly how source code becomes executable instructions
2. **Understand the hardware/software boundary**: Learn what the CPU actually does vs. what the operating system provides
3. **Build machine-level intuition**: Recognize patterns that help you write better high-level code
4. **Prepare for systems programming**: Assembly knowledge is essential for OS development, embedded systems, reverse engineering, and performance optimization

**The Instruction Set Architecture (ISA)**

Think of the ISA as the "contract" between hardware and software. It's the specification that defines:
- **What instructions exist** (add, load, jump, etc.)
- **How they're encoded** (which bits mean what)
- **What registers are available** (temporary storage locations)
- **How memory is accessed** (addressing modes)
- **What data types are supported** (integers, floats, etc.)

The ISA is the boundary layer: hardware designers implement it in silicon, and software developers target it with compilers. Famous ISAs include x86 (Intel/AMD), ARM (phones/tablets), RISC-V (open source), and MIPS (educational). Each has different design philosophies trading off complexity, power efficiency, and performance.

**Our Simplified ISA: The Hack Architecture**

We'll build a simplified ISA inspired by the Hack computer (from the excellent "Nand to Tetris" course), which uses only **two instruction types**. This minimalism isn't just for learning—it reveals that all computation can be expressed with surprisingly simple primitives.

**A-instruction** (Address instruction):
```
Format: @value
Binary: 0vvvvvvvvvvvvvvv (0 followed by 15-bit value)
Effect: Sets A register to value
Purpose: Load constants or set memory addresses
```

The A-instruction is your "setup" instruction. It loads a value into the A register, which serves two purposes:
1. **As a constant**: You can immediately use this value in calculations
2. **As an address**: The A register tells the CPU which RAM location to access

Example usage:
```assembly
@100     // A = 100 (prepare to access RAM[100])
D=M      // D = RAM[100] (read from that address)
@5       // A = 5 (load constant 5)
D=D+A    // D = D + 5 (add the constant)
```

**C-instruction** (Compute instruction):
```
Format: dest=comp;jump
Binary: 111accccccdddjjj
- 111: Instruction type marker (distinguishes from A-instruction)
- a: Use A register (0) or M[A] memory (1) as second operand
- cccccc: Which computation (add, sub, and, or, not, etc.)
- ddd: Destination register(s) to store result
- jjj: Jump condition (conditional or unconditional control flow)
```

The C-instruction is the workhorse. In a single 16-bit instruction, it can:
- **Compute** a value using the ALU (Arithmetic Logic Unit)
- **Store** that result in registers (A, D) and/or memory (M)
- **Jump** to a different instruction based on the result

Example power: `D=D+1;JGT` (increment D, jump if positive) accomplishes three operations in one instruction:
1. Computation: D + 1
2. Destination: Store result in D
3. Jump: If result > 0, jump to address in A

🎓 **Why only two instruction types?**

This design follows **RISC principles** (Reduced Instruction Set Computing):
- **Simplicity**: Fewer instruction types means simpler hardware decoding
- **Flexibility**: The C-instruction is extremely versatile—one format handles arithmetic, logic, memory access, and control flow
- **Regularity**: All instructions are 16 bits, simplifying instruction fetch
- **Clarity**: The separation between "load address" (A) and "compute" (C) makes programs explicit about what they're doing

Real processors use more instruction types for efficiency, but this minimal set proves that any computation can be expressed with just load-address and compute-store-jump primitives.

#### Learning Path

**Step 1: Design Your Instruction Format** (1-2 hours)

Before writing any code, you need to deeply understand the instruction encoding. This step is like learning the "vocabulary" of your machine—every assembly instruction must map to exactly one 16-bit binary pattern.

**The Three-Part Encoding Challenge**

A C-instruction packs three independent operations into 16 bits:
```
111 a cccccc ddd jjj
│   │ │      │   └─ Jump condition (3 bits = 8 possibilities)
│   │ │      └───── Destination(s) (3 bits = 8 combinations)
│   │ └──────────── Computation (6 bits = 64 operations, we use ~18)
│   └────────────── A or Memory selector
└────────────────── Instruction type marker (111 = C-instruction)
```

Each field is independent, so you can mix and match: any computation can go to any destination with any jump. This orthogonality gives you 18 × 8 × 8 = **1,152 possible instructions** from one simple format.

**Computation codes (cccccc bits)**

The 6-bit computation field tells the ALU what operation to perform. The `a` bit determines whether the second operand is the A register (a=0) or RAM[A] (a=1):

```
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
```

🎓 **Understanding the `a` bit**: This single bit doubles your instruction set. When a=0, you compute with the A register (fast, no memory access). When a=1, the CPU fetches RAM[A] before computing (slower, but accesses variables/arrays).

**Key insight**: Notice that some operations (like `0`, `1`, `-1`, `D`) ignore the `a` bit because they don't use the second operand. Others (like `A` vs `M`) fundamentally change meaning based on `a`. This is the difference between `D=A` (copy register) and `D=M` (load from memory).

**Destination codes (ddd bits)**

The 3 destination bits form a bitmap where each bit controls one storage location:

```
Mnemonic | A | D | M | Binary | Behavior
---------|---|---|---|--------|----------------------------------
null     | 0 | 0 | 0 | 000    | Compute but discard result (side effects: sets flags for jump)
M        | 0 | 0 | 1 | 001    | Store to RAM[A] only
D        | 0 | 1 | 0 | 010    | Store to D register only
MD       | 0 | 1 | 1 | 011    | Store to both D and RAM[A]
A        | 1 | 0 | 0 | 100    | Store to A register only
AM       | 1 | 0 | 1 | 101    | Store to both A and RAM[A]
AD       | 1 | 1 | 0 | 110    | Store to both A and D
AMD      | 1 | 1 | 1 | 111    | Store to all three locations
```

🎓 **Bitmap encoding**: Each bit position corresponds to a destination:
- Bit 2 (0x4): Store in A register
- Bit 1 (0x2): Store in D register
- Bit 0 (0x1): Store in RAM[A]

This means `dest_bits & 0x4` tests "should we write to A?" in your emulator. The hardware likely uses the same bit as a write-enable signal for each storage unit.

**Example usage patterns**:
- `D=D+1` (dest=010): Increment in-place, common for counters
- `MD=D+1` (dest=011): Increment D and save to memory simultaneously
- `null=D-1;JEQ` (dest=000): Compute for comparison only, don't store

**Jump codes (jjj bits)**

The 3 jump bits determine whether to jump based on the computation result. The CPU evaluates conditions on the **computed value** (before storing to destination):

```
Mnemonic | Condition      | Binary | When to use
---------|----------------|--------|----------------------------------
null     | no jump        | 000    | Sequential execution (default)
JGT      | if out > 0     | 001    | Positive number checks
JEQ      | if out == 0    | 010    | Equality tests, loop termination
JGE      | if out >= 0    | 011    | Non-negative checks
JLT      | if out < 0     | 100    | Negative number checks
JNE      | if out != 0    | 101    | "Not done yet" checks
JLE      | if out <= 0    | 110    | Non-positive checks
JMP      | unconditional  | 111    | Infinite loops, goto
```

🎓 **Bitmap encoding (again!)**: The jump bits form a condition table:
- Bit 2 (0x4): Jump if result < 0
- Bit 1 (0x2): Jump if result == 0
- Bit 0 (0x1): Jump if result > 0

Example: `JGE` (011) = jump if zero **or** positive = bits for "zero" and "positive" set.

**Critical detail**: The condition is evaluated on the **computation result**, not the original register value:

```assembly
@10
D=D-A;JEQ   // Jump if D was equal to 10 (because D-10 == 0)
            // D now contains (D-10), not original D
```

**Practice Exercise: Decode by Hand**

Before writing code, manually decode these binary instructions to assembly:

1. `0000000000001010` → ? (Hint: starts with 0)
2. `1110110000010000` → ? (Hint: starts with 111)
3. `1110011111001000` → ? (What does comp=011111 do?)
4. `1110001100000111` → ? (What does jump=111 mean?)

<details>
<summary>Click for answers</summary>

1. `@10` (A-instruction with value 10)
2. `D=A` (comp=110000 with a=0, dest=010)
3. `M=D+1` (comp=011111, dest=001)
4. `0;JMP` (comp=001100 is D, but dest=000 so we just compute D, then always jump)
</details>

**Why This Matters**

These encoding tables aren't arbitrary—they reflect hardware design choices:
- Common operations have **short codes** (fewer transistors)
- The **bitmap structure** simplifies decoding logic
- The **orthogonal design** (any comp + any dest + any jump) reduces special cases in hardware

When you build your assembler, you'll create lookup dictionaries from these tables. When you build your emulator, you'll decode these bit patterns back into actions. Understanding them now makes both steps dramatically easier.

🎓 **Study these tables**: Print them out. Quiz yourself. Every instruction you write maps to one of these bit patterns. Memorizing common ones (like D=M, M=D, D=D+1) helps build machine-level intuition that carries over to real assembly languages.

**Connecting Back to Your ALU (Project 2)**

Remember the ALU you built in Project 2? Those computation codes (`cccccc` bits) are **literally the control signals** for your ALU! Here's the direct mapping:

In Project 2, your ALU had control inputs that selected which operation to perform:
- `zx` (zero the x input)
- `nx` (negate the x input)
- `zy` (zero the y input)
- `ny` (negate the y input)
- `f` (function: 1=add, 0=and)
- `no` (negate the output)

Those 6 control bits map directly to the `cccccc` computation bits in your instructions! For example:

```
Operation | ALU Control | Assembly | Instruction Bits
----------|-------------|----------|------------------
D+A       | zx=0 nx=0   | D=D+A    | comp=000010
          | zy=0 ny=0   |          |
          | f=1 no=0    |          |
----------|-------------|----------|------------------
D&A       | zx=0 nx=0   | D=D&A    | comp=000000
          | zy=0 ny=0   |          |
          | f=0 no=0    |          |
```

**The Full Picture: How Your Hardware Executes Instructions**

When you execute `D=D+1`:

1. **Instruction Fetch**: Program Counter (PC) points to ROM address
2. **Instruction Decode**: CPU reads `1110011111010000`
   - Recognizes it's a C-instruction (starts with 111)
   - Extracts comp bits: `011111` = D+1
   - Extracts dest bits: `010` = store in D
   - Extracts jump bits: `000` = no jump

3. **Execute (This is your ALU from Project 2!)**:
   - Comp bits `011111` configure the ALU control signals
   - ALU receives D (from D register) and 1 (constant)
   - ALU outputs the sum (using the adder circuits you built)

4. **Store**: Result written to D register (from Project 3)
   - The dest bits `010` enable the write signal on the D register
   - D register latches the new value on the clock edge

5. **Next Instruction**: PC increments, cycle repeats

Every single component you built in Projects 1-3 is working together, controlled by the instruction bits you'll encode in this project. **This is what makes it a programmable computer** - the same hardware can perform different operations based on the instruction bits loaded into it.

**Step 2: Build the Assembler** (3 hours)
Translate assembly text to binary machine code:

```python
class Assembler:
    def __init__(self):
        # Lookup tables from above
        self.comp_table = {
            "0": "0101010", "1": "0111111", "-1": "0111010",
            "D": "0001100", "A": "0110000", "M": "1110000",
            "!D": "0001101", "!A": "0110001", "!M": "1110001",
            # ... rest of comp table
        }
        self.dest_table = {
            "": "000", "M": "001", "D": "010", "MD": "011",
            "A": "100", "AM": "101", "AD": "110", "AMD": "111"
        }
        self.jump_table = {
            "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
            "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"
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
```

**Step 3: Build the Emulator** (3-4 hours)
Execute machine code:

```python
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
        """Perform ALU operation based on comp bits"""
        # Map comp_bits to operations using your ALU from Project 2
        operations = {
            0b101010: lambda d, a: 0,
            0b111111: lambda d, a: 1,
            0b111010: lambda d, a: -1,
            0b001100: lambda d, a: d,
            0b110000: lambda d, a: a,
            0b001101: lambda d, a: ~d,
            0b110001: lambda d, a: ~a,
            # ... rest of operations
        }
        return operations[comp_bits](d_val, ay_val) & 0xFFFF

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
        for cycle in range(max_cycles):
            self.step()
            if self.PC >= len(self.ROM) or self.ROM[self.PC] == 0:
                break
```

**Step 4: Write Example Programs** (2-3 hours)

**Program 1: Add two numbers**
```assembly
// Compute RAM[2] = RAM[0] + RAM[1]
@0       // A = 0
D=M      // D = RAM[0]
@1       // A = 1
D=D+M    // D = D + RAM[1]
@2       // A = 2
M=D      // RAM[2] = D
```

**Program 2: Multiply (repeated addition)**
```assembly
// RAM[2] = RAM[0] * RAM[1]
@2       // Initialize result
M=0
@0       // Load multiplicand
D=M
@END
D;JEQ    // If RAM[0]=0, done
@counter
M=D      // counter = RAM[0]

(LOOP)
@counter
D=M
@END
D;JEQ    // If counter=0, done
@1
D=M      // D = RAM[1]
@2
M=D+M    // RAM[2] += RAM[1]
@counter
M=M-1    // counter--
@LOOP
0;JMP    // Repeat

(END)
@END
0;JMP    // Infinite loop (halt)
```

🎓 **Key lessons from multiplication**:
- **Loops** use labels and jumps
- **Variables** stored in RAM (counter at address 16+)
- **Conditionals** use jump instructions checking ALU flags

**Step 5: Build a Debugger** (2-3 hours)
Visualize execution:

```python
class Debugger:
    def __init__(self, cpu):
        self.cpu = cpu
        self.breakpoints = set()

    def step(self):
        """Step one instruction with output"""
        print(f"PC={self.cpu.PC:04d} | A={self.cpu.A:05d} | D={self.cpu.D:05d}")
        instruction = self.cpu.ROM[self.cpu.PC]
        print(f"Instruction: {instruction:016b}")
        self.cpu.step()

    def run_until_breakpoint(self):
        """Run until breakpoint or completion"""
        while self.cpu.PC not in self.breakpoints:
            self.step()

    def print_memory_region(self, start, end):
        """Display RAM contents"""
        for addr in range(start, end):
            print(f"RAM[{addr}] = {self.cpu.RAM[addr]}")
```

#### What You Should Understand After This Project
- ✅ Instructions are just bit patterns with meaning
- ✅ Registers provide fast temporary storage
- ✅ Memory access requires an address (stored in A register)
- ✅ Jumps change PC to enable loops and conditionals
- ✅ All high-level constructs (if, while, functions) compile to these primitives
- ✅ Assembly is tedious but gives complete hardware control

#### Common Pitfalls
- **Forgetting to update PC**: Every instruction must increment PC or jump
- **A vs M confusion**: `A` is the register value, `M` is RAM[A]
- **Jump conditions**: Flags are set by *computation result*, not destination
- **Off-by-one in loops**: Fencepost errors are common in assembly

#### Extension Ideas
- Add symbols/labels to assembler (Project 6 preview)
- Implement multiplication/division instructions
- Add I/O simulation (keyboard/screen)
- Create a disassembler (binary → assembly)
- Build a profiler (count instructions per program section)

#### Real-World Connection
- x86 assembly is more complex but follows the same principles
- ARM uses a similar load-store architecture (separate registers and memory)
- Modern compilers generate assembly from high-level code
- Understanding assembly is crucial for optimization, debugging, and security research

---