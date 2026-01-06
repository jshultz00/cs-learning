"""
CPU (Central Processing Unit) - The brain of the computer
"""

from alu import ALU
from ram import RAM
from rom import ROM


class CPU:
    """
    Central Processing Unit for the Hack computer.

    Simulates the CPU executing instructions from ROM, manipulating registers,
    performing ALU operations, and reading/writing to RAM.

    Architecture:
    - Three registers: A (address/value), D (data), PC (program counter)
    - ALU for arithmetic and logic operations
    - RAM for data storage
    - ROM for instruction storage
    """

    def __init__(self, rom_size=32768, ram_size=32768):
        """
        Initialize CPU with specified memory sizes.

        Args:
            rom_size: Size of ROM (instruction memory)
            ram_size: Size of RAM (data memory)
        """
        # Registers
        self.A = 0          # Address register
        self.D = 0          # Data register
        self.PC = 0         # Program counter

        # Components
        self.ram = RAM(ram_size)
        self.rom = ROM(rom_size)
        self.alu = ALU()

    def load_program(self, binary_instructions):
        """
        Load program into ROM.

        Args:
            binary_instructions: List of 16-bit binary instruction strings
        """
        self.rom.load_program(binary_instructions)

    def fetch(self):
        """
        Fetch instruction from ROM[PC].

        Returns:
            16-bit instruction at current program counter
        """
        return self.rom[self.PC]

    def execute_a_instruction(self, instruction):
        """
        Execute A-instruction: @value

        Format: 0vvvvvvvvvvvvvvv
        - Bit 15 = 0 (instruction type)
        - Bits 0-14 = 15-bit value

        Effect: Load value into A register, increment PC

        Args:
            instruction: 16-bit instruction word
        """
        value = instruction & 0x7FFF  # Bottom 15 bits
        self.A = value
        self.PC += 1

    def execute_c_instruction(self, instruction):
        """
        Execute C-instruction: dest=comp;jump

        Format: 111accccccdddjjj
        - Bits 13-15 = 111 (instruction type)
        - Bit 12 (a) = 0 for A register, 1 for Memory[A]
        - Bits 6-11 (comp) = ALU operation
        - Bits 3-5 (dest) = destination (A, D, M or combinations)
        - Bits 0-2 (jump) = jump condition

        Args:
            instruction: 16-bit instruction word
        """
        # Decode instruction bits
        a_bit = (instruction >> 12) & 1 # 000000000000111a & 0000000000000001 = a (0 or 1)
        comp_bits = (instruction >> 6) & 0x3F # 000000111acccccc & 0000000000111111 = cccccc
        dest_bits = (instruction >> 3) & 0x7 # 000111accccccddd & 0000000000000111 = ddd
        jump_bits = instruction & 0x7 # 111accccccdddjjj & 0000000000000111 = jjj

        # Compute using ALU
        y = self.ram[self.A] if a_bit else self.A
        result = self.alu.compute(comp_bits, self.D, y)

        # Store result in destinations
        if dest_bits & 0x4:  # A bit set (ddd & 100 = 100)
            self.A = result
        if dest_bits & 0x2:  # D bit set (ddd & 010 = 010)
            self.D = result
        if dest_bits & 0x1:  # M bit set (ddd & 001 = 001)
            self.ram[self.A] = result

        # Handle jump
        if self.should_jump(jump_bits, result):
            self.PC = self.A
        else:
            self.PC += 1

    def should_jump(self, jump_bits, value):
        """
        Determine if jump condition is met based on ALU output.

        Jump conditions:
        - 000: No jump
        - 001: JGT (jump if > 0)
        - 010: JEQ (jump if = 0)
        - 011: JGE (jump if >= 0)
        - 100: JLT (jump if < 0)
        - 101: JNE (jump if != 0)
        - 110: JLE (jump if <= 0)
        - 111: JMP (unconditional)

        Args:
            jump_bits: 3-bit jump condition code
            value: 16-bit result from ALU

        Returns:
            True if should jump, False otherwise
        """
        if jump_bits == 0:  # No jump
            return False
        if jump_bits == 0b111:  # Unconditional
            return True

        # Check conditions
        is_negative = (value & 0x8000) != 0 # If MSB=1, the number is negative (i.e., 0b1111111111110101 = -(0b1010 + 1) = -0b1011 = -11 in decimal)
        is_zero = value == 0
        is_positive = not is_negative and not is_zero

        conditions = {
            0b001: is_positive,  # JGT
            0b010: is_zero,      # JEQ
            0b011: not is_negative,  # JGE
            0b100: is_negative,  # JLT
            0b101: not is_zero,  # JNE
            0b110: is_negative or is_zero,  # JLE
        }
        return conditions.get(jump_bits, False)

    def step(self):
        """
        Execute one instruction cycle.

        Returns:
            True if execution should continue, False if HALT encountered
        """
        instruction = self.fetch()

        # Check for HALT instruction (all 1s: 0xFFFF)
        if instruction == 0xFFFF:
            return False  # Signal to stop execution

        if instruction & 0x8000:  # C-instruction (bit 15 = 1)
            self.execute_c_instruction(instruction)
        else:  # A-instruction (bit 15 = 0)
            self.execute_a_instruction(instruction)

        return True  # Continue execution

    def run(self, max_cycles=1000):
        """
        Run program until halt or max cycles reached.

        Program halts when:
        - HALT instruction is encountered
        - PC points beyond ROM
        - Max cycles reached (prevents infinite loops)

        Note: @0 is a valid instruction (sets A=0), not a halt.
        Use the HALT instruction to explicitly stop program execution.

        Args:
            max_cycles: Maximum number of cycles to execute

        Returns:
            Tuple (halted, cycles_executed) where:
            - halted: True if HALT was encountered, False if stopped by other means
            - cycles_executed: Number of instruction cycles executed
        """
        for cycle in range(max_cycles):
            if self.PC >= self.rom.size:
                return (False, cycle)  # Stopped: PC beyond ROM

            continue_execution = self.step()
            if not continue_execution:
                return (True, cycle + 1)  # Stopped: HALT instruction

        return (False, max_cycles)  # Stopped: max cycles reached

    def reset(self):
        """Reset CPU to initial state."""
        self.A = 0
        self.D = 0
        self.PC = 0
        self.ram.reset()
