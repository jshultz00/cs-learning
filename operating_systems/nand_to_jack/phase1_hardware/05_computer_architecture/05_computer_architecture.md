### Project 5: Complete Computer Architecture
**Objective**: Build a complete Von Neumann computer with modular, testable components

#### Background Concepts

This is the capstone of the hardware phase—you're building a **complete computer** by integrating everything you've built so far. Unlike previous projects that focused on individual components, this project is about **architecture**: how components fit together to create a functioning system.

**What You've Built So Far**:

In Projects 1-4, you constructed all the fundamental building blocks:

1. **Project 1 - Logic Gates** ([logic_gates.py](../01_logic_gates/logic_gates.py)):
   - Compositional gate design starting from `NAND` as the only primitive
   - Built `NOT`, `AND`, `OR`, `XOR`, `MUX`, `DMUX` entirely from NAND gates
   - These gates form the foundation of all digital logic

2. **Project 2 - Binary Arithmetic** ([binary_arithmetic.py](../02_binary_arithmetic/binary_arithmetic.py)):
   - Half adder and full adder for binary addition
   - 16-bit addition with `add16()`, two's complement negation with `negate16()`
   - **Your ALU** with 6 control bits performing 18+ operations
   - ALU status flags: `zr` (zero) and `ng` (negative) for conditional logic

3. **Project 3 - Memory Hierarchy** ([memory_hierarchy.py](../03_memory_hierarchy/memory_hierarchy.py)):
   - D Flip-Flop (`DFF`) providing 1-bit memory with critical one-cycle delay
   - 16-bit `Register` with load control
   - Hierarchical RAM: `RAM8` → `RAM64` → `RAM512` using address decoding
   - `PC` (Program Counter) with reset, load, and increment capabilities

4. **Project 4 - Assembly Emulator** ([assembly_emulator.py](../04_assembly_emulator/assembly_emulator.py)):
   - Basic CPU simulator with instruction execution
   - Understanding of A-instructions and C-instructions
   - Foundation for the real computer architecture

**Now, in Project 5, you're building a production-quality computer with proper separation of concerns**.

**Von Neumann Architecture**:
The dominant computer design since 1945:

```
      ┌─────────────────────────────┐
      │           CPU               │
      │  ┌─────────────────────┐    │
      │  │        ALU          │    │  Performs all computations
      │  │  (compute method)   │    │  (add, sub, and, or, etc.)
      │  └─────────────────────┘    │
      │                              │
      │  ┌─────────────────────┐    │
      │  │    Registers        │    │
      │  │  A (address/value)  │    │  Three architectural registers
      │  │  D (data)           │    │  visible to programmers
      │  │  PC (program ctr)   │    │
      │  └─────────────────────┘    │
      │                              │
      │  ┌─────────────────────┐    │
      │  │  Control Logic      │    │  Fetch, decode, execute
      │  │  (execute_*_instr)  │    │  and jump evaluation
      │  └─────────────────────┘    │
      └──────────┬──────────────────┘
                 │ (Bus)
      ┌──────────┴──────────────────┐
      │       Memory System         │
      │  ┌──────────┬──────────┐    │
      │  │   ROM    │   RAM    │    │  Separate instruction
      │  │(32K ins) │ (32K data)│    │  and data memory
      │  └──────────┴──────────┘    │
      └─────────────────────────────┘
```

