# Project 1: Logic Gate Simulator

**Objective**: Understand Boolean logic and gate composition

## Background Concepts

Logic gates are the fundamental building blocks of all digital circuits. Everything in a computer—from addition to memory storage—is built from these simple components. The beauty of Boolean logic is that you only need ONE gate (NAND) to build everything else.

**Why NAND is universal**:
- `NOT(a) = NAND(a, a)` - both inputs the same
- `AND(a, b) = NOT(NAND(a, b))` - invert a NAND
- Once you have NOT and AND, you can build any logic function

**Truth tables** are how we describe gate behavior. For example:
```
NAND truth table:
A | B | Out
0 | 0 | 1
0 | 1 | 1
1 | 0 | 1
1 | 1 | 0   (only false when both inputs are true)
```

## Learning Path

### Step 1: Implement the NAND gate (30 minutes)
Start with a simple function or class:
```python
def nand(a, b):
    """The only 'primitive' gate - all others built from this"""
    return not (a and b)
```

Test it manually with all input combinations. This is your atomic building block.

### Step 2: Build NOT from NAND (15 minutes)
```python
def not_gate(a):
    """Feed same input to both NAND inputs"""
    return nand(a, a)
```

🎓 **Learning moment**: You're now doing *gate composition*—building complex behavior from simpler parts. This is abstraction in action!

