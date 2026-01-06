# Import your CPU from Project 5
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / 'phase1_hardware' / '05_computer_architecture'))
from computer_architecture import CPU  # type: ignore

# Import your assembler from Project 6
from assembler import Assembler



# Assemble to binary
assembler = Assembler()
binary = assembler.assemble('program.asm', 'program.hack')

# Load into CPU
cpu = CPU()
cpu.load_program(binary)

# Execute
cpu.run(max_cycles=10)

# Check result
print(f"RAM[0] = {cpu.ram[0]}")  # Should be 15 (5 + 10)