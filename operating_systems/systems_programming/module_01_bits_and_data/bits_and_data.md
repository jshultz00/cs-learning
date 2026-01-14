# Module 01: Bits and Data

## Overview

This module explores how computers represent and manipulate information at the fundamental level. Understanding binary representation, integer encoding, floating-point formats, and bitwise operations is essential for systems programming, debugging, and writing efficient code.

**Learning Objectives:**
- Understand binary, hexadecimal, and two's complement representation
- Master bitwise operations and bit manipulation techniques
- Learn integer and floating-point encoding standards
- Recognize numeric overflow, underflow, and precision limitations
- Apply bit-level operations to solve practical problems

---

## 1. Information Representation Basics

### 1.1 Why Bits?

Modern computers store and process information using **binary** (base-2) because:
- Electronic circuits have two stable states: high voltage (1) and low voltage (0)
- Binary logic is simple, reliable, and easy to implement in hardware
- Boolean algebra provides a mathematical foundation for computation

**Key Insight**: Everything in a computer—numbers, text, images, programs—is ultimately represented as sequences of bits.

### 1.2 Number Systems

#### Binary (Base-2)
Each position represents a power of 2:
```
1011₂ = 1×2³ + 0×2² + 1×2¹ + 1×2⁰
      = 8 + 0 + 2 + 1
      = 11₁₀
```

#### Hexadecimal (Base-16)
Uses digits 0-9 and A-F (10-15). Each hex digit represents exactly 4 bits:
```
0x2A = 2×16¹ + 10×16⁰ = 32 + 10 = 42₁₀
Binary: 0010 1010
```

**Conversion Table:**
| Hex | Decimal | Binary |
|-----|---------|--------|
| 0   | 0       | 0000   |
| 1   | 1       | 0001   |
| 2   | 2       | 0010   |
| ...  | ...     | ...    |
| 9   | 9       | 1001   |
| A   | 10      | 1010   |
| B   | 11      | 1011   |
| C   | 12      | 1100   |
| D   | 13      | 1101   |
| E   | 14      | 1110   |
| F   | 15      | 1111   |

**Why Hex?** It's compact and maps cleanly to binary (1 hex digit = 4 bits).

### 1.3 Word Size and Addressing

- **Word size**: The nominal size of pointer data (32-bit vs 64-bit systems)
- **32-bit systems**: Can address 2³² bytes (4GB) of memory
- **64-bit systems**: Can address 2⁶⁴ bytes (16 exabytes) of memory

**Practical Impact:**
```c
// On 32-bit system
sizeof(int*)  = 4 bytes
sizeof(long)  = 4 bytes

// On 64-bit system
sizeof(int*)  = 8 bytes
sizeof(long)  = 8 bytes (on most Unix systems)
```

---

## 2. Integer Representation

### 2.1 Unsigned Integers

Straightforward binary encoding where all bits contribute to magnitude:

**w-bit unsigned integer:**
```
B2U(X) = Σ(i=0 to w-1) xᵢ × 2ⁱ

Range: [0, 2^w - 1]
```

**Example (8-bit unsigned):**
```
0000 0000₂ = 0
1111 1111₂ = 255
0101 1010₂ = 90
```

### 2.2 Two's Complement (Signed Integers)

Most significant bit is the **sign bit** (negative weight):

**w-bit two's complement:**
```
B2T(X) = -xw-1 × 2^(w-1) + Σ(i=0 to w-2) xᵢ × 2ⁱ

Range: [-2^(w-1), 2^(w-1) - 1]
```

**Example (8-bit signed):**
```
0111 1111₂ = +127 (largest positive)
0000 0000₂ = 0
1111 1111₂ = -1
1000 0000₂ = -128 (most negative)
```

**Key Properties:**
- **Asymmetric range**: |TMin| = |TMax| + 1
- **TMin = -128, TMax = 127** (for 8-bit)
- **Unique zero**: Only one representation for 0
- **Negation**: `-x = ~x + 1` (bitwise complement plus one)

### 2.3 Conversion Between Signed and Unsigned

**C language behavior:**
```c
int x = -1;
unsigned u = x;  // u = 4294967295 (on 32-bit)

// Bit pattern unchanged, interpretation changes:
// 1111...1111 interpreted as unsigned
```

