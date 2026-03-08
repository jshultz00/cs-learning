/* 
 * CS:APP Data Lab 
 * 
 * <Please put your name and userid here>
 * 
 * bits.c - Source file with your solutions to the Lab.
 *          This is the file you will hand in to your instructor.
 *
 * WARNING: Do not include the <stdio.h> header; it confuses the dlc
 * compiler. You can still use printf for debugging without including
 * <stdio.h>, although you might get a compiler warning. In general,
 * it's not good practice to ignore compiler warnings, but in this
 * case it's OK.  
 */

#if 0
/*
 * Instructions to Students:
 *
 * STEP 1: Read the following instructions carefully.
 */

You will provide your solution to the Data Lab by
editing the collection of functions in this source file.

INTEGER CODING RULES:
 
  Replace the "return" statement in each function with one
  or more lines of C code that implements the function. Your code 
  must conform to the following style:
 
  int Funct(arg1, arg2, ...) {
      /* brief description of how your implementation works */
      int var1 = Expr1;
      ...
      int varM = ExprM;

      varJ = ExprJ;
      ...
      varN = ExprN;
      return ExprR;
  }

  Each "Expr" is an expression using ONLY the following:
  1. Integer constants 0 through 255 (0xFF), inclusive. You are
      not allowed to use big constants such as 0xffffffff.
  2. Function arguments and local variables (no global variables).
  3. Unary integer operations ! ~
  4. Binary integer operations & ^ | + << >>
    
  Some of the problems restrict the set of allowed operators even further.
  Each "Expr" may consist of multiple operators. You are not restricted to
  one operator per line.

  You are expressly forbidden to:
  1. Use any control constructs such as if, do, while, for, switch, etc.
  2. Define or use any macros.
  3. Define any additional functions in this file.
  4. Call any functions.
  5. Use any other operations, such as &&, ||, -, or ?:
  6. Use any form of casting.
  7. Use any data type other than int.  This implies that you
     cannot use arrays, structs, or unions.

 
  You may assume that your machine:
  1. Uses 2s complement, 32-bit representations of integers.
  2. Performs right shifts arithmetically.
  3. Has unpredictable behavior when shifting an integer by more
     than the word size.

EXAMPLES OF ACCEPTABLE CODING STYLE:
  /*
   * pow2plus1 - returns 2^x + 1, where 0 <= x <= 31
   */
  int pow2plus1(int x) {
     /* exploit ability of shifts to compute powers of 2 */
     return (1 << x) + 1;
  }

  /*
   * pow2plus4 - returns 2^x + 4, where 0 <= x <= 31
   */
  int pow2plus4(int x) {
     /* exploit ability of shifts to compute powers of 2 */
     int result = (1 << x);
     result += 4;
     return result;
  }

FLOATING POINT CODING RULES

For the problems that require you to implent floating-point operations,
the coding rules are less strict.  You are allowed to use looping and
conditional control.  You are allowed to use both ints and unsigneds.
You can use arbitrary integer and unsigned constants.

You are expressly forbidden to:
  1. Define or use any macros.
  2. Define any additional functions in this file.
  3. Call any functions.
  4. Use any form of casting.
  5. Use any data type other than int or unsigned.  This means that you
     cannot use arrays, structs, or unions.
  6. Use any floating point data types, operations, or constants.


NOTES:
  1. Use the dlc (data lab checker) compiler (described in the handout) to 
     check the legality of your solutions.
  2. Each function has a maximum number of operators (! ~ & ^ | + << >>)
     that you are allowed to use for your implementation of the function. 
     The max operator count is checked by dlc. Note that '=' is not 
     counted; you may use as many of these as you want without penalty.
  3. Use the btest test harness to check your functions for correctness.
  4. Use the BDD checker to formally verify your functions
  5. The maximum number of ops for each function is given in the
     header comment for each function. If there are any inconsistencies 
     between the maximum ops in the writeup and in this file, consider
     this file the authoritative source.

/*
 * STEP 2: Modify the following functions according the coding rules.
 * 
 *   IMPORTANT. TO AVOID GRADING SURPRISES:
 *   1. Use the dlc compiler to check that your solutions conform
 *      to the coding rules.
 *   2. Use the BDD checker to formally verify that your solutions produce 
 *      the correct answers.
 */


