from logic_gates import *

def half_adder(a, b):
    """
    Sum: a XOR b (true when inputs differ)
    Carry: a AND b (true when both inputs are 1)
    """
    sum_bit = XOR(a, b)
    carry = AND(a, b)
    return sum_bit, carry

def full_adder(a, b, carry_in):
    """
    Built from two half adders:
    1. Add a + b
    2. Add that sum + carry_in
    Carry out if either stage produces carry
    """
    sum1, carry1 = half_adder(a, b)
    sum2, carry2 = half_adder(sum1, carry_in)
    carry_out = OR(carry1, carry2)
    return sum2, carry_out

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

def negate16(a):
    """
    1. Invert all bits (using NOT16)
    2. Add 1
    """
    inverted = not16(a)
    one = [0] * 15 + [1] # Binary representation of 1
    negated, _ = add16(inverted, one)
    return negated

def sub16(a, b):
    """Subtraction is addition of negation: a - b = a + (-b)"""
    return add16(a, negate16(b))

def alu(x, y, zx, nx, zy, ny, f, no):
    """
    Control bits determine operation:
    zx: zero the x input
    nx: negate the x input
    zy: zero the y input
    ny: negate the y input
    f:  function (1=add, 0=and)
    no: negate the output

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
    ng = out[0] == 1  # Output is negative (MSB set at index 0)

    return out, zr, ng

def to16(x):
    return [(x >> (15 - i)) & 1 for i in range(16)]

def from16(bits):
    val = 0
    for i, bit in enumerate(bits):
        val |= bit << (15 - i)
    if bits[0] == 1:
        val -= 1 << 16
    return val

def calculator():
    print("Binary Calculator (16-bit two's complement)")

    while True:
        cmd = input("> ").strip()

        if cmd in ("quit", "q"):
            break

        elif cmd == "add":
            x = to16(int(input("x: ")))
            y = to16(int(input("y: ")))
            out, zr, ng = alu(x, y, 0,0,0,0,1,0)
            print(f"Operation: {from16(x)} + {from16(y)}")
            print(f"Result: {from16(out)}")
            print(f"Zero flag: {zr}")
            print(f"Negative flag: {ng}")

        elif cmd == "sub":
            x = to16(int(input("x: ")))
            y = to16(int(input("y: ")))
            out, zr, ng = alu(x, y, 0,1,0,0,1,1)
            print(f"Operation: {from16(x)} - {from16(y)}")
            print(f"Result: {from16(out)}")
            print(f"Zero flag: {zr}")
            print(f"Negative flag: {ng}")

        elif cmd == "and":
            x = to16(int(input("x: ")))
            y = to16(int(input("y: ")))
            out, zr, ng = alu(x, y, 0,0,0,0,0,0)
            print(f"Operation: {x} & {y}")
            print(f"Result: {from16(out)} / {out}")
            print(f"Zero flag: {zr}")
            print(f"Negative flag: {ng}")

        elif cmd == "or":
            x = to16(int(input("x: ")))
            y = to16(int(input("y: ")))
            out, zr, ng = alu(x, y, 0,1,0,1,0,1)
            print(f"Operation: {x} | {y}")
            print(f"Result: {from16(out)} / {out}")
            print(f"Zero flag: {zr}")
            print(f"Negative flag: {ng}")

        elif cmd == "not":
            x = to16(int(input("x: ")))
            out, zr, ng = alu(x, to16(0), 0,1,1,1,0,0)
            print(f"Operation: !{from16(x)} / !{x}")
            print(f"Result: {from16(out)} / {out}")
            print(f"Zero flag: {zr}")
            print(f"Negative flag: {ng}")

        elif cmd == "neg":
            x = to16(int(input("x: ")))
            out, zr, ng = alu(x, to16(1), 0,1,0,0,1,0)
            print(f"Operation: -{x}")
            print(f"Result: {from16(out)} / {out}")
            print(f"Zero flag: {zr}")
            print(f"Negative flag: {ng}")

        elif cmd == "inc":
            x = to16(int(input("x: ")))
            out, zr, ng = alu(x, to16(1), 0,0,0,0,1,0)
            print(f"Operation: {x} + 1")
            print(f"Result: {from16(out)} / {out}")
            print(f"Zero flag: {zr}")
            print(f"Negative flag: {ng}")

        elif cmd == "dec":
            x = to16(int(input("x: ")))
            out, zr, ng = alu(x, to16(1), 0,1,0,0,1,1)
            print(f"Operation: {x} - 1")
            print(f"Result: {from16(out)} / {out}")
            print(f"Zero flag: {zr}")
            print(f"Negative flag: {ng}")

calculator()