**Casting rules:**
- Bits are unchanged
- Only the interpretation changes
- Can lead to subtle bugs:
```c
if (-1 < 0u) {  // FALSE! -1 becomes large unsigned
    printf("This won't print\n");
}
```

### 2.4 Sign Extension

When converting to a larger data type, preserve the value:

**Rule**: Copy the sign bit to all new higher-order bits

**Example (8-bit to 16-bit):**
```
-5 (8-bit):  1111 1011
-5 (16-bit): 1111 1111 1111 1011
             ^^^^^^^^ (sign extension)

+5 (8-bit):  0000 0101
+5 (16-bit): 0000 0000 0000 0101
             ^^^^^^^^ (zero extension)
```

**In C:**
```c
short sx = -12345;
int ix = sx;        // Sign extension automatically applied
unsigned ux = sx;   // Sign extended, then reinterpreted as unsigned
```

---

## 3. Integer Arithmetic

### 3.1 Unsigned Addition

**Modular arithmetic**: Results wrap around

```c
// 4-bit example
9 + 8 = 17 → 1 (overflow, wraps to 17 mod 16)
  1001
+ 1000
------
 10001 → 0001 (discard overflow bit)
```

**Overflow detection:**
```c
unsigned int a, b, sum;
sum = a + b;
if (sum < a) {
    // Overflow occurred
}
```

### 3.2 Two's Complement Addition

**Same bit-level operation** as unsigned, different interpretation:

```c
// 4-bit example
5 + 6 = 11 (no overflow)
  0101
+ 0110
------
  1011 → 11

// But in signed interpretation:
5 + 6 = -5 (overflow!)
  0101 (+5)
+ 0110 (+6)
------
  1011 (-5) ← Positive overflow wraps to negative
```

**Overflow conditions:**
- Positive + Positive → Negative: Overflow
- Negative + Negative → Positive: Overflow
- Positive + Negative: Never overflows

### 3.3 Multiplication

**Unsigned:** `u * v` (mod 2^w)

**Signed:** Similar truncation, but maintains two's complement

**Example - 4-bit unsigned multiplication:**
```c
// 3 × 2 = 6 (fits in 4 bits)
  0011  (3)
× 0010  (2)
------
  0110  (6)

// 5 × 4 = 20 (doesn't fit in 4 bits!)
  0101  (5)
× 0100  (4)
------
  10100  (20 in binary)
  0100   (4 after truncation to 4 bits)
// Only lower 4 bits kept: 20 mod 16 = 4
```