#endif
/* 
 * bitAnd - x&y using only ~ and | 
 *   Example: bitAnd(6, 5) = 4
 *   Legal ops: ~ |
 *   Max ops: 8
 *   Rating: 1
 */
int bitAnd(int x, int y) {
  return ~(~x | ~y);
}
/* 
 * getByte - Extract byte n from word x
 *   Bytes numbered from 0 (LSB) to 3 (MSB)
 *   Examples: getByte(0x12345678,1) = 0x56
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 6
 *   Rating: 2
 */
int getByte(int x, int n) {
  return (x >> (n << 3)) & 0xFF;
}
/* 
 * logicalShift - shift x to the right by n, using a logical shift
 *   Can assume that 0 <= n <= 31
 *   Examples: logicalShift(0x87654321,4) = 0x08765432
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 20
 *   Rating: 3 
 */
int logicalShift(int x, int n) {
  return (x >> n) & ~(((1 << 31) >> n) << 1);
}
/*
 * bitCount - returns count of number of 1's in word
 *   Examples: bitCount(5) = 2, bitCount(7) = 3
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 40
 *   Rating: 4
 */
 int bitCount(int x) {
  /*
   * Divide-and-conquer popcount: count 1-bits by summing adjacent groups,
   * doubling the group size each stage: bits -> pairs -> nibbles -> bytes -> halves -> total
   *
   * Example with x = 0b11101010:
   *   Stage 0:  1 1 1 0 1 0 1 0       raw bits
   *   Stage 1: 10 01 01 01             count per pair   (2,1,1,1)
   *   Stage 2: 0011 0010              count per nibble  (3,2)
   *   Stage 3: 00000101               count per byte    (5) ✓
   */

  /* Masks select alternating groups at each level:
   *   mask1: every other BIT      0101...  selects even bits
   *   mask2: every other PAIR     0011...  selects even pairs
   *   mask3: every other NIBBLE   00001111...  selects even nibbles
   * (Can't use large constants directly in datalab, so build from 0xFF pieces) */
  int m1 = 0x55 | (0x55 << 8);
  int mask1 = m1 | (m1 << 16);        /* 0x55555555 */
  int m2 = 0x33 | (0x33 << 8);
  int mask2 = m2 | (m2 << 16);        /* 0x33333333 */
  int m3 = 0x0F | (0x0F << 8);
  int mask3 = m3 | (m3 << 16);        /* 0x0F0F0F0F */

  /* Stage 1: count bits in each PAIR (result: 0, 1, or 2 per pair)
   *   Even bits: x & mask1       Odd bits shifted down: (x>>1) & mask1
   *   Add them together */
  x = (x & mask1) + ((x >> 1) & mask1);

  /* Stage 2: count bits in each NIBBLE (result: 0-4 per nibble)
   *   Even pairs: x & mask2      Odd pairs shifted down: (x>>2) & mask2 */
  x = (x & mask2) + ((x >> 2) & mask2);

  /* Stage 3: count bits in each BYTE (result: 0-8 per byte)
   *   Optimization: max per nibble is 4, and 4+4=8 fits in 4 bits,
   *   so we can add FIRST, mask ONCE after (saves an op) */
  x = (x + (x >> 4)) & mask3;

  /* Stage 4: count bits in each 16-bit HALF (result: 0-16)
   *   Max 16 fits in 8 bits, so no masking needed yet */
  x = x + (x >> 8);

  /* Stage 5: count bits in full 32-bit WORD (result: 0-32)
   *   Max 32 fits in 8 bits, so no masking needed yet */
  x = x + (x >> 16);

  /* Final mask: 0x3F = 63 = 0b111111, keeps only the 6-bit total (0-32) */
  return x & 0x3F;
}
/* 
 * bang - Compute !x without using !
 *   Examples: bang(3) = 0, bang(0) = 1
 *   Legal ops: ~ & ^ | + << >>
 *   Max ops: 12
 *   Rating: 4 
 */
