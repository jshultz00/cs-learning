"""
Hack Computer Architecture - Main module
Imports and re-exports all components for easy use.

This file serves as a unified interface to the complete computer architecture.
Individual components are separated into their own modules for clarity:
- alu.py: Arithmetic Logic Unit
- ram.py: Random Access Memory
- rom.py: Read-Only Memory
- cpu.py: Central Processing Unit
- assembler.py: Assembly language assembler

Usage:
    from computer_architecture import CPU, Assembler

    # Create and use components
    cpu = CPU()
    assembler = Assembler()

    # Assemble and run a program
    program = ["@5", "D=A", "@10", "M=D"]
    binary = assembler.assemble(program)
    cpu.load_program(binary)
    cpu.run()
"""

# Import all components
from alu import ALU
from ram import RAM
from rom import ROM
from cpu import CPU
from assembler import Assembler

# Re-export for convenience
__all__ = ['ALU', 'RAM', 'ROM', 'CPU', 'Assembler']
