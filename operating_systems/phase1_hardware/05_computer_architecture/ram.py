"""
RAM (Random Access Memory) - Data storage
"""

class RAM:
    """
    Random Access Memory for the Hack computer.

    Provides addressable storage for data during program execution.
    Supports read and write operations at any valid address.
    """

    def __init__(self, size=32768):
        """
        Initialize RAM with specified size.

        Args:
            size: Number of 16-bit words (default: 32768 = 32K)
        """
        self.size = size
        self.memory = [0] * size

    def read(self, address):
        """
        Read value at specified address.

        Args:
            address: Memory address to read from (0 to size-1)

        Returns:
            16-bit value at that address
        """
        if 0 <= address < self.size:
            return self.memory[address]
        return 0

    def write(self, address, value):
        """
        Write value to specified address.

        Args:
            address: Memory address to write to (0 to size-1)
            value: 16-bit value to store
        """
        if 0 <= address < self.size:
            self.memory[address] = value & 0xFFFF

    def __getitem__(self, address):
        """Allow array-style access: ram[address]"""
        return self.read(address)

    def __setitem__(self, address, value):
        """Allow array-style assignment: ram[address] = value"""
        self.write(address, value)

    def reset(self):
        """Clear all memory to zero"""
        self.memory = [0] * self.size