int bang(int x) {
  /*
   * Goal: return 1 if x == 0, else 0. Without using !.
   *
   * Key insight: 0 is the ONLY number where both x and -x have a 0 sign bit.
   *   - Positive x: x has sign bit 0, but -x has sign bit 1
   *   - Negative x: x has sign bit 1
   *   - Zero: both x and -x (which is still 0) have sign bit 0
   *
   * So: OR x with -x. The sign bit is 1 for any nonzero value, 0 only for zero.
   * Arithmetic right shift by 31 spreads the sign bit to all 32 bits:
   *   - Nonzero: 0xFFFFFFFF (which is -1)
   *   - Zero:    0x00000000 (which is 0)
   * Add 1: nonzero gives 0, zero gives 1. Done!
   *
   * Example: x = 5
   *   -x = ~5 + 1 = 0xFFFFFFFB
   *   x | (-x) = 0x00000005 | 0xFFFFFFFB = 0xFFFFFFFF  (sign bit = 1)
   *   >> 31 = 0xFFFFFFFF = -1
   *   + 1 = 0  ✓
   *
   * Example: x = 0
   *   -x = ~0 + 1 = 0x00000000
   *   x | (-x) = 0 | 0 = 0  (sign bit = 0)
   *   >> 31 = 0
   *   + 1 = 1  ✓
   */
  return ((x | (~x + 1)) >> 31) + 1;
}
/* 
 * tmin - return minimum two's complement integer 
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 4
 *   Rating: 1
 */
int tmin(void) {
  /*
   * The minimum two's complement 32-bit integer is 0x80000000 = -2147483648.
   * It's just a 1 in the sign bit and 0s everywhere else.
   * Shift 1 left by 31 positions to place it in the sign bit.
   */
  return 1 << 31;
}
/* 
 * fitsBits - return 1 if x can be represented as an 
 *  n-bit, two's complement integer.
 *   1 <= n <= 32
 *   Examples: fitsBits(5,3) = 0, fitsBits(-4,3) = 1
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 15
 *   Rating: 2
 */
int fitsBits(int x, int n) {
  /*
   * x fits in n bits if the top (32 - n) bits are all copies of the sign bit.
   * In other words, everything above bit (n-1) is just sign extension.
   *
   * Approach: arithmetic right shift x by (n-1). This collapses all the upper
   * bits AND the sign bit into one value:
   *   - If x is non-negative and fits: shifted = 0x00000000 (all 0s)
   *   - If x is negative and fits:     shifted = 0xFFFFFFFF (all 1s, i.e., -1)
   *   - If x doesn't fit:              shifted = something else
   *
   * So we just need to check: is shifted == 0 OR shifted == -1?
   *   !shifted       → 1 if shifted == 0,  0 otherwise
   *   !(~shifted)    → 1 if shifted == -1, 0 otherwise  (because ~(-1) = 0)
   *   OR them together with |
   *
   * We use n + ~0 instead of n - 1 (since minus isn't allowed; ~0 = -1).
   *
   * Example: fitsBits(5, 3)    →  5 = 0b...00101
   *   shifted = 5 >> 2 = 1  →  !1 = 0, !(~1) = 0  → 0 ✓ (5 doesn't fit in 3 bits)
   *
   * Example: fitsBits(-4, 3)   →  -4 = 0xFFFFFFFC
   *   shifted = -4 >> 2 = -1  →  !(-1) = 0, !(~(-1)) = !(0) = 1  → 1 ✓
   *
   * Example: fitsBits(3, 3)    →  3 = 0b...011
   *   shifted = 3 >> 2 = 0  →  !0 = 1  → 1 ✓
   */
  int shift = n + (~0);       /* n - 1 */
  int shifted = x >> shift;    /* all 0s or all 1s if x fits */
  return !(shifted) | !(~shifted);
}
/* 
 * divpwr2 - Compute x/(2^n), for 0 <= n <= 30
 *  Round toward zero
 *   Examples: divpwr2(15,1) = 7, divpwr2(-33,4) = -2
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 15
 *   Rating: 2
 */
