# Project 2: Binary Arithmetic Calculator

**Objective**: Understand binary arithmetic and ALU design

## Background Concepts

Computers don't "do math" the way humans do. They manipulate electrical signals through logic gates. Addition, the most fundamental operation, is built from XOR and AND gates. Everything else—subtraction, multiplication, division—builds on addition.

**How binary addition works**:
```
  1 0 1 1  (11 in decimal)
+ 0 1 1 0  (6 in decimal)
---------
1 0 0 0 1  (17 in decimal)
```

Notice the "carry" that propagates left, just like decimal addition. This carry is the key challenge in hardware.

**Two's complement** for negative numbers:
- To negate a number: flip all bits, then add 1
- Example: 5 (0101) becomes -5 (1011)
- This clever encoding means subtraction `a - b` becomes `a + (-b)`—no separate subtraction circuit needed!

## Learning Path

### Step 1: Half Adder (30 minutes)
The simplest adder: adds two single bits, produces sum and carry.

```python
def half_adder(a, b):
    """
    Sum: a XOR b (true when inputs differ)
    Carry: a AND b (true when both inputs are 1)
    """
    sum_bit = xor(a, b)
    carry = and_gate(a, b)
    return sum_bit, carry
```

Truth table to memorize:
```
a | b | sum | carry
0 | 0 |  0  |   0
0 | 1 |  1  |   0
1 | 0 |  1  |   0
1 | 1 |  0  |   1    (1+1=10 in binary)
```

🎓 **Key insight**: XOR detects difference, AND detects "overflow." This pattern repeats throughout computer architecture.

### Step 2: Full Adder (45 minutes)
Adds three bits: a, b, and carry-in from previous position.

```python
def full_adder(a, b, carry_in):
    """
    Built from two half adders:
    1. Add a + b
    2. Add that sum + carry_in
    Carry out if either stage produces carry
    """
    sum1, carry1 = half_adder(a, b)
    sum2, carry2 = half_adder(sum1, carry_in)
    carry_out = or_gate(carry1, carry2)
    return sum2, carry_out
```

🎓 **Why this matters**: Every bit position except the rightmost needs to account for carry-in. Full adders are the building blocks of multi-bit addition.

### Step 3: 16-bit Ripple Carry Adder (1 hour)
Chain 16 full adders together, carry ripples left:

```python
def add16(a, b):
    """
    a, b: 16-bit numbers (lists of 16 bits, rightmost is index 0)
    Returns: 16-bit sum, overflow flag
    """
    result = [0] * 16
    carry = 0

    for i in range(16):  # Start from rightmost bit
        result[15-i], carry = full_adder(a[15-i], b[15-i], carry)

    overflow = carry  # Final carry indicates overflow
    return result, overflow
```

🎓 **The "ripple" problem**: Carry must propagate through all 16 stages. In real hardware, this creates delay. Advanced CPUs use "carry lookahead" adders to parallelize carry computation.

### Step 4: Implement Two's Complement Negation (30 minutes)
```python
def negate16(a):
    """
    1. Invert all bits (using NOT16)
    2. Add 1
    """
    inverted = not16(a)
    one = [0] * 15 + 1  # Binary representation of 1
    negated, _ = add16(inverted, one)
    return negated
```

Test this carefully:
- `5` (0000000000000101) → `-5` (1111111111111011)
- `-5` negated should give back `5`

🎓 **Why two's complement is brilliant**:
- Only one representation for zero (unlike sign-magnitude)
- Addition/subtraction use the same circuit
- Comparison operations work naturally with bit patterns

### Step 5: Build Subtraction (15 minutes)
```python
def sub16(a, b):
    """Subtraction is addition of negation: a - b = a + (-b)"""
    return add16(a, negate16(b))
```

That's it! No separate subtraction logic needed. This is why two's complement won the encoding war.

### Step 6: Create the ALU (2 hours)

#### What is an ALU?

The **Arithmetic Logic Unit (ALU)** is the computational heart of a CPU. Every calculation your computer performs—from adding numbers in a spreadsheet to rendering graphics—flows through the ALU.

**Think of the ALU as a Swiss Army knife for binary operations**:
- It can add, subtract, compare numbers
- It can perform logical operations (AND, OR, NOT)
- It decides which operation to perform based on **control signals**
- It reports status information (zero, negative, overflow) to guide program flow

**Why is the ALU so important?**
- **Central to computation**: Without an ALU, a CPU is just fancy storage
- **Enables branching**: Status flags (zero, negative) let programs make decisions (`if`, `while`)
- **Efficiency through reuse**: Same hardware performs multiple operations via control bits
- **Foundation for complexity**: Modern CPUs have multiple ALUs working in parallel

**The big insight**: You don't need separate circuits for 18 different operations. A clever design uses **preprocessing**, **postprocessing**, and **control bits** to create many operations from just two core functions (ADD and AND).

Let's build one.

#### The ALU Implementation