**Key insight**: Instructions and data are in separate memory spaces in our implementation. This is called a **Harvard architecture** modification of Von Neumann, common in embedded systems and safer for learning (can't accidentally execute data).

**The Fetch-Decode-Execute Cycle**:
Every computer does this repeatedly:

```python
while running:
    instruction = fetch()      # Read instruction from ROM[PC]
    decode(instruction)        # Determine A-instr vs C-instr
    execute(instruction)       # Perform the operation
    # PC automatically advances or jumps
```

This happens billions of times per second in modern CPUs!

#### The Hack Instruction Set Architecture (ISA)

Before building the computer, understand what it can do:

**Three Instruction Types**:

1. **A-instruction** (Address): `0vvvvvvvvvvvvvvv`
   - Format: 15-bit value with leading 0
   - Effect: `A = value`, `PC++`
   - Assembly: `@5` loads 5 into A register
   - Used for: loading constants, setting memory addresses, jump targets

2. **C-instruction** (Compute): `111accccccdddjjj`
   - Format: 111 prefix + a-bit + 6-bit comp + 3-bit dest + 3-bit jump
   - Effect: `dest = ALU_compute(comp)`, conditionally jump based on result
   - Assembly: `D=D+1;JGT` means "increment D, jump if result > 0"

3. **HALT instruction**: `1111111111111111` (all 1s)
   - Format: Special encoding not used by standard C-instructions
   - Effect: Stops program execution immediately
   - Assembly: `HALT`
   - Used for: Explicitly ending program execution (cleaner than infinite loops)

**Important Notes**:
- `@0` is a **valid instruction** that sets A=0. It does NOT cause a halt!
- Use `HALT` to explicitly stop execution instead of infinite loops like `@END; 0;JMP`

**C-Instruction Fields**:

- **a-bit** (1 bit): Select between A register (0) or RAM[A] (1) as ALU input
- **comp** (6 bits): Specifies which ALU operation (28 total operations)
- **dest** (3 bits): Where to store result (A, D, M, or combinations)
- **jump** (3 bits): Conditional jump based on ALU output flags

See [assembler.py:17-53](assembler.py#L17-L53) for the complete encoding tables.

#### Learning Path

**Step 1: Study the Existing Modular Architecture** (30 minutes)

You already have a complete, well-structured implementation! Let's understand it:

**Component Overview**:

```
computer_architecture.py    # Main module (imports all components)
├── alu.py                 # Arithmetic Logic Unit
├── ram.py                 # Random Access Memory
├── rom.py                 # Read-Only Memory
├── cpu.py                 # Central Processing Unit
└── assembler.py           # Assembly → Machine Code translator
```

Each component has a **single responsibility**:

- **ALU**: Pure computation (no state, no memory access)
- **RAM/ROM**: Pure storage (no computation, no control logic)
- **CPU**: Orchestration (uses ALU, reads/writes RAM/ROM)
- **Assembler**: Translation (assembly text → binary instructions)

🎓 **Key insight**: This separation mirrors real hardware. The ALU is a physical circuit, RAM is memory chips, CPU is the control circuitry. Each can be designed, tested, and upgraded independently.

**Step 2: Understand the ALU Implementation** (45 minutes)

Read [alu.py](alu.py) carefully:

```python
class ALU:
    def compute(self, comp_bits, d_val, ay_val):
        """Perform one of 28 operations based on comp_bits"""
        # Maps 6-bit comp code to operation
        operations = {
            0b101010: lambda d, a: 0,        # Constant zero
            0b111111: lambda d, a: 1,        # Constant one
            0b001100: lambda d, a: d,        # Pass through D
            0b000010: lambda d, a: ...,      # D+A addition
            # ... 24 more operations
        }
        result = operations[comp_bits](d_val, ay_val)
        return to_unsigned(result)  # Always return 16-bit unsigned
```

**Key Design Decisions**:

1. **Lookup table approach**: Clean, readable, easy to verify against spec
2. **Signed arithmetic helpers**: `to_signed()` and `to_unsigned()` handle two's complement
3. **Pure function**: No side effects, just input → output
4. **CPU decides A vs M**: ALU receives `ay_val`, doesn't know if it's A or RAM[A]

**What operations exist?**
- Constants: 0, 1, -1
- Pass-through: D, A/M
- Unary: !D, !A, -D, -A (bitwise NOT and arithmetic negate)
- Increment/decrement: D+1, D-1, A+1, A-1
- Binary arithmetic: D+A, D-A, A-D
- Binary logic: D&A, D|A

**Exercise**: Trace how `D=D+1` gets executed:
1. Assembler converts to: `111 0 011111 010 000` (comp=D+1, dest=D, jump=none)
2. CPU extracts comp_bits = `011111`
3. ALU computes: `operations[0b011111](D, A)` = `to_signed(D) + 1`
4. CPU writes result back to D register

**Step 3: Understand Memory Components** (30 minutes)

**RAM** ([ram.py](ram.py)): Data storage during execution

```python
class RAM:
    def __init__(self, size=32768):
        self.memory = [0] * size  # 32K words of 16-bit data

    def __getitem__(self, address):
        return self.memory[address]  # Array-style access

    def __setitem__(self, address, value):
        self.memory[address] = value & 0xFFFF  # Mask to 16 bits
```

**ROM** ([rom.py](rom.py)): Instruction storage (loaded once, read many times)

```python
class ROM:
    def load_program(self, binary_instructions):
        """Load list of "0101010101010101" binary strings"""
        for i, instr in enumerate(binary_instructions):
            self.memory[i] = int(instr, 2)  # Convert binary string to int

    def fetch(self, address):
        return self.memory[address]  # Return instruction at address
```

🎓 **Harvard vs Von Neumann**: In pure Von Neumann, instructions and data share one memory. We use separate ROM/RAM (Harvard modification) because:
- **Safety**: Can't accidentally execute data or modify code
- **Simplicity**: No need for memory protection logic
- **Common in embedded systems**: Many real CPUs do this

**Step 4: Deep Dive into CPU Implementation** (2 hours)

The CPU ([cpu.py](cpu.py)) is the most complex component. Let's trace a complete execution cycle:

**CPU Architecture**:

```python
class CPU:
    def __init__(self):
        # Registers (visible to programmer)
        self.A = 0          # Address/value register
        self.D = 0          # Data register
        self.PC = 0         # Program counter

        # Internal components
        self.ram = RAM()
        self.rom = ROM()
        self.alu = ALU()
```

**Instruction Execution Flow**:

```
┌─────────────┐
│ 1. FETCH    │  instruction = rom[PC]
└──────┬──────┘
       │
┌──────▼──────┐
│ 2. DECODE   │  Check bit 15: A-instr (0) or C-instr (1)?
└──────┬──────┘
       │
┌──────▼──────┐
│ 3. EXECUTE  │  A-instr: A = value, PC++
└─────────────┘  C-instr: ALU compute → dest, check jump
```

**A-Instruction Execution** ([cpu.py:60-75](cpu.py#L60-L75)):

```python
def execute_a_instruction(self, instruction):
    """@value: Load value into A register"""
    value = instruction & 0x7FFF  # Mask bottom 15 bits
    self.A = value
    self.PC += 1
```

Simple! Just load the value and increment PC.

**C-Instruction Execution** ([cpu.py:77-113](cpu.py#L77-L113)):

```python
def execute_c_instruction(self, instruction):
    """dest=comp;jump: Compute, store, conditionally jump"""

    # 1. DECODE bit fields
    a_bit = (instruction >> 12) & 1       # A or M?
    comp_bits = (instruction >> 6) & 0x3F # Which operation?
    dest_bits = (instruction >> 3) & 0x7  # Where to store?
    jump_bits = instruction & 0x7         # Jump condition?

    # 2. COMPUTE using ALU
    y = self.ram[self.A] if a_bit else self.A  # Select A or M
    result = self.alu.compute(comp_bits, self.D, y)

    # 3. STORE to destination(s)
    if dest_bits & 0x4:  # Bit 2 set → A
        self.A = result
    if dest_bits & 0x2:  # Bit 1 set → D
        self.D = result
    if dest_bits & 0x1:  # Bit 0 set → M (RAM[A])
        self.ram[self.A] = result

    # 4. JUMP evaluation
    if self.should_jump(jump_bits, result):
        self.PC = self.A  # Jump to address in A
    else:
        self.PC += 1      # Continue to next instruction
```

🎓 **Key insight**: The CPU is a **state machine**. Each instruction reads current state (registers, memory), performs computation (via ALU), writes new state, and updates PC.

**Jump Logic** ([cpu.py:115-154](cpu.py#L115-L154)):

Jumps are based on the **sign** of the ALU result:

```python
def should_jump(self, jump_bits, value):
    """Evaluate jump condition based on ALU output"""
    if jump_bits == 0:       return False  # No jump
    if jump_bits == 0b111:   return True   # Unconditional (JMP)

    # Check value's sign
    is_negative = (value & 0x8000) != 0    # MSB set = negative
    is_zero = value == 0
    is_positive = not is_negative and not is_zero

    conditions = {
        0b001: is_positive,              # JGT (>0)
        0b010: is_zero,                  # JEQ (=0)
        0b011: not is_negative,          # JGE (≥0)
        0b100: is_negative,              # JLT (<0)
        0b101: not is_zero,              # JNE (≠0)
        0b110: is_negative or is_zero,   # JLE (≤0)
    }
    return conditions.get(jump_bits, False)
```

**Exercise**: Trace execution of this program:
```assembly
@5        // A = 5
D=A       // D = 5, PC++
@10       // A = 10
M=D       // RAM[10] = 5, PC++
```

1. **Cycle 1**: Fetch `@5` (0x0005) → A=5, PC=1
2. **Cycle 2**: Fetch `D=A` → ALU computes A, stores to D → D=5, PC=2
3. **Cycle 3**: Fetch `@10` (0x000A) → A=10, PC=3
4. **Cycle 4**: Fetch `M=D` → ALU computes D (pass-through), stores to RAM[10] → RAM[10]=5, PC=4

**Step 5: Understanding the Assembler** (1 hour)

The assembler ([assembler.py](assembler.py)) translates human-readable assembly to machine code:

**Three Lookup Tables**:

```python
comp_table = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "M": "1110000",
    "D+1": "0011111", "D-A": "0010011",
    # ... all 28 operations
}

dest_table = {
    "": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111"
}

jump_table = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"
}
```

**Assembly Process**:

```python
def assemble(self, assembly_code):
    """Convert list of assembly strings to binary"""
    binary = []
    for line in assembly_code:
        parsed = self.parse_line(line)  # Extract components
        if parsed[0] == 'A':
            binary.append(self.assemble_a_instruction(parsed[1]))
        elif parsed[0] == 'C':
            _, dest, comp, jump = parsed
            binary.append(self.assemble_c_instruction(dest, comp, jump))
    return binary
```

**Example**: Assemble `MD=D+1;JGT`

1. **Parse**: dest="MD", comp="D+1", jump="JGT"
2. **Lookup**:
   - comp_table["D+1"] = "0011111" (a=0, comp=011111)
   - dest_table["MD"] = "011"
   - jump_table["JGT"] = "001"
3. **Combine**: "111" + "0011111" + "011" + "001" = "1110011111011001"

🎓 **Key insight**: The assembler is a simple **translator**. It doesn't execute code, just converts text to numbers using lookup tables.

**Step 6: Write and Test Programs** (2-3 hours)

Now use your computer! Create test programs:

**Test 1: Basic arithmetic**

```python
from computer_architecture import CPU, Assembler

cpu = CPU()
asm = Assembler()

# Compute 5 + 3
program = [
    "@5",
    "D=A",      # D = 5
    "@3",
    "D=D+A",    # D = 5 + 3 = 8
    "HALT"      # Stop execution
]

binary = asm.assemble(program)
cpu.load_program(binary)
halted, cycles = cpu.run()

print(f"Result: D = {cpu.D}")  # Should print 8
print(f"Halted: {halted}, Cycles: {cycles}")  # Should print True, 5
```

**Test 2: Memory operations**

```python
# IMPORTANT: Reset CPU between program runs!
cpu.reset()

# Write 42 to RAM[100]
program = [
    "@42",
    "D=A",
    "@100",
    "M=D",
    "HALT"
]

binary = asm.assemble(program)
cpu.load_program(binary)
halted, cycles = cpu.run()

print(f"RAM[100] = {cpu.ram[100]}")  # Should print 42
```

**Test 3: Conditional jump**

```python
# IMPORTANT: Reset CPU between program runs!
cpu.reset()

# Jump if D > 0
program = [
    "@5",
    "D=A",      # D = 5 (positive)
    "@10",
    "D;JGT",    # Should jump to address 10
    "HALT"      # Won't execute due to jump
]

binary = asm.assemble(program)
cpu.load_program(binary)
# Note: This will hit max_cycles since we jump past HALT
halted, cycles = cpu.run(max_cycles=10)

print(f"PC = {cpu.PC}")  # Should print 10
print(f"Halted: {halted}")  # Should print False (max_cycles reached, not HALT)
```

**Test 4: Sum of 1 to N** (more complex)

```python
# IMPORTANT: Reset CPU between program runs!
cpu.reset()

# Sum numbers from 1 to 10
program = [
    "@10",      # 0: counter = 10 (A=10)
    "D=A",      # 1: D = 10
    "@16",      # 2: A = 16
    "M=D",      # 3: RAM[16] = counter = 10
    "@17",      # 4: A = 17
    "M=0",      # 5: RAM[17] = sum = 0
    # LOOP (starts at address 6):
    "@16",      # 6: A = 16
    "D=M",      # 7: D = RAM[16] = counter
    "@20",      # 8: A = 20 (address of HALT)
    "D;JEQ",    # 9: if counter == 0, jump to HALT
    "@17",      # 10: A = 17
    "D=M",      # 11: D = RAM[17] = sum
    "@16",      # 12: A = 16
    "D=D+M",    # 13: D = sum + counter
    "@17",      # 14: A = 17
    "M=D",      # 15: RAM[17] = sum + counter
    "@16",      # 16: A = 16
    "M=M-1",    # 17: counter--
    "@6",       # 18: A = 6 (address of LOOP)
    "0;JMP",    # 19: Jump back to LOOP
    # END:
    "HALT"      # 20: Stop execution
]

binary = asm.assemble(program)
cpu.load_program(binary)
halted, cycles = cpu.run(max_cycles=200)

print(f"Sum 1..10 = {cpu.ram[17]}")  # Should print 55
print(f"Halted: {halted}, Cycles: {cycles}")  # Should print True, 151
```

**Step 7: Build a Debugger/Visualizer** (2-3 hours, optional)

Create tools to inspect execution:

```python
class CPUDebugger:
    """Step-by-step execution with visualization"""

    def __init__(self, cpu, assembler):
        self.cpu = cpu
        self.asm = assembler
        self.breakpoints = set()

    def disassemble_instruction(self, instr):
        """Convert binary instruction back to assembly"""
        if instr & 0x8000:  # C-instruction
            a_bit = (instr >> 12) & 1
            comp_bits = (instr >> 6) & 0x3F
            dest_bits = (instr >> 3) & 0x7
            jump_bits = instr & 0x7

            # Reverse lookup in assembler tables
            comp = self._find_comp(comp_bits, a_bit)
            dest = self._find_dest(dest_bits)
            jump = self._find_jump(jump_bits)

            dest_str = f"{dest}=" if dest else ""
            jump_str = f";{jump}" if jump else ""
            return f"{dest_str}{comp}{jump_str}"
        else:  # A-instruction
            value = instr & 0x7FFF
            return f"@{value}"

    def step(self):
        """Execute one instruction with full trace"""
        pc = self.cpu.PC
        instr = self.cpu.rom[pc]
        asm = self.disassemble_instruction(instr)

        print(f"\n{'='*60}")
        print(f"PC: {pc:04d} | Instruction: {asm}")
        print(f"Before: A={self.cpu.A:05d} D={self.cpu.D:05d}")

        self.cpu.step()

        print(f"After:  A={self.cpu.A:05d} D={self.cpu.D:05d}")
        print(f"Next PC: {self.cpu.PC:04d}")

    def run_until_breakpoint(self, max_cycles=1000):
        """Run until hitting breakpoint or max cycles"""
        for _ in range(max_cycles):
            if self.cpu.PC in self.breakpoints:
                print(f"Hit breakpoint at PC={self.cpu.PC}")
                return
            if self.cpu.PC >= self.cpu.rom.size:
                print("Reached end of ROM")
                return
            self.cpu.step()
```

Usage:
```python
cpu = CPU()
asm = Assembler()
dbg = CPUDebugger(cpu, asm)

program = ["@5", "D=A", "@10", "M=D"]
binary = asm.assemble(program)
cpu.load_program(binary)

# Step through one instruction at a time
dbg.step()  # Execute @5
dbg.step()  # Execute D=A
dbg.step()  # Execute @10
dbg.step()  # Execute M=D
```

**Step 8: Performance Profiling** (1 hour, optional)

Track instruction execution statistics:

```python
class CPUProfiler:
    """Track performance metrics"""

    def __init__(self, cpu):
        self.cpu = cpu
        self.instruction_counts = {"A": 0, "C": 0}
        self.comp_usage = {}
        self.jump_taken = 0
        self.jump_not_taken = 0

    def profile_step(self):
        """Execute and record metrics"""
        instr = self.cpu.fetch()

        if instr & 0x8000:  # C-instruction
            self.instruction_counts["C"] += 1
            comp_bits = (instr >> 6) & 0x3F
            self.comp_usage[comp_bits] = self.comp_usage.get(comp_bits, 0) + 1

            # Track jump behavior
            old_pc = self.cpu.PC
            self.cpu.step()
            if self.cpu.PC != old_pc + 1:
                self.jump_taken += 1
            else:
                self.jump_not_taken += 1
        else:  # A-instruction
            self.instruction_counts["A"] += 1
            self.cpu.step()

    def report(self):
        """Print performance statistics"""
        total = sum(self.instruction_counts.values())
        print(f"\nExecution Profile:")
        print(f"  Total instructions: {total}")
        print(f"  A-instructions: {self.instruction_counts['A']} "
              f"({100*self.instruction_counts['A']/total:.1f}%)")
        print(f"  C-instructions: {self.instruction_counts['C']} "
              f"({100*self.instruction_counts['C']/total:.1f}%)")
        print(f"  Jumps taken: {self.jump_taken}")
        print(f"  Jumps not taken: {self.jump_not_taken}")
        print(f"\nTop 5 ALU operations:")
        for comp_bits, count in sorted(self.comp_usage.items(),
                                       key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {comp_bits:06b}: {count} times")
```

#### What You Should Understand After This Project

- ✅ **Computer = CPU + Memory + Bus**: Clear separation of responsibilities
- ✅ **Fetch-decode-execute cycle**: The heartbeat of all computation
- ✅ **ISA defines the contract**: Hardware implements what software expects
- ✅ **Modular design enables testing**: Each component verified independently
- ✅ **ALU is stateless**: Pure computation with no side effects
- ✅ **CPU is a state machine**: Reads state → computes → writes state → repeat
- ✅ **Assembly is symbolic machine code**: Human-readable representation of bits
- ✅ **Harvard architecture**: Separate instruction and data memory for safety

#### Common Pitfalls

**1. Forgetting to increment PC**
```python
# WRONG:
def execute_a_instruction(self, instruction):
    self.A = instruction & 0x7FFF
    # Forgot self.PC += 1 → infinite loop!

# RIGHT:
def execute_a_instruction(self, instruction):
    self.A = instruction & 0x7FFF
    self.PC += 1  # Always increment unless jumping
```

**2. Incorrect bit masking**
```python
# WRONG:
value = instruction & 0xFFFF  # Gets all 16 bits, including type bit!

# RIGHT:
value = instruction & 0x7FFF  # Gets bottom 15 bits only
```

**3. Treating @0 as halt**
```python
# WRONG:
if self.rom[self.PC] == 0:
    break  # @0 is valid! Don't halt!

# RIGHT:
if instruction == 0xFFFF:  # Check for HALT instruction
    return False  # Stop execution
```

**4. Forgetting to reset CPU between programs**
```python
# WRONG:
cpu.load_program(program1)
cpu.run()
# D, A, PC, RAM still have old values!
cpu.load_program(program2)
cpu.run()  # May produce incorrect results

# RIGHT:
cpu.load_program(program1)
cpu.run()
cpu.reset()  # Clear all state
cpu.load_program(program2)
cpu.run()  # Clean execution
```

**5. Not using HALT instruction**
```python
# OLD WAY (works but wastes cycles):
program = [
    # ... your code ...
    "@END",
    "0;JMP"  # Infinite loop
]

# BETTER WAY (explicit and efficient):
program = [
    # ... your code ...
    "HALT"  # Stop cleanly
]
```

**6. Not masking ALU output**
```python
# WRONG:
result = d_val + ay_val  # Might exceed 16 bits!

# RIGHT:
result = (d_val + ay_val) & 0xFFFF  # Keep 16-bit
```

**7. Confusing A register vs RAM[A]**
```python
# WRONG:
y = self.A  # Always uses A, ignoring a_bit!

# RIGHT:
y = self.ram[self.A] if a_bit else self.A  # Choose based on a_bit
```

#### Extension Ideas

**Level 1: Enhance the Computer**
- Add memory-mapped I/O (screen at 0x4000-0x5FFF, keyboard at 0x6000)
- Implement a clock that limits instruction rate (e.g., 1 MHz)
- Add hardware breakpoints (halt when PC reaches specific address)
- Implement single-step mode for debugging

**Level 2: Improve the Assembler**
- Add label support: `(LOOP)` and `@LOOP`
- Add variable allocation: `@counter` automatically assigns RAM address
- Add constants: `@SCREEN` = 16384, `@KBD` = 24576
- Two-pass assembly: first pass collects labels, second pass resolves addresses

**Level 3: Build Development Tools**
- Syntax highlighting for assembly code
- Instruction timing analyzer (cycles per instruction)
- Memory access pattern visualizer (see which RAM locations are hot)
- Call stack tracer (for function calls once you implement them)

**Level 4: Optimize Performance**
- Add instruction cache (recently executed instructions stay fast)
- Implement pipelining (overlap fetch/decode/execute stages)
- Add branch prediction (guess jump outcomes to avoid stalls)
- Build a superscalar CPU (execute multiple instructions per cycle)

**Level 5: Advanced Architecture**
- Implement interrupts (hardware can pause CPU and inject instructions)
- Add DMA (Direct Memory Access for fast I/O)
- Build a multi-core version (multiple CPUs sharing memory)
- Implement virtual memory (address translation for memory protection)

#### Real-World Connection

You've built a **real computer**. It's simplified, but the principles are identical to production systems:

**Similar Complexity**:
- **MOS 6502** (Apple II, Commodore 64, NES): ~3500 transistors, similar ISA complexity
- **ARM Cortex-M0**: Modern embedded CPU, comparable instruction set
- **RISC-V RV32I**: Open-source ISA, similar simplicity for base instructions

**Modern Additions**:
- **Pipelining**: Modern CPUs overlap instruction stages (5-20 stages deep)
- **Out-of-order execution**: CPU reorders instructions for efficiency
- **Multiple cores**: 4-64 CPUs sharing memory
- **Vector units**: SIMD (Single Instruction Multiple Data) for parallel computation
- **Branch prediction**: 95%+ accuracy predicting jumps
- **Memory hierarchy**: L1/L2/L3 caches, virtual memory, DRAM, SSD

**But the fundamentals remain**:
- Fetch-decode-execute cycle
- Register-based architecture
- Von Neumann stored program concept
- Assembly language as intermediate representation

**What You Can Build on This**:
- Simple operating system (scheduler, memory manager)
- Compiler (high-level language → assembly)
- Assembler with macro support
- Debugger with full symbolic debugging
- Emulator for other architectures
- Real-time operating system for embedded control

#### Success Criteria

You've mastered this project when you can:

1. **Trace execution**: Given assembly, predict final register/memory state
2. **Debug programs**: Find bugs by inspecting PC, registers, memory
3. **Write assembly**: Convert algorithms to Hack assembly language
4. **Explain architecture**: Draw diagram showing how CPU, ALU, RAM, ROM connect
5. **Modify ISA**: Add new instructions by updating assembler and CPU
6. **Optimize code**: Reduce instruction count for common operations

#### Next Steps

**Project 6: Assembler Enhancement**
Build a full-featured assembler with:
- Symbol table for labels and variables
- Two-pass assembly algorithm
- Error checking and reporting
- Macro expansion
- Include file support

**Project 7: Virtual Machine (Part 1)**
Build a VM that translates stack-based bytecode to assembly:
- Stack operations: push, pop
- Arithmetic: add, sub, neg, eq, gt, lt
- Logic: and, or, not
- This abstraction enables high-level languages

**Project 8-12: Software Stack**
Continue building up to a complete software system:
- VM Part 2: Functions and program flow
- High-level language design
- Compiler front-end (parser, syntax tree)
- Compiler back-end (code generation)
- Operating system (memory, I/O, file system)

---

Congratulations! You've completed the **hardware phase** of Nand to Tetris. You now understand computers from transistors to running programs. Everything above this is software—and you've built the platform that software runs on.

The journey from NAND gates to a working computer is one of the most profound experiences in computer science. You've literally built a computer from first principles. Take a moment to appreciate what you've accomplished. 🎉
