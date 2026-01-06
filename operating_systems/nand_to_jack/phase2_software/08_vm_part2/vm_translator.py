import os
import glob
from code_generator import CodeGenerator
from parser import Parser

class VMTranslator:
    """Main VM-to-Assembly translator with multi-file support"""

    def __init__(self, input_path):
        self.input_path = input_path

        # Determine if input is file or directory
        if os.path.isfile(input_path):
            # Single file
            self.vm_files = [input_path]
            self.output_file = input_path.replace('.vm', '.asm')
        elif os.path.isdir(input_path):
            # Directory: find all .vm files
            self.vm_files = sorted(glob.glob(os.path.join(input_path, '*.vm')))
            if not self.vm_files:
                raise ValueError(f"No .vm files found in directory: {input_path}")
            # Output file named after directory
            dir_name = os.path.basename(input_path.rstrip('/'))
            self.output_file = os.path.join(input_path, f"{dir_name}.asm")
        else:
            raise ValueError(f"Invalid input path: {input_path}")

        self.code_gen = CodeGenerator()

    def translate(self):
        """Translate all VM files to single assembly file"""
        with open(self.output_file, 'w') as out:
            # Write bootstrap code (only once for entire program)
            out.write(self.code_gen.init())

            # Translate each VM file
            for vm_file in self.vm_files:
                # Extract filename for static scoping
                filename = os.path.basename(vm_file)
                self.code_gen.current_file = filename.replace('.vm', '')

                # Add file header comment
                out.write(f"\n// ===== File: {filename} =====\n")

                # Parse and translate file
                parser = Parser(vm_file)
                while parser.has_more_commands():
                    parser.advance()
                    if parser.current_command:
                        asm = self.code_gen.generate(parser.current_command)
                        out.write(asm)

def main():
    """Command-line interface for VM translator"""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python vm_translator.py <file.vm|directory>")
        sys.exit(1)

    input_path = sys.argv[1]

    print(f"Translating {input_path}...")
    translator = VMTranslator(input_path)
    translator.translate()
    print(f"Generated {translator.output_file}")

if __name__ == '__main__':
    main()