Here's a simple but powerful design:

```python
def alu(x, y, zx, nx, zy, ny, f, no):
    """
    Control bits determine operation:
    zx: zero the x input
    nx: negate (NOT) the x input (bitwise)
    zy: zero the y input
    ny: negate (NOT) the y input (bitwise)
    f:  function (1=add, 0=and)
    no: negate (NOT) the output (bitwise)

    This encoding can perform: 0, 1, -1, x, y, !x, !y, -x, -y,
                                x+1, y+1, x-1, y-1, x+y, x-y, y-x,
                                x&y, x|y
    """
    # Pre-process x
    if zx:
        x = [0] * 16
    if nx:
        x = not16(x)

    # Pre-process y
    if zy:
        y = [0] * 16
    if ny:
        y = not16(y)

    # Compute function
    if f == 1:  # Add
        out, _ = add16(x, y)
    else:  # AND
        out = and16(x, y)

    # Post-process output
    if no:
        out = not16(out)

    # Compute status flags
    zr = all(bit == 0 for bit in out)  # Output is zero
    ng = out[0] == 1  # Output is negative (MSB at index 0 is set)

    return out, zr, ng
```

🎓 **ALU design insights**:
- **Control bits** determine operation—same hardware, different behavior
- **Status flags** (zero, negative) enable conditional logic (used for if/while)
- Only need ADD and AND; all other operations built from preprocessing/postprocessing
- Subtraction: preprocess `y` with negation, then add
- Increment: add with y=1
- Decrement: add with y=-1

#### Understanding the Control Bit Magic

The genius of this ALU is how 6 control bits can produce 18 different operations. Let's decode some examples:

**Constant 0** (zx=1, nx=0, zy=1, ny=0, f=1, no=0):
```
x → zero → 0
y → zero → 0
0 + 0 = 0
```

**Constant 1** (zx=1, nx=1, zy=1, ny=1, f=1, no=1):
```
x → zero → 0 → NOT → -1 (all 1s)
y → zero → 0 → NOT → -1 (all 1s)
(-1) + (-1) = -2
-2 → NOT → 1
```

**Output x** (zx=0, nx=0, zy=1, ny=1, f=0, no=0):
```
x → unchanged → x
y → zero → 0 → NOT → -1 (all 1s)
x AND -1 = x  (AND with all 1s is identity)
```

