#!/usr/bin/env python3
"""
Hack Assembler - Command-line driver
Usage:
  ./assembler_cli.py input.asm [output.hack] [--debug] [--run [max_cycles]]

Examples:
  ./assembler_cli.py program.asm                    # Assemble only
  ./assembler_cli.py program.asm --debug            # Assemble with debug output
  ./assembler_cli.py program.asm --run              # Assemble and run on CPU
  ./assembler_cli.py program.asm --run 100          # Assemble and run for 100 cycles
"""

import sys
from pathlib import Path
from assembler import Assembler

# Import CPU from Project 5 (Phase 1)
sys.path.append(str(Path(__file__).parent.parent.parent / 'phase1_hardware' / '05_computer_architecture'))
try:
    from computer_architecture import CPU  # type: ignore
    CPU_AVAILABLE = True
except ImportError:
    CPU_AVAILABLE = False


def main():
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: assembler_cli.py input.asm [output.hack] [--debug] [--run [max_cycles]]")
        print("\nExamples:")
        print("  ./assembler_cli.py program.asm                    # Assemble only")
        print("  ./assembler_cli.py program.asm --debug            # Assemble with debug output")
        print("  ./assembler_cli.py program.asm --run              # Assemble and run on CPU")
        print("  ./assembler_cli.py program.asm --run 100          # Run for 100 cycles")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = input_file.replace('.asm', '.hack')

    # Parse flags
    debug = False
    run_cpu = False
    max_cycles = None

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg == '--debug':
            debug = True
        elif arg == '--run':
            run_cpu = True
            # Check if next arg is a number
            if i + 1 < len(sys.argv) and sys.argv[i + 1].isdigit():
                max_cycles = int(sys.argv[i + 1])
                i += 1
        elif not arg.startswith('--'):
            output_file = arg

        i += 1

    # Assemble
    print(f"Assembling {input_file}...")

    assembler = Assembler()
    try:
        binary = assembler.assemble(input_file, output_file, debug=debug)
        print(f"Output written to {output_file}")

        # Run on CPU if requested
        if run_cpu:
            if not CPU_AVAILABLE:
                print("\n✗ CPU not available. Make sure Phase 1 Project 5 is implemented.")
                sys.exit(1)

            print(f"\n{'='*60}")
            print("Running on CPU...")
            print(f"{'='*60}")

            cpu = CPU()
            cpu.load_program(binary)

            if max_cycles:
                cpu.run(max_cycles=max_cycles)
                print(f"\n✓ Executed {max_cycles} cycles")
            else:
                # Run until infinite loop detected (same PC twice)
                cycles = 0
                prev_pc = -1
                max_default = 10000

                while cycles < max_default:
                    if cpu.PC == prev_pc:
                        print(f"\n✓ Infinite loop detected at PC={cpu.PC}, stopping after {cycles} cycles")
                        break
                    prev_pc = cpu.PC
                    cpu.step()
                    cycles += 1

                if cycles >= max_default:
                    print(f"\n⚠ Reached maximum {max_default} cycles")

            # Show key memory locations
            print(f"\n{'='*60}")
            print("CPU State:")
            print(f"{'='*60}")
            print(f"  A  = {cpu.A}")
            print(f"  D  = {cpu.D}")
            print(f"  PC = {cpu.PC}")

            print(f"\n{'='*60}")
            print("Memory (non-zero values):")
            print(f"{'='*60}")
            for addr in range(100):  # Check first 100 addresses
                if cpu.ram[addr] != 0:
                    print(f"  RAM[{addr}] = {cpu.ram[addr]}")

    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