int divpwr2(int x, int n) {
  /*
   * Dividing by 2^n is just a right shift: x >> n.
   * BUT: arithmetic right shift rounds toward NEGATIVE infinity, not toward zero.
   *   Example: -33 >> 4 = -3 (rounds down), but -33/16 = -2 (rounds toward zero).
   *
   * Fix for negative numbers: add a bias of (2^n - 1) BEFORE shifting.
   * This "bumps up" negative numbers just enough to make the shift round toward zero.
   *   -33 + 15 = -18, then -18 >> 4 = -2 ✓
   *
   * For positive numbers, the bias must be 0 (shifting already rounds toward zero).
   *
   * How to conditionally add the bias:
   *   sign = x >> 31  →  0x00000000 if positive, 0xFFFFFFFF if negative
   *   bias = sign & ((1 << n) - 1)  →  0 if positive, (2^n - 1) if negative
   *
   * The & with sign acts like an if-statement: for positive x, sign is all 0s
   * so bias is 0. For negative x, sign is all 1s so bias passes through unchanged.
   *
   * Example: divpwr2(15, 1)
   *   sign = 0, bias = 0, (15 + 0) >> 1 = 7 ✓
   *
   * Example: divpwr2(-33, 4)
   *   sign = 0xFFFFFFFF, bias = 0xF & 0xF = 15, (-33 + 15) >> 4 = -18 >> 4 = -2 ✓
   */
  int sign = x >> 31;
  int bias = sign & ((1 << n) + (~0));
  return (x + bias) >> n;
}
/* 
 * negate - return -x 
 *   Example: negate(1) = -1.
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 5
 *   Rating: 2
 */
int negate(int x) {
  /*
   * Two's complement negation: -x = ~x + 1
   *
   * Flip all bits (~ turns 0→1 and 1→0), then add 1.
   * This works because ~x = -x - 1 in two's complement (bitwise NOT gives
   * the "one's complement" which is off by one), so ~x + 1 = -x.
   *
   * Example: negate(1)
   *   ~1 = 0xFFFFFFFE = -2
   *   -2 + 1 = -1 ✓
   *
   * Example: negate(-5)
   *   ~(-5) = ~0xFFFFFFFB = 0x00000004 = 4
   *   4 + 1 = 5 ✓
   */
  return ~x + 1;
}
/* 
 * isPositive - return 1 if x > 0, return 0 otherwise 
 *   Example: isPositive(-1) = 0.
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 8
 *   Rating: 3
 */
int isPositive(int x) {
  /*
   * x > 0 means: x is not negative AND x is not zero.
   *
   * Check 1: Is x negative?
   *   x >> 31 gives 0xFFFFFFFF (-1) if negative, 0x00000000 if non-negative.
   *   So !(x >> 31) is 1 if non-negative, 0 if negative.
   *
   * Check 2: Is x zero?
   *   !x is 1 if x is zero, 0 otherwise.
   *
   * We need: non-negative AND not-zero.
   * But we can't use &&, so combine with bitwise tricks:
   *   (x >> 31) gives the sign bit spread to all bits.
   *   (x >> 31) | (!x) is nonzero when x is negative OR x is zero.
   *   Negate with ! to get: 1 only when x is strictly positive.
   *
   * Example: x = 5   → sign = 0, !x = 0  → !(0 | 0) = 1 ✓
   * Example: x = 0   → sign = 0, !x = 1  → !(0 | 1) = 0 ✓
   * Example: x = -1  → sign = -1, !x = 0 → !(-1 | 0) = !(-1) = 0 ✓
   */
  return !((x >> 31) | (!x));
}
/* 
 * isLessOrEqual - if x <= y  then return 1, else return 0 
 *   Example: isLessOrEqual(4,5) = 1.
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 24
 *   Rating: 3
 */
int isLessOrEqual(int x, int y) {
  /*
   * We want: x <= y, i.e., y - x >= 0.
   *
   * Naive approach: compute y - x and check the sign. BUT this overflows
   * when x and y have different signs (e.g., x = -2 billion, y = 2 billion).
   *
   * Safe approach: handle two cases separately.
   *
   * Case 1: x and y have DIFFERENT signs.
   *   If x is negative and y is non-negative → x <= y is always true.
   *   If x is non-negative and y is negative → x <= y is always false.
   *   No subtraction needed, so no overflow risk.
   *
   * Case 2: x and y have the SAME sign.
   *   Subtraction y - x can't overflow (same-sign subtraction is safe).
   *   Check if y - x >= 0 (sign bit is 0).
   *
   * Implementation:
   *   signX = x >> 31 (all 1s if negative, all 0s if non-negative)
   *   signY = y >> 31
   *   diffSign = signX ^ signY  (1 if different signs, 0 if same)
   *
   *   Case 1 result: diffSign & signX
   *     If signs differ AND x is negative → 1 (x <= y is true)
   *
   *   Case 2 result: (!diffSign) & !((y + ~x + 1) >> 31)
   *     If same sign AND (y - x) is non-negative → 1
   *
   * Example: isLessOrEqual(4, 5)
   *   Same sign, y - x = 1 >= 0 → 1 ✓
   *
   * Example: isLessOrEqual(-1, -2147483648)
   *   Same sign, y - x = -2147483648 + 1 = -2147483647, sign bit 1 → 0 ✓
   *   Wait, -1 <= -2147483648 is false, so 0 is correct ✓
   */
  int signX = (x >> 31) & 1;
  int signY = (y >> 31) & 1;
  int diffSign = signX ^ signY;
  int diff = y + (~x + 1);
  int sameSignResult = (!(diff >> 31)) & (!diffSign);
  int diffSignResult = diffSign & signX;
  return sameSignResult | diffSignResult;
}
/*
 * ilog2 - return floor(log base 2 of x), where x > 0
 *   Example: ilog2(16) = 4
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 90
 *   Rating: 4
 */
