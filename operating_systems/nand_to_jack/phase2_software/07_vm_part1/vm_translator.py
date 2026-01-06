from code_generator import CodeGenerator
from parser import Parser

class VMTranslator:
    """Main VM-to-Assembly translator"""

    def __init__(self, input_file):
        self.input_file = input_file
        self.output_file = input_file.replace('.vm', '.asm')
        self.parser = Parser(input_file)

        # Extract filename for static scope
        filename = input_file.split('/')[-1]
        self.code_gen = CodeGenerator(filename)

    def translate(self):
        """Translate entire VM file to assembly"""
        with open(self.output_file, 'w') as out:
            # Write bootstrap code
            out.write(self.code_gen.init())

            # Translate each VM command
            while self.parser.has_more_commands():
                self.parser.advance()
                if self.parser.current_command:
                    asm = self.code_gen.generate(self.parser.current_command)
                    out.write(asm)

def main():
    """Command-line interface for VM translator"""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python vm_translator.py <file.vm>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not input_file.endswith('.vm'):
        print("Error: Input file must have .vm extension")
        sys.exit(1)

    print(f"Translating {input_file}...")
    translator = VMTranslator(input_file)
    translator.translate()
    print(f"Generated {translator.output_file}")

if __name__ == '__main__':
    main()