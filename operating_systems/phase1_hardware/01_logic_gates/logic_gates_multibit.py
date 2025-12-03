from logic_gates import *

def not16(a):
    """Apply NOT to 16 bits in parallel"""
    return [NOT(bit) for bit in a]

def and16(a, b):
    """Apply AND to 16 bits in parallel"""
    return [AND(a[i], b[i]) for i in range(16)]

def or16(a, b):
    """Apply OR to 16 bits in parallel"""
    return [OR(a[i], b[i]) for i in range(16)]

def xor16(a, b):
    """Apply XOR to 16 bits in parallel"""
    return [XOR(a[i], b[i]) for i in range(16)]

def mux16(a, b, sel):
    """Apply MUX to 16 bits in parallel"""
    return [MUX(a[i], b[i], sel) for i in range(16)]

def dmux16(input, sel):
    """Apply DMUX to 16 bits in parallel"""
    return [DMUX(input[i], sel) for i in range(16)]