int ilog2(int x) {
  /*
   * floor(log2(x)) = position of the highest set bit (0-indexed).
   * Example: ilog2(16) = ilog2(0b10000) = 4
   * Example: ilog2(31) = ilog2(0b11111) = 4 (same — highest bit is still bit 4)
   *
   * Strategy: binary search for the highest set bit.
   * Ask "is the highest bit in the top 16? top 8? top 4? top 2? top 1?"
   *
   * Step 1: Are any of the top 16 bits set? (bits 16-31)
   *   If yes, the answer is at least 16 — shift right by 16 and add 16 to result.
   *   If no, the answer is in the bottom 16 — don't shift, add 0.
   *
   * Step 2: Of the remaining bits, are the top 8 set?
   *   Same idea: conditionally shift by 8, add 8.
   *
   * ...and so on for 4, 2, 1.
   *
   * The trick: !!( x >> 16 ) is 1 if any top-16 bits are set, 0 otherwise.
   * Multiply by 16 using << 4 to get either 16 or 0 as the shift amount.
   *
   * Example: ilog2(255) = ilog2(0x000000FF)
   *   Step 1: !!(0xFF >> 16) = !!(0) = 0, shift = 0, result = 0
   *   Step 2: !!(0xFF >> 8) = !!(0) = 0, shift = 0, result = 0
   *   Step 3: !!(0xFF >> 4) = !!(0xF) = 1, shift = 4, x = 0xF, result = 4
   *   Step 4: !!(0xF >> 2) = !!(3) = 1, shift = 2, x = 3, result = 6
   *   Step 5: !!(3 >> 1) = !!(1) = 1, shift = 1, result = 7 ✓  (2^7 = 128 <= 255 < 256 = 2^8)
   */
  int result = 0;
  int shift;

  /* Is the answer in bits 16-31? */
  shift = (!!(x >> 16)) << 4;   /* shift = 16 or 0 */
  result = result + shift;
  x = x >> shift;

  /* Is the answer in bits 8-15 of the remaining value? */
  shift = (!!(x >> 8)) << 3;    /* shift = 8 or 0 */
  result = result + shift;
  x = x >> shift;

  /* Bits 4-7? */
  shift = (!!(x >> 4)) << 2;    /* shift = 4 or 0 */
  result = result + shift;
  x = x >> shift;

  /* Bits 2-3? */
  shift = (!!(x >> 2)) << 1;    /* shift = 2 or 0 */
  result = result + shift;
  x = x >> shift;

  /* Bit 1? */
  shift = !!(x >> 1);            /* shift = 1 or 0 */
  result = result + shift;

  return result;
}
/* 
 * float_neg - Return bit-level equivalent of expression -f for
 *   floating point argument f.
 *   Both the argument and result are passed as unsigned int's, but
 *   they are to be interpreted as the bit-level representations of
 *   single-precision floating point values.
 *   When argument is NaN, return argument.
 *   Legal ops: Any integer/unsigned operations incl. ||, &&. also if, while
 *   Max ops: 10
 *   Rating: 2
 */
