### Project 3: Memory Hierarchy Simulator
**Objective**: Understand sequential logic and memory

#### Background Concepts

Up until now, we've built **combinational logic**—gates that instantly produce outputs based on inputs, with no memory. But computers need to remember things! Memory requires **sequential logic**—circuits whose outputs depend on both current inputs AND past state.

**The Clock Signal**:
All sequential logic synchronizes to a clock—a square wave that oscillates between 0 and 1. State changes happen on clock edges (rising or falling). Think of it as the computer's heartbeat.

```
Clock: _|‾|_|‾|_|‾|_|‾|_
       t0 t1 t2 t3 t4  (discrete time steps)
```

**The D Flip-Flop (DFF)**:
The fundamental memory element that stores one bit. Think of it as the smallest unit of computer memory—a single on/off switch that "remembers" its state.

**Interface**:
- Input: `data_in` (what to store)
- Output: `data_out` (current stored value)
- Behavior: On clock rising edge, `data_out ← data_in`

**Why "D" Flip-Flop?**
The "D" stands for "Data" or "Delay"—it captures the data input and delays it by exactly one clock cycle. This creates a predictable, controlled delay that's essential for building complex circuits.

**How It Works Internally** (conceptual):
```
        Clock Edge
            ↓
    [Master]─→[Slave]
       ↑          ↓
    data_in   data_out
```

When the clock rises:
1. The "master" latch captures the current input
2. The "slave" latch releases the previous stored value
3. On the next clock edge, roles swap

This two-stage design prevents "transparency"—you never see the input immediately appear at the output, which would cause chaos in circuits with feedback.