**Example - 4-bit signed (two's complement) multiplication:**
```c
// 3 × 2 = 6 (fits)
  0011  (3)
× 0010  (2)
------
  0110  (6)

// -3 × 2 = -6 (fits)
  1101  (-3 in two's complement)
× 0010  (2)
------
  1010  (-6 in two's complement)

// Overflow example: 4 × 3 = 12 (doesn't fit in 4-bit signed, max is 7)
  0100  (4)
× 0011  (3)
------
  1100  (Would be 12, but interpreted as -4!)
```

**Multiplication by powers of 2 (left shift optimization):**
```c
// Power of 2: Simply shift left
x * 2  = x << 1
x * 4  = x << 2
x * 8  = x << 3

// Example: 3 * 4
  0011  (3)
<< 2
------
  1100  (12)
```

**Multiplication by constants (compiler optimization):**
```c
// x * 5 = x * (4 + 1) = (x << 2) + x
int x = 3;
x * 5 = (3 << 2) + 3
      = 12 + 3
      = 15

  0011  (3)      0011  (3)
<< 2           +
------         ------
  1100  (12)    1111  (15)

// x * 7 = x * (8 - 1) = (x << 3) - x
int x = 2;
x * 7 = (2 << 3) - 2
      = 16 - 2
      = 14

   0010  (2)         0010  (2)
<< 3              -
-------           -------
  10000  (16)      01110  (14)

// x * 6 = x * (4 + 2) = (x << 2) + (x << 1)
int x = 3;
x * 6 = (3 << 2) + (3 << 1)
      = 12 + 6
      = 18

  0011  (3)      0011  (3)
<< 2           + << 1
------           ------
  1100  (12)     0110  (6)
                -------
                 10010  (18)
```

### 3.4 Division

**Power-of-2 division:**
```c
// Unsigned division by 2^k: right shift k positions
x >> k  (logical shift)

// Signed division (tricky due to rounding toward zero):
(x + (1 << k) - 1) >> k  // Bias for correct rounding
```

**Example - Unsigned division by powers of 2:**
```c
// 12 / 4 = 3 (exact division)
unsigned x = 12;  // 1100
x >> 2            // 0011 (3)

// 13 / 4 = 3 (rounds down)
unsigned y = 13;  // 1101
y >> 2            // 0011 (3)
// Integer division: 13/4 = 3.25 → 3

// 14 / 2 = 7 (exact)
unsigned z = 14;  // 1110
z >> 1            // 0111 (7)
```

**Example - Signed division by powers of 2 (THE TRICKY PART):**
```c
// 4-bit signed range: -8 to +7

// Positive numbers: same as unsigned
int x = 6;        // 0110
x >> 1            // 0011 (3) ✓

// Negative numbers: need bias for correct rounding toward zero
int y = -6;       // 1010 (two's complement)

// WRONG: Direct right shift gives wrong answer (sometimes)
y >> 1            // 1101 (-3)
// But -6/2 should be -3, so this happens to work!

// Where it breaks: -7 / 2
int z = -7;       // 1001
z >> 1            // 1100 (-4) ✗ WRONG!
// -7/2 = -3.5 → should round to -3, not -4

// CORRECT: Add bias before shifting
(z + (1 << 1) - 1) >> 1
= (z + 1) >> 1
= (-7 + 1) >> 1
= (-6) >> 1
= -3 ✓ (rounds toward zero, not down)

// Why bias works:
// - Right shift rounds down (toward -∞)
// - C division rounds toward zero
// - For negative numbers, bias compensates the difference
```

**Visual example of signed division:**
```c
// -5 / 2 = -2.5 → -2 (round toward zero)

// Without bias:
-5 = 1011
-5 >> 1 = 1101 = -3 ✗ (rounds down to -∞)

// With bias:
(-5 + 1) >> 1 = -4 >> 1 = 1100 >> 1 = 1110 = -2 ✓

// -6 / 2 = -3 (exact)
(-6 + 1) >> 1 = -5 >> 1 = 1011 >> 1 = 1101 = -3 ✓

// -8 / 2 = -4 (exact)
(-8 + 1) >> 1 = -7 >> 1 = 1001 >> 1 = 1100 = -4 ✓
```

**Why signed division needs bias:**
| Value | /4 (math) | >>2 (no bias) | (+3)>>2 (bias) |
|-------|-----------|---------------|----------------|
| 7     | 1.75 → 1  | 1 ✓           | 2 ✗            |
| 6     | 1.5 → 1   | 1 ✓           | 2 ✗            |
| 5     | 1.25 → 1  | 1 ✓           | 2 ✗            |
| 4     | 1 → 1     | 1 ✓           | 1 ✓            |
| -1    | -0.25 → 0 | -1 ✗          | 0 ✓            |
| -2    | -0.5 → 0  | -1 ✗          | 0 ✓            |
| -3    | -0.75 → 0 | -1 ✗          | 0 ✓            |
| -4    | -1 → -1   | -1 ✓          | -1 ✓           |
| -5    | -1.25 → -1| -2 ✗          | -1 ✓           |

**Key difference:**
- **Logical shift** (`>>` for unsigned): Fill with zeros
- **Arithmetic shift** (`>>` for signed): Fill with sign bit

---

## 4. Bitwise Operations

### 4.1 Boolean Operations

**Operators:**
- `&` (AND): Both bits must be 1
- `|` (OR): At least one bit must be 1
- `^` (XOR): Exactly one bit must be 1
- `~` (NOT): Flip all bits

**Truth table:**
```
x | y | x&y | x|y | x^y | ~x
--|---|-----|-----|-----|----
0 | 0 |  0  |  0  |  0  | 1
0 | 1 |  0  |  1  |  1  | 1
1 | 0 |  0  |  1  |  1  | 0
1 | 1 |  1  |  1  |  0  | 0
```

**Applications:**
```c
// Extract lowest byte
x & 0xFF
// Example: x = 0xABCD, x & 0xFF = 0xCD

// Set bit 5
x | (1 << 5)
// Example: x = 0b00010000 (16), x | (1 << 5) = 0b00110000 (48)

// Clear bit 3
x & ~(1 << 3)
// Example: x = 0b00011111 (31), x & ~(1 << 3) = 0b00010111 (23)

// Toggle bit 7
x ^ (1 << 7)
// Example: x = 0b10000000 (128), x ^ (1 << 7) = 0b00000000 (0)
//          x = 0b00000000 (0),   x ^ (1 << 7) = 0b10000000 (128)

// Check if bit 4 is set
if (x & (1 << 4)) { ... }
// Example: x = 0b00010100 (20), (x & (1 << 4)) = 0b00010000 = 16 (true)
//          x = 0b00000100 (4),  (x & (1 << 4)) = 0b00000000 = 0 (false)
```

### 4.2 Shift Operations

**Left shift (`<<`):**
```c
x << k  // Multiply by 2^k (fill right with zeros)
```

**Right shift (`>>`):**
- **Logical**: Fill left with zeros (for unsigned)
- **Arithmetic**: Fill left with sign bit (for signed)

```c
unsigned u = 0x80000000;
u >> 1;  // 0x40000000 (logical)

int s = 0x80000000;  // -2147483648
s >> 1;  // 0xC0000000 (arithmetic, still negative)
```

### 4.3 Bit Manipulation Tricks

**Swap without temporary:**
```c
void swap(int *x, int *y) {
    *x = *x ^ *y;
    *y = *x ^ *y;
    *x = *x ^ *y;
}
```

**How it works:**

**Step-by-step example: swap(5, 3)**
```c
// Initial values:
x = 0101 (5)
y = 0011 (3)

// Step 1: *x = *x ^ *y
// XOR each bit position:
   0101  (x = 5)
^  0011  (y = 3)
--------
   0110  (x = 6)
// Now x stores the "difference" between original x and y
// This captures information about both numbers!

// Step 2: *y = *x ^ *y
// XOR the new x with original y:
   0110  (x = 6, which is original_x ^ original_y)
^  0011  (y = 3, still original value)
--------
   0101  (y = 5)
// Magic! y now equals the original x
// Why? (original_x ^ original_y) ^ original_y = original_x
// Because: y ^ y cancels out, leaving just original_x

// Step 3: *x = *x ^ *y
// XOR the old x with new y:
   0110  (x = 6, still original_x ^ original_y)
^  0101  (y = 5, which is now original_x)
--------
   0011  (x = 3)
// Double magic! x now equals the original y
// Why? (original_x ^ original_y) ^ original_x = original_y
// Because: x ^ x cancels out, leaving just original_y

// Final: x = 3, y = 5 (swapped!)
```

**Why it works: XOR properties**
```c
// Key XOR properties:
1. a ^ a = 0           (anything XOR itself is zero)
2. a ^ 0 = a           (anything XOR zero is itself)
3. XOR is commutative: a ^ b = b ^ a
4. XOR is associative: (a ^ b) ^ c = a ^ (b ^ c)

// Proof for Step 2:
y_new = x_new ^ y_old
      = (x_old ^ y_old) ^ y_old       // substitute x_new
      = x_old ^ (y_old ^ y_old)       // associative property
      = x_old ^ 0                     // y_old ^ y_old = 0
      = x_old                         // x_old ^ 0 = x_old ✓

// Proof for Step 3:
x_new = x_old ^ y_new
      = (x_old ^ y_old) ^ x_old       // substitute from Step 1 & 2
      = (x_old ^ x_old) ^ y_old       // rearrange (commutative)
      = 0 ^ y_old                     // x_old ^ x_old = 0
      = y_old                         // 0 ^ y_old = y_old ✓
```

**Detailed bit-by-bit breakdown:**
```c
Position:  3 2 1 0    (bit positions)

Initial:
x:         0 1 0 1    (5)
y:         0 0 1 1    (3)

After Step 1 (x = x ^ y):
x:         0 1 1 0    (6)
           | | | |
Bit 0: 1^1 = 0 ✓
Bit 1: 0^1 = 1 ✓
Bit 2: 1^0 = 1 ✓
Bit 3: 0^0 = 0 ✓

After Step 2 (y = x ^ y):
y:         0 1 0 1    (5) ← original x value!
           | | | |
Bit 0: 0^1 = 1 ✓
Bit 1: 1^1 = 0 ✓
Bit 2: 1^0 = 1 ✓
Bit 3: 0^0 = 0 ✓

After Step 3 (x = x ^ y):
x:         0 0 1 1    (3) ← original y value!
           | | | |
Bit 0: 0^1 = 1 ✓
Bit 1: 1^0 = 1 ✓
Bit 2: 1^1 = 0 ✓
Bit 3: 0^0 = 0 ✓
```

**Important caveats:**
```c
// DANGER: Fails if x and y point to the same location!
int a = 5;
swap(&a, &a);  // BUG: a becomes 0!

// Why?
// Step 1: a = a ^ a = 0
// Step 2: a = 0 ^ 0 = 0
// Step 3: a = 0 ^ 0 = 0
// Everything gets zeroed!

// Always check for aliasing:
void safe_swap(int *x, int *y) {
    if (x != y) {  // Guard against same address
        *x = *x ^ *y;
        *y = *x ^ *y;
        *x = *x ^ *y;
    }
}

// Also: XOR swap is NOT faster than temp variable on modern CPUs!
// Compilers usually optimize temp-based swap better.
// Use XOR swap only for learning or when memory is extremely tight.
```

**Check if power of 2:**
```c
bool isPowerOf2(unsigned x) {
    return x && !(x & (x - 1));
}
```

**How it works:**
```c
// Powers of 2 have exactly one bit set:
// 1:   0001
// 2:   0010
// 4:   0100
// 8:   1000
// 16: 10000

// Subtracting 1 flips all bits after the single set bit:
// 8:     1000
// 8-1:   0111
// 8&7:   0000  ✓ (is power of 2)

// Non-powers have multiple bits:
// 6:     0110
// 6-1:   0101
// 6&5:   0100  ✗ (not power of 2)

// Edge case: 0 is not a power of 2
// 0 && !(0 & -1) = 0 && !0 = 0 && 1 = 0 ✗
```

**Count set bits (population count):**
```c
int popcount(unsigned x) {
    int count = 0;
    while (x) {
        count++;
        x &= (x - 1);  // Clear lowest set bit
    }
    return count;
}
```

**How it works:**
```c
// x & (x-1) clears the lowest set bit

// Example: count bits in 13 (1101)
Iteration 1:
  x = 1101 (13)
  x-1 = 1100 (12)
  x & (x-1) = 1101 & 1100 = 1100
  count = 1

Iteration 2:
  x = 1100 (12)
  x-1 = 1011 (11)
  x & (x-1) = 1100 & 1011 = 1000
  count = 2

Iteration 3:
  x = 1000 (8)
  x-1 = 0111 (7)
  x & (x-1) = 1000 & 0111 = 0000
  count = 3

Iteration 4:
  x = 0 (loop exits)

Result: 3 bits set ✓

// Why it works: (x-1) flips all bits up to and including
// the lowest set bit, so (x & (x-1)) zeroes just that bit
```

**Isolate lowest set bit:**
```c
x & (-x)  // or x & (~x + 1)
```

**How it works:**
```c
// Negative in two's complement: -x = ~x + 1

// Example: isolate lowest bit in 12 (1100)
x = 1100 (12)
~x = 0011 (bitwise NOT)
~x+1 = 0100 (add 1)
x & (~x+1) = 1100 & 0100 = 0100 (isolated bit 2!)

// Another example: 10 (1010)
x = 1010 (10)
-x = 0110 (two's complement)
x & (-x) = 1010 & 0110 = 0010 (isolated bit 1!)

// Why it works:
// Two's complement flips all bits and adds 1
// This causes all bits BELOW the lowest set bit to flip
// The lowest set bit itself stays in the same position
// AND-ing preserves only that bit

Visual:
x:     ...abc100  (lowest set bit at position 2)
~x:    ...~a~b~c011  (all flipped)
~x+1:  ...~a~b~c100  (add 1, carries up)
x&-x:  ...000100  (only lowest bit remains!)
```

---

## 5. Floating-Point Representation

### 5.1 IEEE 754 Standard

**Format:** `(-1)^s × M × 2^E`
- **s**: Sign bit (1 bit)
- **M**: Significand/Mantissa (23 bits for single, 52 for double)
- **E**: Exponent (8 bits for single, 11 for double)

**Single Precision (32-bit float):**
```
 31  30-23  22-0
[S][Exponent][Fraction]
 1     8        23
```

**Double Precision (64-bit double):**
```
 63  62-52  51-0
[S][Exponent][Fraction]
 1     11       52
```

### 5.2 Normalized Values

**Most common case** (exp ≠ 0 and exp ≠ all 1s):

```
E = Exponent - Bias
Bias = 127 (single), 1023 (double)

M = 1.fraction (implied leading 1)
```

**Example:**
```
Float: 0 10000010 01000000000000000000000
       s   exp           frac

s = 0 (positive)
exp = 130 → E = 130 - 127 = 3
frac = 0.25 → M = 1.25

Value = 1.25 × 2³ = 10.0
```

### 5.3 Denormalized Values

**When exp = 0:**
```
E = 1 - Bias (fixed exponent)
M = 0.fraction (no implied leading 1)
```

**Purpose:** Represent numbers very close to zero

**Example:**
```
Smallest positive denorm (single):
0 00000000 00000000000000000000001
= 2^(-126) × 2^(-23) = 2^(-149) ≈ 1.4 × 10^(-45)
```

### 5.4 Special Values

**Infinity:**
```
exp = all 1s, frac = 0
+∞: s=0, exp=11111111, frac=0
-∞: s=1, exp=11111111, frac=0
```

**NaN (Not a Number):**
```
exp = all 1s, frac ≠ 0
Used for: 0/0, ∞-∞, sqrt(-1)
```

**Zero:**
```
exp = 0, frac = 0
+0: s=0
-0: s=1 (yes, two zeros exist!)
```

### 5.5 Rounding

**IEEE 754 rounding modes:**
- **Round-to-even** (default): Ties round to nearest even
- **Round-toward-zero**: Truncation
- **Round-down**: Floor (toward -∞)
- **Round-up**: Ceiling (toward +∞)

**Example (round-to-even):**
```
2.5 → 2 (even)
3.5 → 4 (even)
```

### 5.6 Floating-Point Arithmetic Pitfalls

**Not associative:**
```c
(1e20 + -1e20) + 1.0 = 1.0
1e20 + (-1e20 + 1.0) = 0.0  // 1.0 lost in second addition
```

**Comparing floats:**
```c
// WRONG
if (f == 0.0) { ... }

// BETTER
if (fabs(f) < epsilon) { ... }
```

**Catastrophic cancellation:**
```c
// Computing b² - 4ac when b² ≈ 4ac loses precision
// Use alternative formulas or higher precision
```

**Overflow/Underflow:**
```c
float f = 1e38 * 10;  // Overflow → infinity
float g = 1e-38 / 1e10;  // Underflow → 0 or denorm
```

---

## 6. Practical Applications

### 6.1 Bit Fields and Flags

**Using bits for compact storage:**
```c
// File permissions (Unix-style)
#define READ  0x4   // 100
#define WRITE 0x2   // 010
#define EXEC  0x1   // 001

unsigned perms = READ | WRITE;  // rw-
if (perms & WRITE) {
    // Can write
}
```

### 6.2 Bit Masks

**Extracting/modifying specific bits:**
```c
// RGB color (32-bit: 0xAARRGGBB)
unsigned color = 0xFF3A7FE5;

unsigned alpha = (color >> 24) & 0xFF;  // 0xFF
unsigned red   = (color >> 16) & 0xFF;  // 0x3A
unsigned green = (color >> 8)  & 0xFF;  // 0x7F
unsigned blue  = color & 0xFF;          // 0xE5

// Set green to 0x00
color = (color & 0xFFFF00FF) | (0x00 << 8);
```

### 6.3 Endianness

**Byte ordering in memory:**
- **Big-endian**: Most significant byte at lowest address (network byte order)
- **Little-endian**: Least significant byte at lowest address (x86)

```c
// int x = 0x01234567

// Big-endian memory layout:
// Address: 0x100  0x101  0x102  0x103
// Value:   01     23     45     67

// Little-endian memory layout:
// Address: 0x100  0x101  0x102  0x103
// Value:   67     45     23     01
```

**Detecting endianness:**
```c
int is_little_endian(void) {
    unsigned int x = 1;
    return *(char*)&x == 1;
}
```

### 6.4 Memory-Efficient Data Structures

**Bit vectors:**
```c
#define SET_SIZE 1000
unsigned bitvector[SET_SIZE/32];  // 1 bit per element

void add(int x) {
    bitvector[x/32] |= (1 << (x%32));
}

int contains(int x) {
    return bitvector[x/32] & (1 << (x%32));
}
```

---

## 7. Common Pitfalls and Best Practices

### 7.1 Integer Pitfalls

**Overflow:**
```c
// BAD: Can overflow
int size = x + y;
char *buf = malloc(size);

// BETTER: Check for overflow
if (x > INT_MAX - y) {
    // Handle error
}
```

**Unsigned underflow:**
```c
unsigned x = 0;
x = x - 1;  // Wraps to UINT_MAX (4294967295 on 32-bit)

// Dangerous in loops:
for (unsigned i = n-1; i >= 0; i--) {  // INFINITE LOOP!
    // ...
}
```

**Mixing signed and unsigned:**
```c
int len = -1;
if (len < sizeof(array)) {  // FALSE! len converted to huge unsigned
    // ...
}
```

### 7.2 Floating-Point Pitfalls

**Precision loss:**
```c
float f = 1e20;
f = f + 1.0;  // No change! 1.0 too small relative to 1e20
```

**Using == with floats:**
```c
float a = 0.1 + 0.2;
float b = 0.3;
if (a == b) {  // May be FALSE due to rounding
    // ...
}

// Use epsilon comparison instead
if (fabs(a - b) < 1e-6) {
    // ...
}
```

### 7.3 Best Practices

1. **Use unsigned for bit operations** (shifts, masks)
2. **Be explicit about type conversions**
3. **Check for overflow** in arithmetic
4. **Use fixed-width types** when size matters: `int32_t`, `uint64_t`
5. **Understand your compiler's** type sizes and behavior
6. **Use `sizeof`** instead of hardcoding sizes
7. **Test edge cases**: 0, -1, MAX, MIN values

---

## 8. Practice Problems

### Problem 1: Bit Manipulation
Implement the following without using arithmetic operators:
```c
int add(int x, int y);           // Add two integers
int negate(int x);               // Negate x
int is_odd(int x);              // Return 1 if odd
int byte_swap(int x, int n);    // Swap bytes n and n+1
```

### Problem 2: Integer Overflow
```c
// Safely compute x*y without overflow
// Return 1 if would overflow, 0 otherwise
int mul_overflow(int x, int y, int *result);
```

### Problem 3: Floating-Point Analysis
```c
// For each, determine if always true:
x + y == y + x              // (a)
x * (y + z) == x*y + x*z    // (b)
(x + y) + z == x + (y + z)  // (c)
x + 0.0 == x                // (d)
x * 1.0 == x                // (e)
```

### Problem 4: Two's Complement
Convert the following to decimal:
- `0x8000` (16-bit signed)
- `0xFFFF` (16-bit signed)
- `0x7FFF` (16-bit signed)

### Problem 5: Endianness
Write a function to convert between big-endian and little-endian:
```c
uint32_t swap_endian(uint32_t x);
```

---

## 9. Key Takeaways

1. **Everything is bits**: Understanding binary representation is fundamental
2. **Two's complement** is the standard for signed integers
3. **Overflow/underflow** can happen silently in C
4. **Bitwise operations** are fast and useful for low-level programming
5. **Floating-point** is approximate, not exact
6. **Type conversions** can introduce bugs if not handled carefully
7. **Know your platform**: Word size, endianness, type sizes matter

---

## 10. Additional Resources

**CS:APP Textbook:**
- Chapter 1: A Tour of Computer Systems
- Chapter 2: Representing and Manipulating Information

**CMU Lectures:**
- Lecture 02: Bits, Bytes, and Integers
- Lecture 03: Floating Point

**Online Tools:**
- [IEEE 754 Converter](https://www.h-schmidt.net/FloatConverter/)
- [Two's Complement Calculator](https://www.omnicalculator.com/math/twos-complement)

**Practice:**
- CS:APP Practice Problems (Chapter 2)
- [LeetCode Bit Manipulation Problems](https://leetcode.com/tag/bit-manipulation/)

---

**Next Module:** [Machine-Level Programming (Assembly & x86-64)](../module_02_machine_level/machine_level.md)