unsigned float_neg(unsigned uf) {
  /*
   * IEEE 754 single-precision float layout (32 bits):
   *   [1 sign bit] [8 exponent bits] [23 mantissa/fraction bits]
   *   Bit 31       Bits 30-23        Bits 22-0
   *
   * To negate a float, just flip the sign bit (bit 31).
   * EXCEPT: if the input is NaN, return it unchanged.
   *
   * NaN detection: NaN has exponent = 0xFF (all 1s) AND a nonzero mantissa.
   *   - Infinity also has exponent 0xFF, but mantissa = 0. That's NOT NaN.
   *   - So: NaN iff exponent bits are all 1 AND at least one mantissa bit is 1.
   *
   * Extract exponent: (uf >> 23) & 0xFF
   * Extract mantissa: uf & 0x7FFFFF
   *
   * Example: float_neg(0x3F800000) — this is +1.0
   *   Not NaN, so flip sign bit: 0xBF800000 = -1.0 ✓
   *
   * Example: float_neg(0x7FC00001) — this is NaN
   *   exp = 0xFF, mantissa != 0, so return unchanged ✓
   */
  /*
   * NaN check without control flow:
   *   isNaN = 1 if exp is all 1s AND frac is nonzero, 0 otherwise
   *
   * If NaN:  return uf (unchanged)
   * If not:  return uf ^ 0x80000000 (flip sign bit)
   *
   * Trick: use isNaN as a selector.
   *   result = (isNaN_mask & uf) | (~isNaN_mask & (uf ^ 0x80000000))
   *   When isNaN_mask = 0xFFFFFFFF: picks uf
   *   When isNaN_mask = 0x00000000: picks uf ^ 0x80000000
   *
   * Build isNaN_mask: need all 1s or all 0s.
   *   isNaN = !(exp ^ 0xFF) & !!frac  →  1 or 0
   *   But we need a full mask. Use arithmetic: 0 - isNaN
   *   0 - 0 = 0x00000000, 0 - 1 = 0xFFFFFFFF (wraps to all 1s)
   */
  unsigned exp = (uf >> 23) & 0xFF;
  unsigned frac = uf & 0x7FFFFF;
  unsigned isNaN = !(exp ^ 0xFF) & !!frac;
  unsigned mask = ~isNaN + 1;            /* 0xFFFFFFFF if NaN, 0x00000000 if not */
  unsigned flipped = uf ^ (1 << 31);
  return (mask & uf) | (~mask & flipped);
}
/* 
 * float_i2f - Return bit-level equivalent of expression (float) x
 *   Result is returned as unsigned int, but
 *   it is to be interpreted as the bit-level representation of a
 *   single-precision floating point values.
 *   Legal ops: Any integer/unsigned operations incl. ||, &&. also if, while
 *   Max ops: 30
 *   Rating: 4
 */