**Negate x** (compute -x in two's complement) (zx=0, nx=0, zy=1, ny=1, f=1, no=1):
```
x → unchanged → x
y → zero → 0 → NOT → -1
x + (-1) = x - 1
(x - 1) → NOT → -(x - 1) - 1 = -x  (two's complement identity)
```

**Increment x** (compute x+1) (zx=0, nx=1, zy=1, ny=1, f=1, no=1):
```
x → NOT → !x
y → zero → 0 → NOT → -1
!x + (-1) = !x - 1
(!x - 1) → NOT → -(!x - 1) - 1 = x + 1
```

**Subtract (x - y)** (zx=0, nx=1, zy=0, ny=0, f=1, no=1):
```
x → NOT → !x
y → unchanged → y
!x + y → NOT → !((!x) + y) = !(!x + y) = x - y
```
This uses the identity: `x - y = NOT(NOT(x) + y)`

**Bitwise OR (x | y)** (zx=0, nx=1, zy=0, ny=1, f=0, no=1):
```
x → NOT → !x
y → NOT → !y
!x AND !y → NOT → !(!x AND !y) = x OR y  (De Morgan's law)
```

#### Complete Control Bit Table

| Operation | zx | nx | zy | ny | f | no | How it works |
|-----------|----|----|----|----|---|----|--------------|
| 0         | 1  | 0  | 1  | 0  | 1 | 0  | Zero both inputs, add |
| 1         | 1  | 1  | 1  | 1  | 1 | 1  | 0 → -1, add to get -2, NOT to get 1 |
| -1        | 1  | 1  | 1  | 0  | 1 | 0  | x=0→-1, y=0, add to get -1 |
| x         | 0  | 0  | 1  | 1  | 0 | 0  | x AND -1 = x |
| y         | 1  | 1  | 0  | 0  | 0 | 0  | -1 AND y = y |
| !x        | 0  | 0  | 1  | 1  | 0 | 1  | (x AND -1) then NOT |
| !y        | 1  | 1  | 0  | 0  | 0 | 1  | (-1 AND y) then NOT |
| -x        | 0  | 0  | 1  | 1  | 1 | 1  | x + (-1) = x-1, then NOT |
| -y        | 1  | 1  | 0  | 0  | 1 | 1  | (-1) + y = y-1, then NOT |
| x+1       | 0  | 1  | 1  | 1  | 1 | 1  | !x + (-1), then NOT |
| y+1       | 1  | 1  | 0  | 1  | 1 | 1  | (-1) + !y, then NOT |
| x-1       | 0  | 0  | 1  | 1  | 1 | 0  | x + (-1) |
| y-1       | 1  | 1  | 0  | 0  | 1 | 0  | (-1) + y |
| x+y       | 0  | 0  | 0  | 0  | 1 | 0  | Direct addition |
| x-y       | 0  | 1  | 0  | 0  | 1 | 1  | NOT(!x + y) |
| y-x       | 0  | 0  | 0  | 1  | 1 | 1  | NOT(x + !y) |
| x&y       | 0  | 0  | 0  | 0  | 0 | 0  | Direct AND |
| x\|y      | 0  | 1  | 0  | 1  | 0 | 1  | NOT(!x AND !y) - De Morgan |

#### Status Flags Deep Dive

**Zero flag (zr)**: Set when output is all zeros
- Used for equality testing: `if (x == y)` becomes `if (x - y == 0)`
- Jump instruction: "jump if zero" enables loops and conditionals

**Negative flag (ng)**: Set when MSB (most significant bit) is 1
- In two's complement, MSB=1 means negative number
- Used for comparison: `if (x < y)` becomes `if (x - y < 0)`
- **Critical detail**: Assumes bit array format where index 0 is MSB

**Missing: Overflow flag**
- Real CPUs have an overflow flag: detects when result exceeds representable range
- Example: `32767 + 1 = -32768` (wraps around in 16-bit two's complement)
- Overflow occurs when: sign of result differs from expectation based on operand signs
- For addition: overflow if both positive but result negative, or both negative but result positive

#### Why This Design is Clever

1. **Minimal hardware**: Only 2 functions (ADD, AND) yet 18 operations
2. **Preprocessing saves gates**: Cheaper to conditionally zero/invert inputs than build separate circuits
3. **Postprocessing enables symmetry**: NOT output gives "opposite" operations (x+1 vs x-1)
4. **Mathematical identities**: Leverages identities like De Morgan's laws and two's complement properties
5. **Control bit patterns are logical**: Similar operations have similar bit patterns (compare x+1, y+1)

#### Building Intuition

Try predicting outputs for these control bits:
- (1, 0, 0, 1, 1, 0) → Should compute x + !y
- (0, 1, 1, 0, 0, 1) → Should compute !(!x AND 0) = !0 = -1

The key insight: preprocessing and postprocessing transforms let you reuse the same two core functions (ADD and AND) to create a complete arithmetic and logic unit.

This is why ALUs are programmable—the control bits act as a "micro-instruction" that configures the datapath on the fly.

### Step 7: Create a Command-Line Interface (1 hour)
```python
def calculator():
    """Interactive calculator using your ALU"""
    print("Binary Calculator (16-bit two's complement)")
    print("Commands: add, sub, and, or, not, neg, inc, dec, quit")

    while True:
        cmd = input("> ").strip()
        if cmd == "quit":
            break
        # Parse command, convert decimal to binary, call ALU, display result
```

Support both binary and decimal input/output to build intuition for the encoding.

### Step 8: Visualize Internal Operations (2 hours)
Create detailed output showing:
- Input values in binary and decimal
- Intermediate stages (preprocessing, function, postprocessing)
- Carry propagation in addition
- Flag states (zero, negative, overflow)

Example output:
```
Operation: 5 + (-3)
x: 0000000000000101 (5)
y: 1111111111111101 (-3)

Carry chain:
Bit 0: 1+1+0 = 0, carry 1
Bit 1: 0+0+1 = 1, carry 0
Bit 2: 1+1+0 = 0, carry 1
...

Result: 0000000000000010 (2)
Flags: zero=0, negative=0, overflow=0
```

## What You Should Understand After This Project

- ✅ Binary addition is XOR (sum) + AND (carry)
- ✅ Multi-bit addition chains single-bit adders
- ✅ Two's complement enables unified arithmetic circuits
- ✅ ALU control bits create programmable behavior
- ✅ Status flags enable conditional execution
- ✅ Hardware reuses circuits via preprocessing/postprocessing
- ✅ Carry propagation is the performance bottleneck

## Common Pitfalls

- **Bit order confusion**: Decide if index 0 is LSB or MSB and stick with it
- **Sign extension**: When converting to larger bit widths, copy the sign bit
- **Overflow detection**: Not the same as carry-out; occurs when sign bit flips unexpectedly
- **Testing edge cases**: Test 0, -1, max positive, max negative, overflow scenarios

## Extension Ideas

- Implement carry-lookahead adder (faster)
- Add multiplication (repeated addition or shift-and-add algorithm)
- Implement division (much harder!)
- Add floating-point support (IEEE 754 format)
- Create a microcode interpreter for complex operations
- Optimize gate count—how few gates can you use?

## Real-World Connection

Intel's early processors (8080, 8086) had similar ALUs. Modern CPUs have multiple ALUs operating in parallel, with sophisticated carry-lookahead logic. But the fundamental principles remain: XOR for sum, AND for carry, two's complement for negation.