### Step 3: Build AND, OR, XOR (1 hour)
- AND: NAND followed by NOT
- OR: Apply NOT to inputs, then NAND (DeMorgan's Law)
- XOR: Combination of AND, OR, NOT (outputs true when inputs differ)

For each gate:
1. Draw the truth table by hand
2. Implement using previously built gates
3. Test against your truth table

### Step 4: Multiplexer (MUX) and Demultiplexer (DMUX) (1 hour)
These are more complex but crucial for understanding how computers route data.

#### Understanding the MUX (Multiplexer)

**Conceptual Overview**:
A multiplexer is a digital switch that selects one of several input signals and forwards it to a single output line. Think of it like a railroad switch that routes one train (data) from multiple tracks onto a single track.

**Real-world analogy**: Imagine you have two music sources (a phone and a laptop) and one speaker. The MUX is like the switch that lets you choose which source plays through the speaker. The `sel` (selector) bit is your hand flipping the switch.

**MUX (Multiplexer)** - A 2-to-1 selector that chooses between two inputs:

**Function signature**: `mux(a, b, sel) -> output`

**Truth table**:
```
a | b | sel | out
--|---|-----|----
0 | 0 |  0  |  0   (sel=0: choose a)
1 | 0 |  0  |  1   (sel=0: choose a)
0 | 1 |  0  |  0   (sel=0: choose a)
1 | 1 |  0  |  1   (sel=0: choose a)
0 | 0 |  1  |  0   (sel=1: choose b)
0 | 1 |  1  |  1   (sel=1: choose b)
1 | 0 |  1  |  0   (sel=1: choose b)
1 | 1 |  1  |  1   (sel=1: choose b)
```

**Implementation approach**:
```python
def mux(a, b, sel):
    """
    If sel=0, output=a
    If sel=1, output=b

    Logic: (NOT(sel) AND a) OR (sel AND b)
    - When sel=0: NOT(0)=1, so (1 AND a) OR (0 AND b) = a
    - When sel=1: NOT(1)=0, so (0 AND a) OR (1 AND b) = b
    """
    # TODO: Implement using not_gate, and_gate, or_gate
    pass
```

**Why this logic works** - Let's break down the formula `(NOT(sel) AND a) OR (sel AND b)`:

1. **When sel=0** (we want output = a):
   - `NOT(sel)` becomes `NOT(0) = 1`
   - First part: `1 AND a = a` (passes through a)
   - Second part: `0 AND b = 0` (blocks b)
   - Result: `a OR 0 = a` ✓

2. **When sel=1** (we want output = b):
   - `NOT(sel)` becomes `NOT(1) = 0`
   - First part: `0 AND a = 0` (blocks a)
   - Second part: `1 AND b = b` (passes through b)
   - Result: `0 OR b = b` ✓

The beauty is that the selector "opens a gate" for one input while "closing the gate" for the other.

**Hardware perspective**: In a CPU, MUXes are everywhere:
- **Register selection**: Choose which of 32 registers to read
- **ALU operation**: Route the correct computation result (add vs subtract vs AND)
- **Conditional execution**: Select between branch target or next instruction
- **Data path**: Choose between immediate value or register value

Think of it as a digital switch or hardware's version of an if-statement: `output = a if sel==0 else b`

---

#### Understanding the DMUX (Demultiplexer)

**Conceptual Overview**:
A demultiplexer is the inverse of a multiplexer. It takes one input signal and routes it to one of several output lines based on a selector. Think of it like a railroad switch in reverse—one track splits into multiple tracks, and the switch determines which track the train takes.

**Real-world analogy**: Imagine a postal sorting system. A single letter (the input) arrives, and based on its zip code (the selector), it gets routed to one of several bins (outputs). Only the selected bin receives the letter; all others remain empty.

**DMUX (Demultiplexer)** - Routes one input to one of two outputs based on selector:

**Function signature**: `dmux(input, sel) -> (a, b)`
Note: Returns a tuple of two values!

**Truth table**:
```
in | sel | a | b
---|-----|---|---
0  |  0  | 0 | 0   (sel=0: route to a)
1  |  0  | 1 | 0   (sel=0: route to a)
0  |  1  | 0 | 0   (sel=1: route to b)
1  |  1  | 0 | 1   (sel=1: route to b)
```

**Implementation approach**:
```python
def dmux(input, sel):
    """
    If sel=0, output a gets the input, b gets 0
    If sel=1, output b gets the input, a gets 0

    Logic:
    - a = input AND NOT(sel)  # only passes when sel=0
    - b = input AND sel        # only passes when sel=1
    """
    # TODO: Implement using not_gate, and_gate
    # Return tuple: (a, b)
    pass
```

**Why this logic works** - Let's break down the formulas:

1. **When sel=0** (we want: a=input, b=0):
   - `NOT(sel)` becomes `NOT(0) = 1`
   - Output a: `input AND 1 = input` (passes through)
   - Output b: `input AND 0 = 0` (blocked)
   - Result: `(input, 0)` ✓

2. **When sel=1** (we want: a=0, b=input):
   - `NOT(sel)` becomes `NOT(1) = 0`
   - Output a: `input AND 0 = 0` (blocked)
   - Output b: `input AND 1 = input` (passes through)
   - Result: `(0, input)` ✓

The selector acts like a valve—it opens the path to one output while closing the other.

**Hardware perspective**: In a CPU, DMUXes are used for:
- **Register writing**: Route data to one specific register out of many
- **Memory addressing**: Select which memory location to write to
- **Device selection**: Choose which I/O device receives data
- **Instruction decoding**: Route control signals to different CPU components

**The MUX/DMUX relationship**:
- **MUX**: Many inputs → One output (data convergence)
- **DMUX**: One input → Many outputs (data distribution)
- They're inverse operations: `DMUX(MUX(a,b,s), s)` reconstructs the original routing

Think of DMUX as: `(input, 0) if sel==0 else (0, input)`

---

**Testing strategy**:
1. Test all 8 MUX combinations (2³ = 8 rows in truth table)
2. Test all 4 DMUX combinations (2² = 4 rows in truth table)
3. Verify MUX behaves like: `out = a if sel==0 else b`
4. Verify DMUX behaves like: `(input, 0) if sel==0 else (0, input)`
5. **Symmetry test**: For a given selector, verify that passing data through MUX then DMUX (or vice versa) maintains data integrity

🎓 **Why these matter**: MUX/DMUX are fundamental to data routing in digital systems. Every time your CPU fetches from a register, routes ALU results, or writes to memory, it's using these components. They enable selective data flow—the foundation of programmable computers. Without MUX/DMUX, you couldn't have conditional execution, multiple data paths, or addressable memory.

### Step 5: Build a test harness (1 hour)
Create a comprehensive testing framework for automated verification:

**Core testing function**:
```python
def test_gate(gate_func, truth_table, gate_name="Gate"):
    """
    Compare gate output against expected truth table

    Args:
        gate_func: The gate function to test
        truth_table: List of tuples: (inputs, expected_output)
                    - inputs: tuple of input values
                    - expected_output: expected result
        gate_name: Name for error messages

    Returns:
        True if all tests pass, raises AssertionError otherwise
    """
    passed = 0
    for inputs, expected in truth_table:
        actual = gate_func(*inputs)
        assert actual == expected, \
            f"{gate_name} failed on inputs {inputs}: expected {expected}, got {actual}"
        passed += 1

    print(f"✓ {gate_name}: All {passed} tests passed")
    return True
```

**Example truth tables to create**:

```python
# NAND gate truth table
NAND_TABLE = [
    ((0, 0), 1),
    ((0, 1), 1),
    ((1, 0), 1),
    ((1, 1), 0),
]

# NOT gate truth table
NOT_TABLE = [
    ((0,), 1),
    ((1,), 0),
]

# AND gate truth table
AND_TABLE = [
    ((0, 0), 0),
    ((0, 1), 0),
    ((1, 0), 0),
    ((1, 1), 1),
]

# OR gate truth table
OR_TABLE = [
    ((0, 0), 0),
    ((0, 1), 1),
    ((1, 0), 1),
    ((1, 1), 1),
]

# XOR gate truth table
XOR_TABLE = [
    ((0, 0), 0),
    ((0, 1), 1),
    ((1, 0), 1),
    ((1, 1), 0),
]

# MUX gate truth table
MUX_TABLE = [
    ((0, 0, 0), 0),  # (a, b, sel) -> out
    ((1, 0, 0), 1),
    ((0, 1, 0), 0),
    ((1, 1, 0), 1),
    ((0, 0, 1), 0),
    ((0, 1, 1), 1),
    ((1, 0, 1), 0),
    ((1, 1, 1), 1),
]

# DMUX gate truth table (output is tuple)
DMUX_TABLE = [
    ((0, 0), (0, 0)),  # (input, sel) -> (a, b)
    ((1, 0), (1, 0)),
    ((0, 1), (0, 0)),
    ((1, 1), (0, 1)),
]
```

**Running all tests**:
```python
def run_all_tests():
    """Run the complete test suite"""
    print("Running Logic Gate Test Suite\n" + "="*40)

    test_gate(nand, NAND_TABLE, "NAND")
    test_gate(not_gate, NOT_TABLE, "NOT")
    test_gate(and_gate, AND_TABLE, "AND")
    test_gate(or_gate, OR_TABLE, "OR")
    test_gate(xor_gate, XOR_TABLE, "XOR")
    test_gate(mux, MUX_TABLE, "MUX")
    test_gate(dmux, DMUX_TABLE, "DMUX")

    print("="*40)
    print("✓ All tests passed!")

# Run when script executes
if __name__ == "__main__":
    run_all_tests()
```

**Enhanced testing (optional)**:
```python
def test_gate_with_display(gate_func, truth_table, gate_name="Gate"):
    """Test gate and display truth table comparison"""
    print(f"\n{gate_name} Truth Table Verification:")
    print("-" * 40)

    for inputs, expected in truth_table:
        actual = gate_func(*inputs)
        status = "✓" if actual == expected else "✗"
        print(f"{status} Inputs: {inputs} -> Expected: {expected}, Got: {actual}")

        assert actual == expected, \
            f"Test failed on inputs {inputs}"

    print(f"✓ {gate_name}: All tests passed\n")
```

**What this teaches**:
- **Specification-driven development**: Truth tables are your specification
- **Automated testing**: Manual testing doesn't scale
- **Regression prevention**: Tests ensure changes don't break existing gates
- **Documentation**: Truth tables document expected behavior
- **Hardware verification mindset**: Real chip designers write extensive test benches

🎓 **Key insight**: In hardware design, testing is even more critical than software because you can't easily "patch" a fabricated chip. Test harnesses are your safety net.

### Step 6: Create multi-bit versions (buses) (2 hours)
Extend your gates to operate on multiple bits simultaneously. Real computers process 16, 32, or 64 bits at once. This is called *data parallelism*.

**Two approaches to multi-bit operations**:

#### Approach 1: List-based (easier for learning, more explicit)
Represent a 16-bit value as a list of 16 individual bits:
```python
def not16(a):
    """
    Apply NOT to 16 bits in parallel

    Args:
        a: List of 16 bits [b15, b14, ..., b1, b0]
    Returns:
        List of 16 bits with NOT applied to each

    Example:
        not16([1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0])
        -> [0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]
    """
    return [not_gate(bit) for bit in a]

def and16(a, b):
    """Apply AND to two 16-bit values bit-by-bit"""
    return [and_gate(a[i], b[i]) for i in range(16)]

def or16(a, b):
    """Apply OR to two 16-bit values bit-by-bit"""
    return [or_gate(a[i], b[i]) for i in range(16)]

def mux16(a, b, sel):
    """
    16-bit multiplexer: select entire 16-bit bus

    Args:
        a: 16-bit list
        b: 16-bit list
        sel: Single selector bit
    Returns:
        16-bit list (a if sel=0, b if sel=1)
    """
    return [mux(a[i], b[i], sel) for i in range(16)]
```

**Pros**: Easy to visualize, explicit bit operations, good for learning
**Cons**: Not how Python naturally handles integers

#### Approach 2: Integer-based (more Pythonic, production-like)
Represent a 16-bit value as a Python integer, use bit operations:
```python
def not16(a):
    """
    Apply NOT to 16-bit integer using bitwise complement

    Args:
        a: Integer (0-65535 for 16-bit)
    Returns:
        Integer with all 16 bits inverted

    Example:
        not16(0b1010101010101010)
        -> 0b0101010101010101 (21845)
    """
    # ~a inverts all bits, & 0xFFFF masks to 16 bits
    return (~a) & 0xFFFF

def and16(a, b):
    """Apply AND to two 16-bit integers"""
    return (a & b) & 0xFFFF

def or16(a, b):
    """Apply OR to two 16-bit integers"""
    return (a | b) & 0xFFFF

def mux16(a, b, sel):
    """16-bit multiplexer using conditional"""
    return a if sel == 0 else b
```

**Pros**: More efficient, how real code works, aligns with hardware
**Cons**: Less explicit about individual bit operations

#### Which approach should you use?

**For learning** (recommended for this project):
- Use **Approach 1 (list-based)** for Steps 1-6
- It makes the gate composition explicit
- You'll understand how each bit flows through logic gates

**For production/performance**:
- Use **Approach 2 (integer-based)**
- More efficient and Pythonic
- Better aligns with how hardware actually represents numbers

#### Conversion utilities (useful for both approaches):
```python
def int_to_bits(n, width=16):
    """Convert integer to list of bits (MSB first)"""
    return [(n >> i) & 1 for i in range(width-1, -1, -1)]

def bits_to_int(bits):
    """Convert list of bits to integer"""
    result = 0
    for bit in bits:
        result = (result << 1) | bit
    return result

# Example usage:
# int_to_bits(42, 16) -> [0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,0]
# bits_to_int([1,0,1,0,1,0]) -> 42
```

🎓 **Key insight**: The list-based approach mirrors how hardware works—each wire carries one bit. The integer approach is an abstraction for efficiency. Understanding both helps you think at multiple levels of abstraction.

### Step 7: Visualization (optional but valuable) (2-4 hours)
Build a simple text-based or graphical visualization:
```
Input: a=1, b=0, sel=1

      a(1) ──┐
             ├──[MUX]── out(0)
      b(0) ──┘    ↑
              sel(1)
```

Seeing data flow helps internalize how gates connect.

## What You Should Understand After This Project

- ✅ Boolean algebra translates directly to physical circuits
- ✅ Complex behavior emerges from simple gates (composition)
- ✅ NAND universality: one gate can build any logic
- ✅ Abstraction layers: once you build AND, you forget it's made of NANDs
- ✅ Hardware is parallel: all gates compute simultaneously
- ✅ Testing is crucial: truth tables = specifications

## Common Pitfalls

- **Mixing gate abstraction levels**: Once you build AND from NANDs, only use AND in higher constructs
- **Forgetting bit width**: Keep track of whether you're working with single bits or buses
- **Not testing edge cases**: Test all 0s, all 1s, and alternating patterns

## Extension Ideas

- Add timing simulation (gate delays)
- Implement three-state logic (0, 1, high-impedance)
- Build a circuit optimizer (reduce gate count)
- Create a circuit description language (like HDL)

## Real-World Connection

Every digital circuit in existence uses these gates. When you look at a CPU die photo under a microscope, you're seeing billions of transistors arranged into these exact gate patterns. The Pentium, ARM cores in your phone, GPU shaders—all built from NAND gates at the bottom.
