### Project 5: Complete Computer Architecture
**Objective**: Integrate all components into a functioning computer

#### Background Concepts

This is the capstone of the hardware phase—you're building a **complete computer**. It will execute real programs, manipulate memory, and demonstrate the fetch-decode-execute cycle that powers every computer from your phone to supercomputers.

**Von Neumann Architecture**:
The dominant computer design since 1945:

```
      ┌─────────────┐
      │     CPU     │
      │  ┌───────┐  │
      │  │  ALU  │  │
      │  └───────┘  │
      │  ┌───────┐  │
      │  │Control│  │
      │  └───────┘  │
      │  Registers  │
      └──────┬──────┘
             │ (Bus)
      ┌──────┴──────┐
      │   Memory    │
      │  (ROM+RAM)  │
      │ Instructions│
      │  and Data   │
      └─────────────┘
```

**Key insight**: Instructions and data share the same memory. This enables:
- Programs that modify themselves
- Compilers (programs that generate programs)
- The entire software ecosystem we know today

**The Fetch-Decode-Execute Cycle**:
Every computer does this repeatedly:
1. **Fetch**: Read instruction from memory[PC]
2. **Decode**: Determine what the instruction means
3. **Execute**: Perform the operation
4. **Repeat**: PC moves to next instruction

This happens billions of times per second in modern CPUs!

#### Learning Path

**Step 1: Design the Computer Architecture** (1 hour)
Plan the system:

**Components needed**:
- CPU (ALU + registers + control logic)
- RAM (32K words of data memory)
- ROM (32K words of instruction memory)
- Memory-mapped I/O (keyboard, screen)

**Memory map**:
```
0x0000-0x3FFF: RAM (16K for variables and stack)
0x4000-0x5FFF: Screen memory (8K words = 256x512 pixels)
0x6000       : Keyboard input (1 word)
```

🎓 **Memory-mapped I/O**: Hardware devices appear as memory locations. Reading address 0x6000 returns the last key pressed. Writing to 0x4000-0x5FFF changes pixels on screen.

**Step 2: Integrate the CPU** (2-3 hours)
Combine your ALU, registers, and control logic:

```python
class HackCPU:
    """Complete CPU with control logic"""
    def __init__(self):
        self.A = 0                    # Address register
        self.D = 0                    # Data register
        self.PC = 0                   # Program counter
        self.alu = ALU()              # Your ALU from Project 2
        self.instruction = 0          # Current instruction

    def connect_memory(self, memory):
        """Connect CPU to memory system"""
        self.memory = memory

    def fetch(self):
        """Fetch instruction from ROM[PC]"""
        self.instruction = self.memory.read_rom(self.PC)
        return self.instruction

    def decode_and_execute(self):
        """Decode instruction and execute it"""
        instr = self.instruction

        if instr & 0x8000:  # C-instruction
            # Extract control bits
            a_bit = (instr >> 12) & 1
            comp = (instr >> 6) & 0x3F
            dest = (instr >> 3) & 0x7
            jump = instr & 0x7

            # ALU input selection
            x = self.D
            y = self.memory.read_ram(self.A) if a_bit else self.A

            # Compute
            alu_out, zr, ng = self.alu.compute(comp, x, y)

            # Write to destinations
            write_to_mem = False
            if dest & 0x4:  # Write to A
                self.A = alu_out
            if dest & 0x2:  # Write to D
                self.D = alu_out
            if dest & 0x1:  # Write to M[A]
                write_to_mem = True
                self.memory.write_ram(self.A, alu_out)

            # Handle jumps
            do_jump = self._should_jump(jump, zr, ng)
            if do_jump:
                self.PC = self.A
            else:
                self.PC += 1

        else:  # A-instruction
            self.A = instr & 0x7FFF
            self.PC += 1

    def _should_jump(self, jump_bits, is_zero, is_negative):
        """Evaluate jump condition"""
        if jump_bits == 0:
            return False
        if jump_bits == 0b111:  # JMP
            return True

        is_positive = not is_zero and not is_negative

        jump_table = {
            0b001: is_positive,      # JGT
            0b010: is_zero,          # JEQ
            0b011: not is_negative,  # JGE
            0b100: is_negative,      # JLT
            0b101: not is_zero,      # JNE
            0b110: is_negative or is_zero,  # JLE
        }
        return jump_table.get(jump_bits, False)

    def cycle(self):
        """One complete CPU cycle: fetch + decode + execute"""
        self.fetch()
        self.decode_and_execute()
```

