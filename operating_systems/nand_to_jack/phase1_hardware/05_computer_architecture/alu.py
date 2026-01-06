"""
ALU (Arithmetic Logic Unit) - Performs all arithmetic and logical operations
"""

class ALU:
    """
    Arithmetic Logic Unit for the Hack computer.

    Performs computation based on 6-bit comp field from C-instructions.
    Supports arithmetic operations (addition, subtraction, increment, decrement),
    bitwise operations (AND, OR, NOT), and constant generation.
    """

    def compute(self, comp_bits, d_val, ay_val):
        """
        Perform ALU operation based on comp bits (6-bit comp field, no a-bit).

        Args:
            comp_bits: 6-bit value specifying the operation
            d_val: Value from D register
            ay_val: Value from A register or RAM[A] (determined by a-bit in CPU)

        Returns:
            16-bit result of the computation (unsigned)
        """
        # Helper to convert to signed 16-bit
        def to_signed(val):
            val = val & 0xFFFF
            return val if val < 0x8000 else val - 0x10000

        # Helper to convert back to unsigned 16-bit
        def to_unsigned(val):
            return val & 0xFFFF

        operations = {
            # Constants
            0b101010: lambda d, a: 0,                           # 0
            0b111111: lambda d, a: 1,                           # 1
            0b111010: lambda d, a: -1,                          # -1

            # Pass-through
            0b001100: lambda d, a: d,                           # D
            0b110000: lambda d, a: a,                           # A or M

            # Bitwise NOT
            0b001101: lambda d, a: ~d,                          # !D
            0b110001: lambda d, a: ~a,                          # !A or !M

            # Arithmetic negate (two's complement)
            0b001111: lambda d, a: -to_signed(d),               # -D
            0b110011: lambda d, a: -to_signed(a),               # -A or -M

            # Increment
            0b011111: lambda d, a: to_signed(d) + 1,            # D+1
            0b110111: lambda d, a: to_signed(a) + 1,            # A+1 or M+1

            # Decrement
            0b001110: lambda d, a: to_signed(d) - 1,            # D-1
            0b110010: lambda d, a: to_signed(a) - 1,            # A-1 or M-1

            # Addition
            0b000010: lambda d, a: to_signed(d) + to_signed(a), # D+A or D+M

            # Subtraction
            0b010011: lambda d, a: to_signed(d) - to_signed(a), # D-A or D-M
            0b000111: lambda d, a: to_signed(a) - to_signed(d), # A-D or M-D

            # Bitwise operations
            0b000000: lambda d, a: d & a,                       # D&A or D&M
            0b010101: lambda d, a: d | a,                       # D|A or D|M
        }

        result = operations[comp_bits](d_val, ay_val)
        return to_unsigned(result)