**The Timing Paradox** (and why it's brilliant):
```
Cycle | Input | Output | Internal State
------|-------|--------|---------------
  0   |   ?   |   0    | 0 (initial)
  1   |   1   |   0    | 1 (captured 1)
  2   |   1   |   1    | 1 (still holding)
  3   |   0   |   1    | 0 (captured 0)
  4   |   0   |   0    | 0 (still holding)
```

Notice: **Output lags input by one cycle**. This seems backwards, but it's the secret sauce:
- Prevents infinite feedback loops (output → combinational logic → input)
- Creates stable timing domains (everything updates simultaneously)
- Enables pipelining (each stage processes different data)

🎓 **Key insight**: The DFF breaks the "instant computation" model. It creates a delay—output reflects *previous* input. This enables feedback loops and state machines without creating timing paradoxes.

**Why This Is the ONLY Memory Primitive You Need**:
Every memory structure in a computer—from CPU registers to RAM to your hard drive—can be built by combining DFFs with combinational logic. It's the atomic unit of state storage.

**Hardware vs Simulation**:
- **Real hardware**: Built from cross-coupled NAND/NOR gates or transistor pairs
- **Our simulation**: We model the *behavior* (store and delay) without the internal complexity
- Both produce identical logical behavior at the clock edge level

#### Learning Path

**Step 1: Implement a DFF** (1 hour)
In simulation, model the clock explicitly:

```python
class DFF:
    """D Flip-Flop: 1-bit memory"""
    def __init__(self):
        self.state = 0  # Current stored bit

    def clock_cycle(self, data_in):
        """On rising edge: capture input, emit old state"""
        output = self.state  # Output is PREVIOUS state
        self.state = data_in  # Store for next cycle
        return output
```

🎓 **Timing is crucial**: The output you get is from the *previous* cycle. This seems backwards but prevents infinite loops in circuits.

Test it:
```python
dff = DFF()
print(dff.clock_cycle(1))  # 0 (initial state)
print(dff.clock_cycle(1))  # 1 (from previous input)
print(dff.clock_cycle(0))  # 1 (from previous input)
print(dff.clock_cycle(0))  # 0 (from previous input)
```

**Step 2: Build a 1-bit Register** (30 minutes)
A register adds a "load" control: only update on load=1. This transforms the DFF from "always stores new value" to "stores only when told to."

**Why We Need Load Control**:
The DFF alone has a problem—it *always* captures whatever's on its input every clock cycle. But real registers need to hold values indefinitely until explicitly updated. The load signal gives us selective control.

**Circuit Structure**:
```
    data_in ─┐
             ├─→[MUX]─→[DFF]─→ data_out
    output ──┘     ↑           |
                   |           |
                 load      feedback
                           (when load=0)
```

**Implementation**:
```python
class Bit:
    """1-bit register with load control"""
    def __init__(self):
        self.dff = DFF()

    def clock_cycle(self, data_in, load):
        """
        If load=1: store new data
        If load=0: keep old data (feedback loop!)
        """
        current_state = self.dff.state

        # MUX: select new data or old data
        to_store = data_in if load else current_state

        return self.dff.clock_cycle(to_store)
```

**How It Works—Step by Step**:

1. **Load = 1 (Write Mode)**:
   ```
   data_in(1) → MUX selects data_in → DFF stores 1
   Next cycle: output = 1
   ```

2. **Load = 0 (Hold Mode)**:
   ```
   data_in(0) → MUX selects current_state(1) → DFF stores 1
   Next cycle: output = 1 (unchanged!)
   ```

**The Feedback Loop** (Critical Concept):
When load=0, the register's output is fed back to its input through the MUX. This creates a **closed loop**:
```
[DFF output] → current_state → MUX → [DFF input]
      ↑                                    ↓
      └────────────────────────────────────┘
```

This loop is **stable** because:
- The DFF's one-cycle delay prevents instantaneous feedback
- Each cycle, the DFF stores "what it already had"
- The value persists indefinitely until load=1 breaks the loop

**Practical Example—Storing a Bit**:
```python
bit = Bit()

# Initially: state = 0
cycle 0: bit.clock_cycle(1, load=1)  → output=0, state becomes 1
cycle 1: bit.clock_cycle(0, load=0)  → output=1, state stays 1 (feedback!)
cycle 2: bit.clock_cycle(0, load=0)  → output=1, state stays 1
cycle 3: bit.clock_cycle(1, load=1)  → output=1, state becomes 1
cycle 4: bit.clock_cycle(0, load=1)  → output=1, state becomes 0
cycle 5: bit.clock_cycle(1, load=0)  → output=0, state stays 0 (feedback!)
```

🎓 **Key Insights**:
- **The feedback loop is essential for storage**: Without it, the register would only hold values for one cycle
- **The MUX is the gatekeeper**: It chooses between "new data" and "preserve old data"
- **Load signal is your "save button"**: Like hitting Ctrl+S—nothing changes until you explicitly save
- **This is your first sequential circuit with control**: You're no longer just transforming data, you're controlling *when* transformations happen

**Why This Pattern Matters**:
Every memory element in a computer uses this pattern:
- CPU registers: "Load this value into register AX"
- RAM cells: "Write to this address" vs "just reading, don't change"
- Cache lines: "Update on cache miss" vs "hold current data"

The 1-bit register is the building block. Everything else is just more sophisticated control logic around this same core idea.

**Step 3: Build a 16-bit Register** (30 minutes)
Now we scale from 1 bit to 16 bits—creating a real CPU register that can store a complete value.

**Conceptual Architecture**:
```
data_in[0] ──→ [Bit 0]  ──→ data_out[0]
data_in[1] ──→ [Bit 1]  ──→ data_out[1]
data_in[2] ──→ [Bit 2]  ──→ data_out[2]
    ...          ...           ...
data_in[15] ─→ [Bit 15] ──→ data_out[15]
                  ↓
            load (shared)
            clock (shared)
```

**Key Design Principle**: All 16 bits operate **in parallel**, synchronized by:
- **Shared load signal**: One control line enables/disables all bits simultaneously
- **Shared clock**: All bits update on the same clock edge
- **Independent data**: Each bit stores its own value independently

**Implementation**:
```python
class Register:
    """16-bit register"""
    def __init__(self):
        self.bits = [Bit() for _ in range(16)]

    def clock_cycle(self, data_in, load):
        """data_in: 16-bit value, load: single control bit"""
        return [
            self.bits[i].clock_cycle(data_in[i], load)
            for i in range(16)
        ]
```

**Why This Design Works**:

1. **Parallelism**: All 16 bits process simultaneously—no sequential iteration in hardware
   - Bit 0 doesn't wait for bit 15
   - All updates happen on the same clock edge
   - This is true parallel execution, not a loop

2. **Single Control**: One load signal controls all 16 bits
   - You can't load just some bits—it's all or nothing
   - This matches real CPU registers (you can't half-update a register)
   - Simplifies control logic

3. **Data Format**: Input/output as bit lists `[b0, b1, ..., b15]`
   - LSB (Least Significant Bit) at index 0
   - MSB (Most Significant Bit) at index 15
   - Example: `5` = `0b0101` = `[1, 0, 1, 0, 0, 0, ..., 0]`

**Practical Example—Storing a 16-bit Value**:
```python
register = Register()

# Write 0x1234 (hex) = 4660 (decimal) = 0001 0010 0011 0100 (binary)
# As bit list (LSB first): [0,0,1,0,1,1,0,0,0,1,0,0,1,0,0,0]
bits = [0,0,1,0,1,1,0,0,0,1,0,0,1,0,0,0]

# Cycle 1: Write value
output = register.clock_cycle(bits, load=1)
# output = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]  (initial state)

# Cycle 2: Read back
output = register.clock_cycle([0]*16, load=0)
# output = [0,0,1,0,1,1,0,0,0,1,0,0,1,0,0,0]  (stored value!)

# The register now holds 0x1234 indefinitely (until load=1 again)
```

**Comparison: 1-bit vs 16-bit Register**:

| Aspect | 1-bit Register | 16-bit Register |
|--------|---------------|-----------------|
| **Storage** | 1 bit (0 or 1) | 16 bits (0x0000 to 0xFFFF) |
| **Components** | 1 DFF + 1 MUX | 16 DFFs + 16 MUXes |
| **Load signal** | Controls 1 bit | Controls all 16 bits |
| **Data I/O** | Single bit | List of 16 bits |
| **Use case** | Building block | CPU register, address storage |

🎓 **Key Insights**:
- **This IS a CPU register**: When you write `MOV AX, 5` in assembly, AX is a 16-bit register like this
- **Width is arbitrary**: 8-bit, 32-bit, 64-bit registers use the same pattern, just more bits
- **No new concepts**: It's just parallel composition of identical units
- **Hardware efficiency**: Real registers use this exact architecture—parallel is fast

**What Makes This "Parallel"?**
In simulation, we use a list comprehension that *looks* sequential:
```python
return [self.bits[i].clock_cycle(...) for i in range(16)]
```

But in **actual hardware**, all 16 operations happen simultaneously:
- All 16 MUXes decide at the same instant
- All 16 DFFs capture on the same clock edge
- The entire 16-bit value updates in one clock cycle

This is the difference between **modeling** (which may use loops) and **hardware reality** (which is truly parallel).

**Testing Your Register**:
```python
# Test 1: Write and hold
register.clock_cycle([1]*16, load=1)  # Write all 1s (0xFFFF)
for _ in range(100):
    output = register.clock_cycle([0]*16, load=0)
    assert output == [1]*16  # Value persists

# Test 2: Overwrite
register.clock_cycle([0]*16, load=1)  # Write all 0s
output = register.clock_cycle([1]*16, load=0)
assert output == [0]*16  # Old value was overwritten

# Test 3: Load control
register.clock_cycle([1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0], load=1)
register.clock_cycle([0]*16, load=0)  # Try to write 0s with load=0
output = register.clock_cycle([0]*16, load=0)
assert output == [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]  # Unchanged!
```

**Step 4: Build RAM (8 registers)** (2 hours)
Now we scale from one register to multiple registers—introducing **addressable memory**. This is the conceptual leap from "a register" to "RAM".

**The Challenge**: We have 8 registers, but we can only read/write one at a time. How do we choose which one?

**Solution**: Add an **address** input that selects which register to access.

**Conceptual Architecture**:
```
                    ┌─────────────┐
data_in ───────────→│             │
address ───────────→│   Address   │
load ──────────────→│   Decoder   │
                    │             │
                    └──────┬──────┘
                           │ (control signals)
         ┌─────────────────┼─────────────────┐
         │        │        │        │         │
    ┌────▼───┐ ┌─▼──────┐ │  ...  ┌▼────────┐
    │ Reg 0  │ │ Reg 1  │ │       │ Reg 7   │
    └────┬───┘ └─┬──────┘ │       └┬────────┘
         │        │        │        │
         └────────┴────────┴────────┘
                  │
                  ▼ (output mux)
              data_out
```

**Implementation**:
```python
class RAM8:
    """8 registers, 3-bit address"""
    def __init__(self):
        self.registers = [Register() for _ in range(8)]

    def clock_cycle(self, data_in, address, load):
        """
        address: 3 bits (0-7)
        load: write enable
        Returns: data from addressed register
        """
        # Decode address: only one register gets load=1
        outputs = []
        for i in range(8):
            reg_load = (load == 1 and address == i)
            out = self.registers[i].clock_cycle(data_in, reg_load)
            outputs.append(out)

        # Output from selected register
        return outputs[address]
```

**How Address Decoding Works**:

The address decoder is like a railway switch—it routes the load signal to exactly one register:

```
Address = 0:  load → Register 0,  others get 0
Address = 1:  load → Register 1,  others get 0
Address = 2:  load → Register 2,  others get 0
...
Address = 7:  load → Register 7,  others get 0
```

**Why 3 bits for 8 registers?**
- 3 bits can represent 2³ = 8 different values (0-7)
- Each address uniquely identifies one register
- General rule: n bits → 2ⁿ addressable locations

**Step-by-Step Operation**:

1. **Write Operation** (load=1):
   ```python
   # Write value 0x1234 to address 3
   ram.clock_cycle(bits_1234, address=3, load=1)

   # What happens internally:
   # - Reg 0: gets load=0 → holds old value
   # - Reg 1: gets load=0 → holds old value
   # - Reg 2: gets load=0 → holds old value
   # - Reg 3: gets load=1 → stores 0x1234  ← ONLY THIS ONE
   # - Reg 4-7: get load=0 → hold old values
   ```

2. **Read Operation** (load=0):
   ```python
   # Read from address 3
   output = ram.clock_cycle(zeros, address=3, load=0)

   # What happens internally:
   # - All registers get load=0 → all hold their values
   # - Address decoder selects outputs[3]
   # - Return value from Register 3
   ```

**Practical Example—Using RAM**:
```python
ram = RAM8()

# Cycle 1: Write 0xAAAA to address 0
ram.clock_cycle(int_to_bits(0xAAAA), address=0, load=1)

# Cycle 2: Write 0xBBBB to address 1
ram.clock_cycle(int_to_bits(0xBBBB), address=1, load=1)

# Cycle 3: Write 0xCCCC to address 7
ram.clock_cycle(int_to_bits(0xCCCC), address=7, load=1)

# Cycle 4: Read from address 0 (should get 0xAAAA)
output = ram.clock_cycle([0]*16, address=0, load=0)
assert bits_to_int(output) == 0xAAAA

# Cycle 5: Read from address 1 (should get 0xBBBB)
output = ram.clock_cycle([0]*16, address=1, load=0)
assert bits_to_int(output) == 0xBBBB

# All three values are stored simultaneously!
# This is your first real memory system.
```

🎓 **Key Concepts**:

1. **Address Decoding** (Demultiplexing):
   - Takes one control signal (load) and routes it to one of many destinations
   - Implementation: `reg_load = (load == 1 and address == i)`
   - Only the register matching the address gets load=1

2. **Output Multiplexing**:
   - All registers output their values every cycle
   - We collect all outputs, then select one based on address
   - Implementation: `return outputs[address]`

3. **Memory Isolation**:
   - Writing to address 3 doesn't affect addresses 0-2 or 4-7
   - Each register maintains independent state
   - Critical for data integrity

**Why All Registers Clock Every Cycle?**

You might wonder: "Why clock all 8 registers if we're only accessing one?"

- **Reason 1**: All registers share the same clock (it's a global signal)
- **Reason 2**: Hardware doesn't "skip" components—everything runs in parallel
- **Reason 3**: The load signal controls whether they *store* new data
- **Efficiency**: In real hardware, this is actually more efficient than selective clocking

Think of it like this: The clock is a heartbeat. Every register "beats" at the same time, but the load signal controls whether they "remember" anything new.

**Memory Map View**:
```
Address | Value (hex) | Purpose
--------|-------------|--------
   0    |   0xAAAA    | Data we wrote
   1    |   0xBBBB    | Data we wrote
   2    |   0x0000    | Uninitialized
   3    |   0x0000    | Uninitialized
   4    |   0x0000    | Uninitialized
   5    |   0x0000    | Uninitialized
   6    |   0x0000    | Uninitialized
   7    |   0xCCCC    | Data we wrote
```

**Real-World Connection**:
- This is exactly how CPU register files work (AX, BX, CX, DX in x86)
- Assembly: `MOV [address], value` uses address decoding
- Your computer's RAM uses the same principle, scaled to billions of addresses

**Step 5: Build Larger RAMs (64, 512, 4K)** (1 hour)
Now we scale from 8 registers to 64+ using **hierarchical composition**—the same technique used in real memory chips. Instead of building RAM64 with 64 individual registers, we build it from 8 RAM8 units.

**Why Hierarchical Design?**

The naive approach would be:
```python
# DON'T DO THIS (doesn't scale well)
class RAM64_Flat:
    def __init__(self):
        self.registers = [Register() for _ in range(64)]  # 64 individual registers
```

Problems:
- **Address decoder complexity**: 64-way decision logic is complex in hardware
- **Signal routing**: 64 parallel outputs to multiplex
- **Design reuse**: Can't leverage existing tested RAM8 design
- **Doesn't match hardware**: Real chips use hierarchical banks

**The Hierarchical Approach**:
```
RAM64 (64 registers total)
  ├── RAM8 Bank 0 (registers 0-7)
  ├── RAM8 Bank 1 (registers 8-15)
  ├── RAM8 Bank 2 (registers 16-23)
  ├── RAM8 Bank 3 (registers 24-31)
  ├── RAM8 Bank 4 (registers 32-39)
  ├── RAM8 Bank 5 (registers 40-47)
  ├── RAM8 Bank 6 (registers 48-55)
  └── RAM8 Bank 7 (registers 56-63)
```

**Address Space Division**:
A 6-bit address (000000 to 111111 in binary) naturally divides into two parts:

```
6-bit address:  [BBB][RRR]
                 │    └─→ Register select (3 bits) → which register in the bank (0-7)
                 └──────→ Bank select (3 bits) → which RAM8 bank (0-7)

Example: Address 19 (decimal) = 010011 (binary)
         [010][011]
          │    └─→ Register 3 within the bank
          └──────→ Bank 2

So address 19 → Bank 2, Register 3
```

**Implementation**:
```python
class RAM64:
    """64 registers using 8x RAM8, 6-bit address"""
    def __init__(self):
        self.banks = [RAM8() for _ in range(8)]

    def clock_cycle(self, data_in, address, load):
        """
        address: 6 bits
        - High 3 bits select which RAM8 bank
        - Low 3 bits select register within bank
        """
        bank_select = address >> 3  # Top 3 bits (divide by 8)
        register_select = address & 0b111  # Bottom 3 bits (modulo 8)

        # Clock all banks, but only selected bank gets load=1
        outputs = []
        for i in range(8):
            bank_load = (load == 1 and bank_select == i)
            out = self.banks[i].clock_cycle(
                data_in, register_select, bank_load
            )
            outputs.append(out)

        # Return output from selected bank
        return outputs[bank_select]
```

**Step-by-Step Operation Example**:

```python
# Write 0x1234 to address 19
ram64 = RAM64()
ram64.clock_cycle(bits_1234, address=19, load=1)

# What happens internally:
# 1. Address decoding:
#    - address = 19 = 0b010011
#    - bank_select = 19 >> 3 = 2 (top 3 bits = 010)
#    - register_select = 19 & 0b111 = 3 (bottom 3 bits = 011)
#
# 2. Bank activation:
#    - Bank 0: bank_load=0, register_select=3 → holds old values
#    - Bank 1: bank_load=0, register_select=3 → holds old values
#    - Bank 2: bank_load=1, register_select=3 → WRITES 0x1234 to register 3
#    - Bank 3-7: bank_load=0, register_select=3 → hold old values
#
# 3. Output selection:
#    - All banks return their outputs
#    - We select outputs[2] (from Bank 2)
#    - This gives us the value from Bank 2, Register 3
```

**Address Decoding Deep Dive**:

The bit manipulation is critical:
```python
# Right shift (>>) extracts high bits
address = 0b010011  # 19
bank_select = address >> 3  # Shift right 3 positions
# 010011 → 000010 = 2

# Bitwise AND with mask extracts low bits
register_select = address & 0b111  # Keep only bottom 3 bits
# 010011 & 000111 = 000011 = 3
```

**Why This Works**:
- **Binary math**: In binary, dividing by 8 (2³) is the same as shifting right 3 bits
- **Masking**: AND with 0b111 keeps only the rightmost 3 bits (0-7 range)
- **Complete coverage**: Every 6-bit address maps to exactly one (bank, register) pair
- **No gaps**: Addresses 0-63 all map to valid locations

**Memory Map View**:
```
Address (decimal) | Binary    | Bank | Register | Description
------------------|-----------|------|----------|------------
       0          | 000 000   |  0   |    0     | Bank 0, Reg 0
       1          | 000 001   |  0   |    1     | Bank 0, Reg 1
       7          | 000 111   |  0   |    7     | Bank 0, Reg 7
       8          | 001 000   |  1   |    0     | Bank 1, Reg 0
      19          | 010 011   |  2   |    3     | Bank 2, Reg 3  ← Our example
      63          | 111 111   |  7   |    7     | Bank 7, Reg 7
```

**Scaling Up—Continue the Pattern**:

Once you have RAM64, building larger memories follows the same recursive pattern:

**RAM512** (512 registers = 8 × RAM64):
```python
class RAM512:
    """512 registers using 8x RAM64, 9-bit address"""
    def __init__(self):
        self.banks = [RAM64() for _ in range(8)]

    def clock_cycle(self, data_in, address, load):
        # 9-bit address: [BBB][RRRRRR]
        #   High 3 bits → which RAM64 bank (0-7)
        #   Low 6 bits → which register within that RAM64 (0-63)
        bank_select = address >> 6  # Top 3 bits
        register_select = address & 0b111111  # Bottom 6 bits

        outputs = []
        for i in range(8):
            bank_load = (load == 1 and bank_select == i)
            out = self.banks[i].clock_cycle(
                data_in, register_select, bank_load
            )
            outputs.append(out)

        return outputs[bank_select]
```

**RAM4K** (4096 registers = 8 × RAM512):
```python
class RAM4K:
    """4096 registers using 8x RAM512, 12-bit address"""
    def __init__(self):
        self.banks = [RAM512() for _ in range(8)]

    def clock_cycle(self, data_in, address, load):
        # 12-bit address: [BBB][RRRRRRRRR]
        #   High 3 bits → which RAM512 bank (0-7)
        #   Low 9 bits → which register within that RAM512 (0-511)
        bank_select = address >> 9  # Top 3 bits
        register_select = address & 0b111111111  # Bottom 9 bits

        outputs = []
        for i in range(8):
            bank_load = (load == 1 and bank_select == i)
            out = self.banks[i].clock_cycle(
                data_in, register_select, bank_load
            )
            outputs.append(out)

        return outputs[bank_select]
```

**RAM16K** (16384 registers = 4 × RAM4K):
```python
class RAM16K:
    """16K registers using 4x RAM4K, 14-bit address"""
    def __init__(self):
        self.banks = [RAM4K() for _ in range(4)]

    def clock_cycle(self, data_in, address, load):
        # 14-bit address: [BB][RRRRRRRRRRRR]
        #   High 2 bits → which RAM4K bank (0-3)
        #   Low 12 bits → which register within that RAM4K (0-4095)
        bank_select = address >> 12  # Top 2 bits
        register_select = address & 0b111111111111  # Bottom 12 bits

        outputs = []
        for i in range(4):
            bank_load = (load == 1 and bank_select == i)
            out = self.banks[i].clock_cycle(
                data_in, register_select, bank_load
            )
            outputs.append(out)

        return outputs[bank_select]
```

**Hierarchical Memory Tree**:
```
RAM16K (16,384 registers)
 ├── RAM4K Bank 0 (4,096 registers)
 │    ├── RAM512 Bank 0 (512 registers)
 │    │    ├── RAM64 Bank 0 (64 registers)
 │    │    │    ├── RAM8 Bank 0 (8 registers)
 │    │    │    │    ├── Register 0
 │    │    │    │    ├── Register 1
 │    │    │    │    └── ... (8 total)
 │    │    │    └── ... (8 RAM8 banks)
 │    │    └── ... (8 RAM64 banks)
 │    └── ... (8 RAM512 banks)
 └── ... (4 RAM4K banks)
```

**Address Decoding Depth**:

For RAM16K with address 12345:
```
Address 12345 (decimal) = 11000000111001 (binary, 14 bits)

Level 1 (RAM16K):
  [11][000000111001]
   │         └─→ Pass 000000111001 (3129) to selected RAM4K
   └─→ Bank 3

Level 2 (RAM4K Bank 3):
  [000][000111001]
    │       └─→ Pass 000111001 (57) to selected RAM512
    └─→ Bank 0

Level 3 (RAM512 Bank 0):
  [000][111001]
    │      └─→ Pass 111001 (57) to selected RAM64
    └─→ Bank 0

Level 4 (RAM64 Bank 0):
  [111][001]
   │     └─→ Pass 001 (1) to selected RAM8
   └─→ Bank 7

Level 5 (RAM8 Bank 7):
  Register 1 ← FINAL LOCATION
```

So address 12345 maps to: **RAM4K[3] → RAM512[0] → RAM64[0] → RAM8[7] → Register[1]**

🎓 **Key Insights**:

1. **Logarithmic Decoding Depth**: To access 16K registers, we only need 5 levels of hierarchy
   - Flat design would need to decode 1 of 16,384 choices
   - Hierarchical design decodes 1 of 4, then 1 of 8, then 1 of 8, etc.
   - Much simpler hardware

2. **Address Bit Allocation**:
   - Each level "consumes" some bits from the address
   - RAM16K: 2 bits for bank selection, passes 12 bits down
   - RAM4K: 3 bits for bank selection, passes 9 bits down
   - RAM512: 3 bits for bank selection, passes 6 bits down
   - RAM64: 3 bits for bank selection, passes 3 bits down
   - RAM8: 3 bits for register selection (final)
   - Total: 2 + 3 + 3 + 3 + 3 = 14 bits (2¹⁴ = 16,384 addresses ✓)

3. **Design Reuse**: Each level uses the same pattern—8 (or 4) banks of the next smaller unit
   - Testable at each level
   - Debuggable incrementally
   - Matches real hardware architecture

4. **Signal Propagation**:
   - Data flows DOWN: from RAM16K → RAM4K → RAM512 → RAM64 → RAM8 → Register
   - Control (load) flows DOWN: Only one path gets load=1 at each level
   - Output flows UP: Selected register → RAM8 → RAM64 → RAM512 → RAM4K → RAM16K

**Real-World Connection**:

Modern memory chips use this exact architecture:
- **DDR4 DIMM**: Multiple ranks → multiple banks → row/column addressing
- **SSD**: Multiple dies → multiple planes → multiple blocks → multiple pages
- **Cache**: L3 → L2 → L1 → Cache lines → Bytes

**Testing Hierarchical Memory**:
```python
def test_ram16k_hierarchy():
    """Verify hierarchical addressing works correctly"""
    ram = RAM16K()

    # Test addresses at different hierarchy levels
    test_addresses = [
        0,       # Bank 0, all zeros
        4095,    # Bank 0, max address in first RAM4K
        4096,    # Bank 1, first address in second RAM4K
        8192,    # Bank 2, first address
        12288,   # Bank 3, first address
        16383    # Bank 3, max address (all ones)
    ]

    # Write unique values
    for addr in test_addresses:
        value = addr * 2
        ram.clock_cycle(to_binary(value, 16), addr, load=1)

    # Read back and verify
    for addr in test_addresses:
        expected = addr * 2
        result = ram.clock_cycle([0]*16, addr, load=0)
        assert to_decimal(result) == expected, f"Address {addr} failed"
```

**Performance Implications**:

In real hardware:
- **Access latency**: Each level adds gate delays (nanoseconds)
- **Parallelism**: All banks can be pre-charged in parallel
- **Power efficiency**: Only active banks consume power
- **Scalability**: Can scale to gigabytes using the same pattern

**Step 6: Implement Program Counter (PC)** (1.5 hours)
The Program Counter is the most important register in a computer—it controls **what happens next**. While RAM stores data, the PC stores the address of the next instruction to execute.

**What Makes the PC Special?**

Unlike a normal register that just holds a value, the PC needs to:
1. **Increment automatically** (most common: move to next instruction)
2. **Jump to a new address** (for function calls, loops, conditionals)
3. **Reset to zero** (on system boot or reset)
4. **Hold current value** (when processor is paused/waiting)

**The Control Flow Problem**:

Consider this simple program:
```
Address | Instruction
--------|------------
   0    | LOAD 5
   1    | ADD 3
   2    | STORE result
   3    | JUMP 10
   4    | ...never executed...
  10    | HALT
```

The PC must:
- Start at 0
- Increment to 1, then 2, then 3 (sequential execution)
- Jump to 10 when it sees JUMP instruction (breaking sequential flow)
- Stop at 10

**PC Architecture**:

```
              ┌────────────────────────────┐
              │    Control Logic (MUX)     │
              │                            │
  reset ─────→│  if reset: 0               │
  load ──────→│  elif load: data_in        │←── data_in (jump address)
  inc ───────→│  elif inc: current + 1     │
              │  else: current (hold)      │
              │                            │
              └──────────┬─────────────────┘
                         │
                    ┌────▼────┐
                    │ Register│
                    │ (DFF)   │
                    └────┬────┘
                         │
                      current ──→ output (next instruction address)
                         │
                         └───────┘ (feedback for increment)
```

**Implementation**:
```python
class PC:
    """Program Counter: tracks next instruction address"""
    def __init__(self):
        self.register = Register()  # 16-bit register for storage
        self.current = [0] * 16     # Track current value for increment

    def clock_cycle(self, data_in, load, inc, reset):
        """
        Priority: reset > load > inc > hold

        reset=1: Go to address 0 (system boot/reset)
        load=1:  Go to data_in address (jump/branch)
        inc=1:   Go to next address (sequential execution)
        else:    Stay at current address (hold/wait)
        """
        if reset:
            next_val = [0] * 16
        elif load:
            next_val = data_in
        elif inc:
            one = [1] + [0] * 15  # Binary representation of 1
            next_val, _ = add16(self.current, one)
        else:
            next_val = self.current

        # Always store the computed next value
        self.current = self.register.clock_cycle(next_val, load=1)
        return self.current
```

**Control Signal Priority—Critical Design Decision**:

The `if-elif-else` chain implements **priority logic**. Why does order matter?

```python
# CORRECT: reset > load > inc > hold
if reset:        # Highest priority: system boot/panic
elif load:       # Jump/branch instruction
elif inc:        # Normal sequential execution
else:            # Processor paused

# WRONG: Different priority could break the system
if inc:          # Would always increment, even during reset!
elif reset:      # Reset would never happen if inc=1
```

**Priority Justification**:
1. **Reset must be highest**: If the system crashes, you need to be able to restart regardless of other signals
2. **Load before inc**: When jumping, you don't want to accidentally increment first
3. **Inc before hold**: When executing normally, increment is the default action
4. **Hold is lowest**: Only when explicitly doing nothing

**Step-by-Step Operation Examples**:

**Example 1: Sequential Execution (inc=1)**
```python
pc = PC()

# Boot: Reset to 0
cycle 0: output = pc.clock_cycle([0]*16, load=0, inc=0, reset=1)
         # output = [0,0,0,...,0] (address 0)

# Execute instructions sequentially
cycle 1: output = pc.clock_cycle([0]*16, load=0, inc=1, reset=0)
         # output = [1,0,0,...,0] (address 1)
         # current was 0, so next = 0 + 1 = 1

cycle 2: output = pc.clock_cycle([0]*16, load=0, inc=1, reset=0)
         # output = [0,1,0,...,0] (address 2)
         # current was 1, so next = 1 + 1 = 2

cycle 3: output = pc.clock_cycle([0]*16, load=0, inc=1, reset=0)
         # output = [1,1,0,...,0] (address 3)
         # current was 2, so next = 2 + 1 = 3
```

This is **sequential execution**—the normal flow of a program.

**Example 2: Jump (load=1)**
```python
# Currently at address 5, need to jump to address 100
current_address = 5
jump_target = 100  # 0b0000000001100100 in binary

cycle N: output = pc.clock_cycle(to_binary(100, 16), load=1, inc=0, reset=0)
         # output = [0,0,1,0,0,1,1,0,0,...,0] (address 100)
         # Ignores current value, loads jump_target directly

# Next cycle continues from 100
cycle N+1: output = pc.clock_cycle([0]*16, load=0, inc=1, reset=0)
           # output = address 101 (100 + 1)
```

This is **control flow transfer**—used for:
- Function calls: `CALL function_address`
- Loops: `JUMP loop_start`
- Conditionals: `IF condition THEN JUMP else_address`

**Example 3: Reset (reset=1)**
```python
# Currently at address 9999, system crashes
crash_address = 9999

cycle X: output = pc.clock_cycle([0]*16, load=1, inc=1, reset=1)
         # output = [0,0,0,...,0] (address 0)
         # reset=1 overrides ALL other signals (load=1 and inc=1 ignored)

# System reboots from address 0
cycle X+1: output = pc.clock_cycle([0]*16, load=0, inc=1, reset=0)
           # output = address 1
```

This is **system recovery**—back to known good state.

**Example 4: Hold (all signals = 0)**
```python
# Currently at address 42, processor needs to wait for memory
current_address = 42

cycle K: output = pc.clock_cycle([0]*16, load=0, inc=0, reset=0)
         # output = [0,1,0,1,0,1,0,0,...,0] (address 42, unchanged)
         # Feedback loop: current → current

cycle K+1: output = pc.clock_cycle([0]*16, load=0, inc=0, reset=0)
           # output = address 42 (still unchanged)
```

This is **stall/wait state**—used when:
- Memory isn't ready yet
- Waiting for I/O operation
- Processor is in low-power mode
- Debugging (breakpoint hit)

**The Increment Operation—Deep Dive**:

Incrementing seems simple, but it requires:
1. An adder circuit (from previous project!)
2. Feedback from register output to adder input
3. Constant "1" as the other adder input

```python
# Increment logic breakdown
inc = True
current = [0, 1, 0, 1]  # Binary: 0b0101 = 5 decimal

# Create constant 1 in binary (LSB first)
one = [1, 0, 0, 0]  # Binary: 0b0001 = 1 decimal

# Use 16-bit adder from Project 2
next_val, carry = add16(current, one)
# next_val = [1, 1, 0, 1] = 0b0110 = 6 decimal
```

**Why Feedback?**
The PC creates a feedback loop:
```
┌──────────────────┐
│   Register       │
│   current = N    │
└─────┬────────────┘
      │ (output)
      ↓
   ┌──▼─────┐
   │ Adder  │
   │ N + 1  │
   └──┬─────┘
      │
      ↓ (next value)
┌─────▼────────────┐
│   Register       │
│   current = N+1  │
└──────────────────┘
```

Without feedback, the register couldn't increment itself—it would just store whatever external value you gave it.

**Overflow Behavior**:

What happens when PC = 0xFFFF (65535) and you increment?
```python
pc = PC()
# Set PC to maximum value
pc.current = [1] * 16  # 0xFFFF = 65535

# Increment
output = pc.clock_cycle([0]*16, load=0, inc=1, reset=0)
# output = [0,0,0,...,0]  # Wraps around to 0!

# Why? 16-bit adder discards the carry bit
# 0xFFFF + 1 = 0x10000, but we only keep 16 bits → 0x0000
```

In real computers:
- Some architectures trap this as an error
- Some allow wrapping (modular arithmetic)
- Some have special handling for instruction fetch past memory end

**Real-World PC Variations**:

**x86 Architecture** (Instruction Pointer):
- 64-bit on modern CPUs (can address massive memory)
- Increments by instruction length (1-15 bytes, variable)
- Called RIP (64-bit), EIP (32-bit), or IP (16-bit)

**ARM Architecture** (Program Counter):
- Called R15 or PC
- Always increments by 4 (ARM instructions are 4 bytes)
- Special behavior: reading PC gives current + 8 (pipeline artifact)

**RISC-V Architecture**:
- Called PC (no register number, implicit)
- Increments by 4 for normal instructions
- Increments by 2 for compressed instructions (16-bit)

**Simulating a Simple Program**:

```python
def simulate_program():
    """Simulate a simple program with PC"""
    pc = PC()
    ram = RAM16K()

    # Load program into RAM
    # Address 0: LOAD 5 (load constant 5)
    # Address 1: ADD 3 (add constant 3)
    # Address 2: STORE 100 (store to address 100)
    # Address 3: JUMP 10 (jump to address 10)
    # Address 10: HALT (stop)

    instructions = [
        ("LOAD", 5),
        ("ADD", 3),
        ("STORE", 100),
        ("JUMP", 10),
        None, None, None, None, None, None,  # addresses 4-9 (unused)
        ("HALT",),
    ]

    # Execution simulation
    print("Cycle | PC | Instruction | Action")
    print("------|-----|-------------|-------")

    # Reset
    pc_value = pc.clock_cycle([0]*16, load=0, inc=0, reset=1)
    print(f"  0   |  0  | RESET       | PC = 0")

    # Cycle 1: Fetch from address 0
    pc_value = pc.clock_cycle([0]*16, load=0, inc=1, reset=0)
    addr = bits_to_int(pc_value)
    print(f"  1   |  0  | LOAD 5      | PC = {addr}")

    # Cycle 2: Fetch from address 1
    pc_value = pc.clock_cycle([0]*16, load=0, inc=1, reset=0)
    addr = bits_to_int(pc_value)
    print(f"  2   |  1  | ADD 3       | PC = {addr}")

    # Cycle 3: Fetch from address 2
    pc_value = pc.clock_cycle([0]*16, load=0, inc=1, reset=0)
    addr = bits_to_int(pc_value)
    print(f"  3   |  2  | STORE 100   | PC = {addr}")

    # Cycle 4: Fetch from address 3, execute JUMP
    jump_addr = to_binary(10, 16)
    pc_value = pc.clock_cycle(jump_addr, load=1, inc=0, reset=0)
    addr = bits_to_int(pc_value)
    print(f"  4   |  3  | JUMP 10     | PC = {addr} (JUMPED!)")

    # Cycle 5: Fetch from address 10
    pc_value = pc.clock_cycle([0]*16, load=0, inc=1, reset=0)
    addr = bits_to_int(pc_value)
    print(f"  5   | 10  | HALT        | PC = {addr}")

    print("\nProgram executed successfully!")
    print("Notice: Addresses 4-9 were skipped due to JUMP")

# Output:
# Cycle | PC | Instruction | Action
# ------|-----|-------------|-------
#   0   |  0  | RESET       | PC = 0
#   1   |  0  | LOAD 5      | PC = 1
#   2   |  1  | ADD 3       | PC = 2
#   3   |  2  | STORE 100   | PC = 3
#   4   |  3  | JUMP 10     | PC = 10 (JUMPED!)
#   5   | 10  | HALT        | PC = 11
#
# Program executed successfully!
# Notice: Addresses 4-9 were skipped due to JUMP
```

🎓 **Key Insights**:

1. **The PC Defines Execution Order**: Without a PC, you can't have a stored program computer
   - Von Neumann architecture depends on this
   - Instructions are data stored in memory
   - PC tells you which instruction is "active"

2. **Three Types of Control Flow**:
   - **Sequential** (inc=1): Normal execution, instruction after instruction
   - **Jump** (load=1): Unconditional change (GOTO, CALL, RETURN)
   - **Conditional jump**: Compute jump target, then load=1 only if condition met

3. **Timing is Critical**: PC must update **after** current instruction executes
   - Fetch cycle: Use current PC to read instruction from memory
   - Execute cycle: Perform instruction operation
   - Update cycle: Increment or jump to next PC
   - This is the **fetch-decode-execute cycle**

4. **PC Enables Loops**: Without being able to jump backwards, you couldn't repeat code
   ```
   Address 0: LOAD counter
   Address 1: DEC (decrement)
   Address 2: JUMP_IF_NOT_ZERO 0  ← PC can go backwards!
   Address 3: HALT
   ```

5. **Reset is Essential**: Every computer needs a defined starting state
   - x86: Starts at 0xFFFFFFF0 (near end of address space, BIOS ROM)
   - ARM: Starts at 0x00000000 (beginning of memory)
   - Our design: Starts at 0x0000 (simplest approach)

**Why Always `load=1` to Internal Register?**

Notice this line in the implementation:
```python
self.current = self.register.clock_cycle(next_val, load=1)
```

The internal register **always** has `load=1` because:
- The MUX before it already selected what to store (`next_val`)
- We always want to capture the decision made by control logic
- The PC's external control signals (reset/load/inc) already determined `next_val`
- This is different from a general register where load comes from outside

**Testing the PC**:
```python
def test_pc_priority():
    """Verify control signal priority works correctly"""
    pc = PC()

    # Test reset priority
    pc.clock_cycle(to_binary(999, 16), load=1, inc=1, reset=1)
    assert bits_to_int(pc.current) == 0  # Reset wins

    # Test load priority over inc
    pc.clock_cycle(to_binary(50, 16), load=1, inc=1, reset=0)
    assert bits_to_int(pc.current) == 50  # Load wins

    # Test increment
    pc.clock_cycle([0]*16, load=0, inc=1, reset=0)
    assert bits_to_int(pc.current) == 51  # Incremented

    # Test hold
    pc.clock_cycle(to_binary(999, 16), load=0, inc=0, reset=0)
    assert bits_to_int(pc.current) == 51  # Unchanged (hold wins)

def test_pc_increment_sequence():
    """Verify sequential execution"""
    pc = PC()
    pc.clock_cycle([0]*16, load=0, inc=0, reset=1)  # Start at 0

    for expected in range(1, 100):
        result = pc.clock_cycle([0]*16, load=0, inc=1, reset=0)
        assert bits_to_int(result) == expected

def test_pc_jump_and_continue():
    """Verify jump breaks sequence, then resumes"""
    pc = PC()
    pc.clock_cycle([0]*16, load=0, inc=0, reset=1)  # PC = 0

    # Increment to 5
    for _ in range(5):
        pc.clock_cycle([0]*16, load=0, inc=1, reset=0)
    assert bits_to_int(pc.current) == 5

    # Jump to 1000
    pc.clock_cycle(to_binary(1000, 16), load=1, inc=0, reset=0)
    assert bits_to_int(pc.current) == 1000

    # Continue incrementing from 1000
    pc.clock_cycle([0]*16, load=0, inc=1, reset=0)
    assert bits_to_int(pc.current) == 1001
```

**Real-World Connection**:

The PC is why your computer can:
- Run loops (jump backwards in program)
- Call functions (save current PC, jump to function, return to saved PC)
- Make decisions (if-then-else: conditionally jump past code)
- Recover from crashes (reset PC to bootloader address)

When you see assembly like:
```assembly
    MOV AX, 5      ; PC = 0
    ADD AX, 3      ; PC = 2
    JMP label      ; PC = 10 (jumps to label)
    ...            ; PC = 4-9 skipped
label:
    HALT           ; PC = 10
```

The PC is what makes that `JMP` instruction work—it's the hardware that implements control flow.

**Step 7: Visualize Memory State** (2 hours)
Create a timeline view:

```
Cycle | PC  | RAM[0] | RAM[1] | RAM[2] | Operation
------|-----|--------|--------|--------|----------
  0   |  0  |   0    |   0    |   0    | reset
  1   |  1  |   5    |   0    |   0    | write 5 to RAM[0]
  2   |  2  |   5    |   3    |   0    | write 3 to RAM[1]
  3   |  3  |   5    |   3    |   8    | write 8 to RAM[2]
  4   |  4  |   5    |   3    |   8    | PC increment
```

Add features:
- Highlight changed values
- Show address decoding (which bank/register selected)
- Trace signal flow during read/write
- Display as memory map (address → value table)

**Step 8: Build a Complete Test Suite** (1.5 hours)
Test patterns:
1. **Write-then-Read**: Write to every address, read back, verify
2. **Pattern Fill**: Fill memory with known pattern (0xAAAA, 0x5555)
3. **Adjacent Access**: Write adjacent addresses, ensure no interference
4. **Random Access**: Randomized read/write sequence
5. **PC Sequence**: Reset, increment x10, load, reset, verify

Example test:
```python
def test_ram_isolation():
    """Verify writing to one address doesn't affect others"""
    ram = RAM64()

    # Write unique value to each location
    for addr in range(64):
        ram.clock_cycle(
            to_binary(addr * 100, 16), addr, load=1
        )

    # Read back and verify
    for addr in range(64):
        result = ram.clock_cycle([0]*16, addr, load=0)
        assert to_decimal(result) == addr * 100
```

#### What You Should Understand After This Project
- ✅ DFF is the fundamental memory element
- ✅ Clock synchronizes all state changes
- ✅ Registers are parallel DFFs with shared control
- ✅ RAM is hierarchical: registers → banks → chips
- ✅ Address decoding routes signals to specific memory
- ✅ Program Counter tracks execution flow
- ✅ Memory access takes at least one clock cycle
- ✅ State enables computers to "remember" across computations

#### Common Pitfalls
- **Timing confusion**: Output reflects *previous* cycle, not current input
- **Load control**: Forgetting load=0 means "hold current value"
- **Address width**: n bits can address 2^n locations
- **Feedback loops**: Essential for storage but can cause simulation bugs if not careful

#### Step 9: Understanding Modern Memory Hierarchy (3-4 hours)

Now that you've built RAM from first principles, let's understand how real computers organize memory into a **hierarchy** to balance speed, capacity, and cost.

**The Memory Hierarchy Problem**:

Your CPU can execute billions of instructions per second, but memory is much slower. If the CPU had to wait for RAM on every instruction, it would spend most of its time idle. The solution? **Cache**—small, fast memory that sits between the CPU and main memory.

**The Complete Memory Hierarchy**:

```
                    Speed          Size           Cost/GB
                    (faster ↑)     (smaller ↑)    (higher ↑)
┌─────────────┐
│ CPU Registers│     < 1 ns       ~1 KB          N/A (on-die)
├─────────────┤
│  L1 Cache    │     ~1-2 ns      32-64 KB       Very High
├─────────────┤
│  L2 Cache    │     ~3-10 ns     256-512 KB     High
├─────────────┤
│  L3 Cache    │     ~10-20 ns    8-32 MB        Medium
├─────────────┤
│  Main RAM    │     ~50-100 ns   4-64 GB        Low
│  (DRAM)      │
├─────────────┤
│  SSD         │     ~10-100 µs   256GB-4TB      Very Low
├─────────────┤
│  Hard Disk   │     ~1-10 ms     1-20 TB        Lowest
└─────────────┘
     (slower ↓)      (larger ↓)    (lower ↓)
```

🎓 **Key Insight**: Each level is **10-100x faster** but **10-100x smaller** than the level below. This creates a performance cliff—you want data in the fastest level possible.

**Cache Fundamentals**:

A cache stores **copies** of frequently accessed data from main memory. When the CPU needs data:

1. **Cache Hit**: Data is in cache → Fast access (~1-10ns)
2. **Cache Miss**: Data not in cache → Fetch from RAM (~100ns), copy to cache

**Why Cache Works—Locality Principles**:

Modern programs exhibit two types of locality that make caching highly effective:

1. **Temporal Locality**: If you access data once, you'll likely access it again soon
   - Example: Loop counter variables accessed every iteration
   - Example: Function local variables accessed throughout function execution

2. **Spatial Locality**: If you access data at address X, you'll likely access X+1, X+2, etc. soon
   - Example: Iterating through an array sequentially
   - Example: CPU instruction fetch (next instruction is usually adjacent)

**Cache Architecture—The Building Blocks**:

**Cache Line (Block)**:
Cache doesn't store individual bytes—it stores **cache lines** (typically 64 bytes). When you request byte 1000, the cache fetches bytes 960-1023 all at once. This exploits spatial locality.

```
Memory Address:        960  961  962 ... 1000 ... 1022  1023
                        ↓    ↓    ↓       ↓        ↓     ↓
Cache Line:          [████████████████████████████████████]
                     64 bytes loaded together
```

**Cache Organization—Three Strategies**:

**1. Direct-Mapped Cache** (Simplest):

Every memory address maps to **exactly one** cache line.

```
Memory Address → Cache Index
address % num_cache_lines

Example (8 cache lines):
Address 0, 8, 16, 24 → Cache Line 0
Address 1, 9, 17, 25 → Cache Line 1
Address 2, 10, 18, 26 → Cache Line 2
...
```

**Implementation**:
```python
class DirectMappedCache:
    """Simple direct-mapped cache"""
    def __init__(self, num_lines=256, line_size=64):
        self.num_lines = num_lines
        self.line_size = line_size
        # Each cache line: [valid, tag, data]
        self.lines = [[False, 0, [0]*line_size] for _ in range(num_lines)]
        self.hits = 0
        self.misses = 0

    def access(self, address, main_memory):
        """Access byte at address (returns data, hit/miss)"""
        # Decode address into: [tag | index | offset]
        index = (address // self.line_size) % self.num_lines
        tag = address // (self.line_size * self.num_lines)
        offset = address % self.line_size

        line_valid, line_tag, line_data = self.lines[index]

        # Check for hit
        if line_valid and line_tag == tag:
            self.hits += 1
            return line_data[offset], True  # HIT

        # Cache miss: fetch from main memory
        self.misses += 1
        base_addr = (address // self.line_size) * self.line_size
        new_data = [main_memory[base_addr + i] for i in range(self.line_size)]

        # Replace cache line
        self.lines[index] = [True, tag, new_data]
        return new_data[offset], False  # MISS

    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0
```

**Address Breakdown Example**:
```
32-bit address: 0x00401A3C
Binary: 0000 0000 0100 0000 0001 1010 0011 1100

For 256-line cache with 64-byte lines:
┌───────────────┬────────┬────────┐
│     Tag       │ Index  │ Offset │
│   (18 bits)   │(8 bits)│(6 bits)│
└───────────────┴────────┴────────┘
     Which           Which      Which byte
   memory block    cache line  within line
   (identity)      (position)   (position)
```

**Problem with Direct-Mapped**: **Conflict Misses**

If you alternate between addresses that map to the same cache line, you'll constantly evict and reload:

```python
# Worst case: alternating access to addresses 0 and 8192
# Both map to cache line 0 (assuming 128 lines)
cache.access(0, memory)      # MISS (load line 0)
cache.access(8192, memory)   # MISS (evict line 0, load new data)
cache.access(0, memory)      # MISS (evict again!)
cache.access(8192, memory)   # MISS (evict again!)
# 0% hit rate even though accessing only 2 addresses!
```

**2. Fully Associative Cache** (Most Flexible):

Any memory address can be stored in **any** cache line. On access, search all lines to find match.

```python
class FullyAssociativeCache:
    """Fully associative cache—any address can go anywhere"""
    def __init__(self, num_lines=256, line_size=64):
        self.num_lines = num_lines
        self.line_size = line_size
        self.lines = [[False, 0, [0]*line_size] for _ in range(num_lines)]
        self.lru_counters = [0] * num_lines  # For LRU replacement
        self.hits = 0
        self.misses = 0
        self.time = 0

    def access(self, address, main_memory):
        """Access with LRU replacement policy"""
        tag = address // self.line_size
        offset = address % self.line_size
        self.time += 1

        # Search all lines for hit (parallel in hardware)
        for i, (valid, line_tag, data) in enumerate(self.lines):
            if valid and line_tag == tag:
                self.hits += 1
                self.lru_counters[i] = self.time  # Update LRU
                return data[offset], True  # HIT

        # Miss: find victim line (LRU policy)
        self.misses += 1
        victim = min(range(self.num_lines), key=lambda i: self.lru_counters[i])

        # Fetch cache line from memory
        base_addr = (address // self.line_size) * self.line_size
        new_data = [main_memory[base_addr + i] for i in range(self.line_size)]

        # Replace victim
        self.lines[victim] = [True, tag, new_data]
        self.lru_counters[victim] = self.time
        return new_data[offset], False  # MISS
```

**Advantage**: No conflict misses—if cache has space, every unique line can stay
**Disadvantage**: Hardware must search **all** lines in parallel → expensive, power-hungry

**3. N-Way Set-Associative Cache** (Real-World Compromise):

Hybrid approach: divide cache into **sets**, each set has N lines (ways). An address maps to a specific **set** but can use any **way** within that set.

```
Example: 4-way set-associative cache with 64 sets

Set 0:  [Way 0] [Way 1] [Way 2] [Way 3]
Set 1:  [Way 0] [Way 1] [Way 2] [Way 3]
...
Set 63: [Way 0] [Way 1] [Way 2] [Way 3]

Address 0, 64, 128, 192 → All map to Set 0
But can occupy different ways (no immediate conflict)
```

**Implementation**:
```python
class SetAssociativeCache:
    """N-way set-associative cache"""
    def __init__(self, num_sets=64, ways=4, line_size=64):
        self.num_sets = num_sets
        self.ways = ways
        self.line_size = line_size
        # Each set contains 'ways' lines
        self.cache = [
            [[False, 0, [0]*line_size] for _ in range(ways)]
            for _ in range(num_sets)
        ]
        self.lru = [[0]*ways for _ in range(num_sets)]
        self.hits = 0
        self.misses = 0
        self.time = 0

    def access(self, address, main_memory):
        """Access with set selection and LRU within set"""
        set_index = (address // self.line_size) % self.num_sets
        tag = address // (self.line_size * self.num_sets)
        offset = address % self.line_size
        self.time += 1

        cache_set = self.cache[set_index]
        lru_set = self.lru[set_index]

        # Search ways in this set
        for way, (valid, line_tag, data) in enumerate(cache_set):
            if valid and line_tag == tag:
                self.hits += 1
                lru_set[way] = self.time
                return data[offset], True  # HIT

        # Miss: find LRU way in this set
        self.misses += 1
        victim_way = min(range(self.ways), key=lambda w: lru_set[w])

        # Fetch from memory
        base_addr = (address // self.line_size) * self.line_size
        new_data = [main_memory[base_addr + i] for i in range(self.line_size)]

        # Replace
        cache_set[victim_way] = [True, tag, new_data]
        lru_set[victim_way] = self.time
        return new_data[offset], False  # MISS
```

**Real CPU Examples**:
- **Intel Core i9**: L1 is 8-way, L2 is 4-way, L3 is 16-way
- **AMD Ryzen**: L1 is 8-way, L2 is 8-way, L3 is 16-way
- **Apple M3**: L1 is 8-way, L2 is 12-way (system cache varies)

**Cache Replacement Policies**:

When a cache line is full and you need to load new data, which line gets evicted?

1. **LRU (Least Recently Used)**: Evict the line accessed longest ago
   - Best performance but complex hardware
   - Requires timestamp tracking per line

2. **FIFO (First-In-First-Out)**: Evict oldest loaded line
   - Simpler but worse performance
   - Ignores actual usage patterns

3. **Random**: Pick random line to evict
   - Simplest hardware (just a random number generator)
   - Surprisingly competitive performance

4. **LFU (Least Frequently Used)**: Evict line used least often
   - Good for some workloads
   - Requires usage counters

**Cache Write Policies**:

What happens when the CPU writes data?

**Write-Through**:
- Write to **both** cache and main memory immediately
- **Advantage**: Memory always consistent
- **Disadvantage**: Slow (every write waits for memory)

```python
def write_through(self, address, value, cache, memory):
    """Write to cache and memory"""
    cache[address] = value  # Update cache
    memory[address] = value  # Update memory (slow!)
    # CPU must wait for memory write to complete
```

**Write-Back** (Modern CPUs):
- Write to cache only, mark line as **dirty**
- Write to memory only when evicting dirty line
- **Advantage**: Much faster (writes happen at cache speed)
- **Disadvantage**: Memory can be stale, complexity on eviction

```python
def write_back(self, address, value, cache, memory, dirty_bits):
    """Write to cache only, defer memory write"""
    cache[address] = value
    dirty_bits[address] = True  # Mark dirty

    # Later, on eviction:
    if dirty_bits[evicted_address]:
        memory[evicted_address] = cache[evicted_address]
```

**Multi-Level Cache Architecture**:

Modern CPUs have 3 cache levels, each with different trade-offs:

```
┌──────────────────────────────────────┐
│             CPU Core                  │
│  ┌────────────────────────────────┐  │
│  │ L1 Instruction Cache (32 KB)   │  │  ← Fastest, smallest
│  │ L1 Data Cache (32 KB)          │  │     Split I/D for parallelism
│  └────────────────┬───────────────┘  │
│                   │                   │
│  ┌────────────────▼───────────────┐  │
│  │ L2 Unified Cache (256-512 KB)  │  │  ← Per-core, shared I/D
│  └────────────────┬───────────────┘  │
└───────────────────┼───────────────────┘
                    │
     ┌──────────────▼──────────────┐
     │ L3 Unified Cache (8-32 MB)  │      ← Shared across all cores
     └──────────────┬──────────────┘
                    │
     ┌──────────────▼──────────────┐
     │   Main Memory (DRAM)         │      ← Slowest, largest
     └──────────────────────────────┘
```

**L1 Cache (Level 1)**:
- **Size**: 32-64 KB per core (split: 32 KB instruction + 32 KB data)
- **Speed**: 1-2 nanoseconds (~4 clock cycles at 3 GHz)
- **Associativity**: 8-way set-associative
- **Location**: On-die, closest to CPU execution units
- **Split I/D**: Separate instruction and data caches allow parallel fetch + data access

**L2 Cache (Level 2)**:
- **Size**: 256-512 KB per core
- **Speed**: 3-10 nanoseconds (~10-30 cycles)
- **Associativity**: 4-8-way set-associative
- **Location**: On-die, per-core (not shared)
- **Unified**: Both instructions and data

**L3 Cache (Level 3)**:
- **Size**: 8-32 MB (shared across all cores)
- **Speed**: 10-20 nanoseconds (~30-60 cycles)
- **Associativity**: 12-16-way set-associative
- **Location**: On-die, shared across all cores on the chip
- **Purpose**: Reduce main memory access, facilitate inter-core communication

**Inclusive vs. Exclusive Caches**:

**Inclusive** (Intel approach):
- L3 contains **all** data in L2/L1
- Advantage: Easy cache coherency (check L3 to find data)
- Disadvantage: Wasted space (data duplicated across levels)

**Exclusive** (AMD approach):
- L3 contains **only** data not in L2/L1
- Advantage: More effective total cache capacity
- Disadvantage: More complex coherency logic

**Cache Coherency in Multi-Core Systems**:

With multiple cores each having their own L1/L2 caches, how do we ensure consistency when Core 0 writes to address X and Core 1 reads address X?

**The Coherency Problem**:
```
Initial: Memory[1000] = 5

Core 0:                     Core 1:
L1 cache: [empty]           L1 cache: [empty]

Core 0 reads addr 1000:
L1: [1000 → 5]              L1: [empty]

                            Core 1 reads addr 1000:
L1: [1000 → 5]              L1: [1000 → 5]

Core 0 writes addr 1000 = 10:
L1: [1000 → 10]             L1: [1000 → 5]  ← STALE!
                            ☠️ Core 1 thinks it's 5!
```

**MESI Protocol** (Most Common):

Each cache line has a **state** that coordinates between cores:

- **M**odified: This cache has the only valid copy, it's been modified (dirty)
- **E**xclusive: This cache has the only copy, same as memory (clean)
- **S**hared: Multiple caches have copies, all match memory
- **I**nvalid: This cache line is not valid

**State Transitions**:
```
                   Read Hit
    ┌───────────────────────────────┐
    │                               │
    ▼                               │
┌───────┐  Write    ┌───────┐  Write Hit  ┌──────────┐
│   I   │─────────→ │   E   │────────────→│    M     │
│Invalid│           │Exclusive│            │ Modified │
└───┬───┘           └───┬───┘             └────┬─────┘
    │                   │                      │
    │ Read (others)     │ Read (others)        │ Read (others)
    │                   │                      │
    └───────────────────┴──────────────────────┘
                        │
                        ▼
                   ┌────────┐
                   │Shared  │
                   │  (S)   │
                   └────────┘
```

**Example: MESI in Action**:
```python
# Core 0 reads address 1000 (exclusive)
Core 0: [1000 → 5, state=E]
Core 1: [1000 → Invalid]

# Core 1 reads address 1000
Core 0: [1000 → 5, state=S]  ← Broadcast sets both to Shared
Core 1: [1000 → 5, state=S]

# Core 0 writes address 1000 = 10
# Protocol sends "invalidate" message to Core 1
Core 0: [1000 → 10, state=M]  ← Modified
Core 1: [1000 → Invalid]       ← Invalidated!

# Core 1 reads address 1000
# Core 0 must provide data (memory is stale)
Core 0: [1000 → 10, state=S]  ← Provides data, transitions to Shared
Core 1: [1000 → 10, state=S]  ← Receives from Core 0
Memory: [1000 → 10]            ← Core 0 wrote back to memory
```

**False Sharing** (Performance Killer):

When two cores access **different** variables that happen to be in the **same cache line**:

```c
// Thread 0 runs on Core 0
struct {
    int counter_0;  // Byte 0-3
    int counter_1;  // Byte 4-7  ← Different variable!
} shared;

// Thread 0 (Core 0):
for (int i = 0; i < 1000000; i++)
    shared.counter_0++;

// Thread 1 (Core 1):
for (int i = 0; i < 1000000; i++)
    shared.counter_1++;
```

**What Happens**:
```
Both counter_0 and counter_1 are in the same 64-byte cache line!

Core 0 writes counter_0 → Line becomes Modified
Core 1 writes counter_1 → Line invalidated on Core 0, fetched to Core 1
Core 0 writes counter_0 → Line invalidated on Core 1, fetched to Core 0
... (ping-pong between cores on EVERY write!)

Performance: ~100x slower than if variables were in separate cache lines
```

**Solution: Cache Line Padding**:
```c
struct {
    int counter_0;
    char padding[60];  // Force to separate cache lines
    int counter_1;
} shared;
```

**SRAM vs. DRAM Technology**:

**SRAM (Static RAM)** - Used in Caches:
```
Physical Structure:
┌──────────────┐
│   6 Transistors   │  ← Cross-coupled inverters (flip-flop)
│   per bit     │
└──────────────┘

Characteristics:
- No refresh needed (data persists while powered)
- Very fast (~1 ns)
- Expensive (~$1000/GB if you could buy it)
- Low density (~6 transistors per bit)
- Used in: L1/L2/L3 caches, CPU registers
```

**DRAM (Dynamic RAM)** - Used in Main Memory:
```
Physical Structure:
┌──────────────┐
│ 1 Transistor +│  ← Transistor + capacitor
│ 1 Capacitor  │
└──────────────┘

Characteristics:
- Needs refresh every ~64ms (capacitor leaks charge)
- Slower (~50-100 ns)
- Cheap (~$5-10/GB)
- High density (~1 transistor + capacitor per bit)
- Used in: Main system RAM (DDR4, DDR5)
```

**Why Capacitors Leak (DRAM Refresh)**:
```
Bit stored as charge on tiny capacitor:
High charge = 1
Low charge = 0

Problem: Capacitor leaks charge over time
└→ After ~64ms, "1" might decay to look like "0"

Solution: Refresh circuit
- Periodically reads each row
- If bit was 1, recharges capacitor to full
- Happens automatically in background
- Costs ~5-10% of memory bandwidth
```

**Modern DRAM Types**:

1. **DDR4** (Current mainstream):
   - Speed: 2400-3200 MHz
   - Bandwidth: ~25 GB/s per channel
   - Latency: ~15-20 ns (CAS latency)

2. **DDR5** (Newer):
   - Speed: 4800-6400 MHz
   - Bandwidth: ~40-50 GB/s per channel
   - Latency: Similar to DDR4 (absolute ns)

3. **HBM (High Bandwidth Memory)**:
   - Used in GPUs, high-end accelerators
   - Bandwidth: ~1 TB/s (stacked 3D design)
   - Expensive, specialized applications

**Practical Cache Performance Testing**:

```python
import time
import random

def test_cache_effects():
    """Demonstrate cache performance differences"""

    # Test 1: Sequential access (exploits spatial locality)
    size = 64 * 1024 * 1024  # 64 MB
    data = [0] * size

    start = time.perf_counter()
    for i in range(size):
        data[i] = data[i] + 1  # Sequential access
    sequential_time = time.perf_counter() - start

    # Test 2: Random access (cache thrashing)
    indices = list(range(size))
    random.shuffle(indices)

    start = time.perf_counter()
    for i in indices[:size]:
        data[i] = data[i] + 1  # Random access
    random_time = time.perf_counter() - start

    print(f"Sequential: {sequential_time:.3f}s")
    print(f"Random: {random_time:.3f}s")
    print(f"Slowdown: {random_time/sequential_time:.1f}x")
    # Typical result: 5-10x slower for random access!

def test_cache_line_effect():
    """Show effect of cache line size"""
    array_size = 64 * 1024 * 1024
    data = [0] * array_size

    # Access every 64th element (different cache lines)
    start = time.perf_counter()
    for i in range(0, array_size, 64):
        data[i] += 1
    sparse_time = time.perf_counter() - start

    # Access every element (same cache lines reused)
    start = time.perf_counter()
    for i in range(0, array_size, 1):
        data[i] += 1
    dense_time = time.perf_counter() - start

    print(f"Sparse (every 64th): {sparse_time:.3f}s")
    print(f"Dense (every element): {dense_time:.3f}s")
    print(f"Speedup from cache line reuse: {sparse_time/dense_time:.1f}x")
```

**Cache-Aware Programming**:

**Good: Array of Structs (AoS)** when accessing all fields together:
```c
struct Particle {
    float x, y, z;     // Position
    float vx, vy, vz;  // Velocity
};

Particle particles[1000];

// Update positions - good cache usage!
for (int i = 0; i < 1000; i++) {
    particles[i].x += particles[i].vx;  // All in same cache line
    particles[i].y += particles[i].vy;
    particles[i].z += particles[i].vz;
}
```

**Better: Struct of Arrays (SoA)** when accessing single field across many items:
```c
struct ParticleSystem {
    float x[1000], y[1000], z[1000];
    float vx[1000], vy[1000], vz[1000];
};

ParticleSystem particles;

// Update only x positions - excellent cache usage!
for (int i = 0; i < 1000; i++) {
    particles.x[i] += particles.vx[i];  // Sequential, cache-friendly
}
```

**Memory Bandwidth vs. Latency**:

Two critical metrics:

- **Latency**: Time to access first byte (~100 ns for RAM)
- **Bandwidth**: Bytes per second once data is flowing (~25 GB/s for DDR4)

```
Example: Reading 1 KB
Latency: 100 ns (time to get first byte)
Bandwidth: After first byte, stream at 25 GB/s

Total time = Latency + (Size / Bandwidth)
          = 100 ns + (1024 / 25,000,000,000)
          = 100 ns + 40 ns = 140 ns

For small accesses: latency dominates
For large accesses: bandwidth dominates
```

🎓 **Key Insights**:

1. **Hierarchy is Essential**: CPUs would be 100x slower without cache
2. **Locality Matters**: Write code that accesses memory sequentially when possible
3. **Cache Lines**: 64 bytes loaded together—use them all!
4. **False Sharing**: Separate frequently-written variables by >64 bytes in multi-threaded code
5. **Write-Back**: Modern caches defer memory writes for massive speedup
6. **Coherency is Hard**: Multi-core consistency requires complex protocols
7. **SRAM vs DRAM**: Speed vs. capacity trade-off drives the hierarchy

#### Extension Ideas
- Add cache simulation (faster small memory + slower large memory)
- Implement memory-mapped I/O
- Add wait states for slower memory
- Simulate DRAM refresh cycles
- Build a memory allocator (malloc/free)
- Add memory protection (read-only regions)
- **Implement a complete cache hierarchy** (L1/L2/L3 with coherency)
- **Simulate MESI protocol** for multi-core cache coherency
- **Build a cache performance profiler** to analyze hit rates
- **Implement prefetching** (predict future accesses and load early)

#### Real-World Connection
Modern RAM works exactly like this, scaled up:
- **SRAM** (static RAM): Like your register file, faster but expensive (used in CPU caches)
- **DRAM** (dynamic RAM): Uses capacitors instead of flip-flops, needs refresh, cheaper (main memory)
- **Hierarchy**: L1/L2/L3 caches, main memory, disk—each level bigger and slower
- Your PC register is essentially the CPU's "instruction pointer" (IP/EIP/RIP in x86)
- **Intel Core i9-14900K**: 32 KB L1 + 2 MB L2 per core, 36 MB L3 shared, 8-way L1, 16-way L3
- **AMD Ryzen 9 7950X**: 32 KB L1 + 1 MB L2 per core, 64 MB L3 shared (exclusive design)
- **Apple M3**: 128 KB L1 + 4 MB L2 per performance core, system-level cache varies

---