**Step 3: Build the Memory System** (2 hours)
Combine ROM, RAM, and I/O:

```python
class Memory:
    """Complete memory system with ROM, RAM, and I/O"""
    def __init__(self, rom_size=32768, ram_size=16384):
        self.ROM = [0] * rom_size  # Instruction memory
        self.RAM = [0] * ram_size  # Data memory (0x0000-0x3FFF)
        self.screen = [0] * 8192   # Screen buffer (0x4000-0x5FFF)
        self.keyboard = 0          # Keyboard register (0x6000)

    def load_program(self, instructions):
        """Load program into ROM"""
        for i, instruction in enumerate(instructions):
            if i < len(self.ROM):
                self.ROM[i] = instruction

    def read_rom(self, address):
        """Fetch instruction from ROM"""
        if 0 <= address < len(self.ROM):
            return self.ROM[address]
        return 0

    def read_ram(self, address):
        """Read from RAM or memory-mapped devices"""
        if 0 <= address < 0x4000:  # RAM
            return self.RAM[address]
        elif 0x4000 <= address < 0x6000:  # Screen
            return self.screen[address - 0x4000]
        elif address == 0x6000:  # Keyboard
            return self.keyboard
        return 0

    def write_ram(self, address, value):
        """Write to RAM or memory-mapped devices"""
        value = value & 0xFFFF  # Keep 16-bit

        if 0 <= address < 0x4000:  # RAM
            self.RAM[address] = value
        elif 0x4000 <= address < 0x6000:  # Screen
            self.screen[address - 0x4000] = value
            # Note: In a real system, this would update display
```

**Step 4: Build the Complete Computer** (1 hour)
Connect CPU and Memory:

```python
class HackComputer:
    """Complete computer system"""
    def __init__(self):
        self.cpu = HackCPU()
        self.memory = Memory()
        self.cpu.connect_memory(self.memory)
        self.cycles = 0
        self.running = False

    def load_program(self, program):
        """Load program into ROM"""
        # program can be binary strings or integers
        instructions = [
            int(instr, 2) if isinstance(instr, str) else instr
            for instr in program
        ]
        self.memory.load_program(instructions)

    def reset(self):
        """Reset computer to initial state"""
        self.cpu.PC = 0
        self.cpu.A = 0
        self.cpu.D = 0
        self.cycles = 0
        self.running = True

    def step(self):
        """Execute one instruction"""
        if self.running:
            self.cpu.cycle()
            self.cycles += 1

    def run(self, max_cycles=10000):
        """Run until halt or max cycles"""
        self.reset()
        while self.running and self.cycles < max_cycles:
            self.step()
            # Halt on infinite loop at end
            if self.cpu.PC >= len(self.memory.ROM):
                self.running = False
```

**Step 5: Create a Visual Dashboard** (3-4 hours)
Build a visualization of the running computer:

```python
class ComputerDashboard:
    """Visual representation of computer state"""
    def __init__(self, computer):
        self.computer = computer

    def display_state(self):
        """Show CPU and memory state"""
        cpu = self.computer.cpu
        mem = self.computer.memory

        print("=" * 60)
        print(f"CYCLE: {self.computer.cycles:06d}")
        print("-" * 60)
        print("CPU STATE:")
        print(f"  PC = {cpu.PC:05d}  (0x{cpu.PC:04X})")
        print(f"  A  = {cpu.A:05d}  (0x{cpu.A:04X})")
        print(f"  D  = {cpu.D:05d}  (0x{cpu.D:04X})")
        print("-" * 60)
        print("INSTRUCTION:")
        instr = cpu.instruction
        print(f"  Binary: {instr:016b}")
        print(f"  Hex:    0x{instr:04X}")
        if instr & 0x8000:
            print(f"  Type:   C-instruction")
            self._decode_c_instruction(instr)
        else:
            print(f"  Type:   A-instruction")
            print(f"  Value:  @{instr & 0x7FFF}")
        print("-" * 60)
        print("RAM (first 10 locations):")
        for i in range(10):
            print(f"  RAM[{i}] = {mem.RAM[i]:05d}")
        print("=" * 60)

    def _decode_c_instruction(self, instr):
        """Pretty-print C-instruction"""
        dest_map = {
            0: "", 1: "M", 2: "D", 3: "MD",
            4: "A", 5: "AM", 6: "AD", 7: "AMD"
        }
        jump_map = {
            0: "", 1: "JGT", 2: "JEQ", 3: "JGE",
            4: "JLT", 5: "JNE", 6: "JLE", 7: "JMP"
        }

        # Extract fields (decode comp lookup omitted for brevity)
        dest = dest_map[(instr >> 3) & 0x7]
        jump = jump_map[instr & 0x7]

        dest_str = f"{dest}=" if dest else ""
        jump_str = f";{jump}" if jump else ""

        print(f"  Format: {dest_str}<comp>{jump_str}")
```

