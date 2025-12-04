"""
ROM (Read-Only Memory) - Instruction storage
"""

class ROM:
    """
    Read-Only Memory for the Hack computer.

    Stores program instructions loaded at initialization.
    In real hardware, ROM cannot be modified during execution,
    but we allow loading programs for simulation purposes.
    """

    def __init__(self, size=32768):
        """
        Initialize ROM with specified size.

        Args:
            size: Number of 16-bit instruction words (default: 32768 = 32K)
        """
        self.size = size
        self.memory = [0] * size

    def load_program(self, binary_instructions):
        """
        Load program into ROM from binary instruction strings.

        Args:
            binary_instructions: List of 16-bit binary strings (e.g., ["0000000000000000", "1110110000010000"])
        """
        for i, instruction in enumerate(binary_instructions):
            if i >= self.size:
                break
            self.memory[i] = int(instruction, 2)

    def load_program_binary(self, instructions):
        """
        Load program into ROM from integer values.

        Args:
            instructions: List of 16-bit integers
        """
        for i, instruction in enumerate(instructions):
            if i >= self.size:
                break
            self.memory[i] = instruction & 0xFFFF

    def fetch(self, address):
        """
        Fetch instruction at specified address.

        Args:
            address: Instruction address (0 to size-1)

        Returns:
            16-bit instruction at that address
        """
        if 0 <= address < self.size:
            return self.memory[address]
        return 0

    def __getitem__(self, address):
        """Allow array-style access: rom[address]"""
        return self.fetch(address)

    def reset(self):
        """Clear all instructions to zero"""
        self.memory = [0] * self.size