unsigned float_i2f(int x) {
  /*
   * Convert an int to its IEEE 754 float bit representation.
   * This is what the CPU does when you write: float f = (float) x;
   *
   * IEEE 754 float = [sign(1)] [exponent(8)] [fraction(23)]
   *
   * Steps:
   * 1. Handle special case: x = 0 → return 0 (float 0.0)
   * 2. Record the sign, then work with the absolute value.
   * 3. Find the position of the highest set bit — that's the exponent.
   *    (In IEEE 754, exponent is stored with bias 127, so exp_field = pos + 127)
   * 4. Shift the remaining bits into the 23-bit fraction field.
   *    - If the number has MORE than 23 bits of precision, we must ROUND.
   *    - IEEE 754 uses "round to even" (banker's rounding):
   *      - Look at the bits being dropped.
   *      - If they're exactly halfway (0b100...0), round to make the last kept bit even.
   *      - If above halfway, round up. Below halfway, round down (truncate).
   * 5. Assemble: sign | exponent | fraction
   *
   * Example: float_i2f(1) → 0x3F800000
   *   abs = 1 = 0b1, highest bit = 0, exp = 127, frac = 0
   *   result = 0 | (127 << 23) | 0 = 0x3F800000 ✓
   *
   * Example: float_i2f(-1) → 0xBF800000
   *   Same but with sign bit set ✓
   */
  unsigned sign = 0;
  unsigned absVal;
  unsigned exp;
  unsigned frac;
  int pos;
  unsigned round_bit, sticky_bits, halfway;

  /* Special case: 0 */
  if (x == 0) return 0;

  /* Extract sign and get absolute value */
  if (x < 0) {
    sign = 1 << 31;
    /* Can't just do -x because -Tmin overflows. Use unsigned. */
    absVal = (unsigned)(~x + 1);
  } else {
    absVal = (unsigned)x;
  }

  /* Find position of highest set bit (this is the unbiased exponent) */
  pos = 0;
  {
    unsigned tmp = absVal;
    while (tmp >> 1) {
      tmp = tmp >> 1;
      pos = pos + 1;
    }
  }

  /* Biased exponent: position + 127 */
  exp = (pos + 127) << 23;

  /*
   * Build the 23-bit fraction.
   * The highest bit is implicit (the "1." in 1.fraction), so we drop it.
   *
   * If pos <= 23: shift LEFT to fill 23 fraction bits. No rounding needed.
   * If pos > 23:  shift RIGHT, losing bits. Must round.
   */
  if (pos <= 23) {
    frac = (absVal << (23 - pos)) & 0x7FFFFF;
  } else {
    /* Bits we're dropping */
    unsigned dropBits = pos - 23;

    frac = (absVal >> dropBits) & 0x7FFFFF;

    /*
     * Round-to-even logic:
     * - round_bit: the most significant bit being dropped (the "halfway" bit)
     * - sticky_bits: OR of all bits below the round bit (any extra precision?)
     * - If round_bit=1 AND (sticky_bits OR last kept bit is odd) → round up
     *   This implements "round to even" aka banker's rounding.
     */
    round_bit = (absVal >> (dropBits - 1)) & 1;
    sticky_bits = absVal & ((1 << (dropBits - 1)) - 1);
    halfway = round_bit && (sticky_bits || (frac & 1));

    frac = frac + halfway;

    /* If rounding overflows the fraction (0x7FFFFF → 0x800000), bump exponent */
    if (frac >> 23) {
      exp = exp + (1 << 23);
      frac = 0;
    }
  }

  return sign | exp | frac;
}
/* 
 * float_twice - Return bit-level equivalent of expression 2*f for
 *   floating point argument f.
 *   Both the argument and result are passed as unsigned int's, but
 *   they are to be interpreted as the bit-level representation of
 *   single-precision floating point values.
 *   When argument is NaN, return argument
 *   Legal ops: Any integer/unsigned operations incl. ||, &&. also if, while
 *   Max ops: 30
 *   Rating: 4
 */
unsigned float_twice(unsigned uf) {
  /*
   * Multiply a float by 2. Three cases based on the exponent:
   *
   * IEEE 754 layout: [sign(1)] [exponent(8)] [fraction(23)]
   *
   * Case 1: NaN or Infinity (exp == 0xFF)
   *   Return unchanged. 2 * inf = inf, 2 * NaN = NaN.
   *
   * Case 2: Denormalized number (exp == 0x00)
   *   Denormals represent very small numbers near zero.
   *   Value = (-1)^sign * 0.fraction * 2^(-126)
   *   To double it: shift the fraction left by 1 (multiply mantissa by 2).
   *   If this causes the fraction to overflow into the exponent field,
   *   that's actually correct — the number naturally "graduates" to a
   *   normalized number. The sign bit is preserved by masking.
   *
   *   Example: uf = 0x00400000 (denorm, frac = 0x400000)
   *     frac << 1 = 0x800000, which sets bit 23 (the exponent's LSB).
   *     Result: 0x00800000 — now a normalized number with exp=1. Correct! ✓
   *
   * Case 3: Normalized number (0 < exp < 0xFF)
   *   Value = (-1)^sign * 1.fraction * 2^(exp-127)
   *   To double it: add 1 to the exponent (multiplies by 2).
   *   If exponent becomes 0xFF, it becomes infinity — which is correct
   *   for overflow.
   *
   *   Example: uf = 0x3F800000 (1.0: sign=0, exp=127, frac=0)
   *     exp + 1 = 128, result = 0x40000000 (2.0) ✓
   */
  unsigned sign = uf & (1 << 31);
  unsigned exp = (uf >> 23) & 0xFF;
  unsigned frac = uf & 0x7FFFFF;

  if (exp == 0xFF) {
    /* NaN or infinity — return unchanged */
    return uf;
  } else if (exp == 0) {
    /* Denormalized: double the fraction (shift left), keep sign */
    return sign | (frac << 1);
  } else {
    /* Normalized: increment exponent (doubles the value) */
    return sign | ((exp + 1) << 23) | frac;
  }
}
