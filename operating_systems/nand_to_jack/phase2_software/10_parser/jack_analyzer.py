#!/usr/bin/env python3
"""
Jack Analyzer - Main program for syntax analysis

Usage:
    python3 jack_analyzer.py <input>

    <input> can be:
    - A single .jack file (output: <filename>.xml)
    - A directory (processes all .jack files, outputs .xml files)

Examples:
    python3 jack_analyzer.py Square.jack
    python3 jack_analyzer.py examples/01_square/

Output:
    Creates .xml files with the same base name as input .jack files
"""

import sys
import os
from pathlib import Path
from parser import CompilationEngine


def analyze_file(jack_file):
    """Analyze a single Jack file.

    Args:
        jack_file: Path to .jack source file
    """
    # Create output filename
    xml_file = jack_file.replace('.jack', '.xml')

    print(f'Analyzing: {jack_file}')

    try:
        # Compile the file
        engine = CompilationEngine(jack_file, xml_file)
        engine.compile()
        print(f'  Output: {xml_file}')
    except SyntaxError as e:
        print(f'  ERROR: {e}')
    except Exception as e:
        print(f'  ERROR: {e}')


def analyze_directory(directory):
    """Analyze all .jack files in a directory.

    Args:
        directory: Path to directory containing .jack files
    """
    path = Path(directory)

    # Find all .jack files
    jack_files = sorted(path.glob('*.jack'))

    if not jack_files:
        print(f'No .jack files found in {directory}')
        return

    print(f'Found {len(jack_files)} Jack file(s) in {directory}\n')

    for jack_file in jack_files:
        analyze_file(str(jack_file))
        print()


def main():
    """Main program entry point."""
    if len(sys.argv) != 2:
        print('Usage: python3 jack_analyzer.py <input>')
        print()
        print('  <input> can be:')
        print('    - A single .jack file')
        print('    - A directory containing .jack files')
        sys.exit(1)

    input_path = sys.argv[1]

    # Check if input is a file or directory
    if os.path.isfile(input_path):
        if not input_path.endswith('.jack'):
            print(f'ERROR: Input file must have .jack extension')
            sys.exit(1)
        analyze_file(input_path)
    elif os.path.isdir(input_path):
        analyze_directory(input_path)
    else:
        print(f'ERROR: {input_path} is not a valid file or directory')
        sys.exit(1)


if __name__ == '__main__':
    main()