**Step 6: Test Programs** (2-3 hours)

**Test 1: Compute sum of 1 to N**
```assembly
// Compute sum = 1 + 2 + ... + N (N in RAM[0])
    @R0
    D=M
    @n
    M=D      // n = RAM[0]
    @sum
    M=0      // sum = 0
    @i
    M=1      // i = 1

(LOOP)
    @i
    D=M
    @n
    D=D-M
    @END
    D;JGT    // if i > n goto END

    @i
    D=M
    @sum
    M=D+M    // sum += i
    @i
    M=M+1    // i++
    @LOOP
    0;JMP

(END)
    @sum
    D=M
    @R1
    M=D      // RAM[1] = sum
    @END
    0;JMP    // halt
```

Run it and watch the dashboard show each step!

**Test 2: Draw to screen**
```assembly
// Fill screen with pattern
    @SCREEN  // SCREEN = 16384 (0x4000)
    D=A
    @addr
    M=D      // addr = screen base

(LOOP)
    @addr
    A=M      // Load address
    M=-1     // Write 0xFFFF (all pixels on)
    @addr
    M=M+1    // Next word
    @8192
    D=A
    @addr
    D=M-D
    @LOOP
    D;JLT    // Loop while addr < 8192
```

If you add screen rendering, you'll see pixels light up!

**Step 7: Add Performance Metrics** (1 hour)
```python
class Profiler:
    """Track computer performance"""
    def __init__(self, computer):
        self.computer = computer
        self.instruction_counts = {}
        self.memory_accesses = 0

    def record_instruction(self, instr):
        """Count instruction types"""
        instr_type = "C" if (instr & 0x8000) else "A"
        self.instruction_counts[instr_type] = \
            self.instruction_counts.get(instr_type, 0) + 1

    def report(self):
        """Display performance statistics"""
        total = sum(self.instruction_counts.values())
        print(f"Total instructions: {total}")
        for instr_type, count in self.instruction_counts.items():
            pct = 100 * count / total
            print(f"  {instr_type}: {count} ({pct:.1f}%)")
        print(f"Memory accesses: {self.memory_accesses}")
```

#### What You Should Understand After This Project
- ✅ Computer = CPU + Memory + I/O
- ✅ Fetch-decode-execute cycle is the heartbeat of computation
- ✅ Von Neumann architecture: stored-program computer
- ✅ Memory-mapped I/O: devices are memory locations
- ✅ All components built from gates ultimately execute programs
- ✅ Software and hardware meet at the instruction set
- ✅ Clock cycles → instructions → programs → applications

#### Common Pitfalls
- **Bus timing**: CPU and memory must synchronize properly
- **PC management**: Forgetting to increment PC causes infinite loops
- **Memory boundaries**: Address wrapping and out-of-bounds access
- **Instruction timing**: Some operations need multiple cycles

#### Extension Ideas
- Add interrupts (hardware can signal CPU)
- Implement DMA (direct memory access)
- Add cache simulation
- Build a multi-cycle CPU (instructions take variable time)
- Add pipelining (overlap instruction execution)
- Implement a simple OS bootloader

#### Real-World Connection
You've now built a simplified but **real** computer. Modern CPUs follow the same principles:
- **ARM Cortex-M0**: Simple embedded CPU, similar complexity
- **RISC-V**: Open-source ISA, used in real products
- **6502**: Powered Apple II, Commodore 64—comparable complexity
- Your computer could run a simple OS, games, compilers, etc.

Congratulations—you've completed the hardware phase! You understand computers from the silicon up. Next, we'll build the software stack on top of your hardware.
