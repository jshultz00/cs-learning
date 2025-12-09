from code_generator import CodeGenerator
from parser import Parser

class VMTranslator:
    """Main VM-to-Assembly translator"""

    def __init__(self, input_file):
        self.input_file = input_file
        self.output_file = input_file.replace('.vm', '.asm')
        self.parser = Parser(input_file)
        self.code_gen = CodeGenerator()

    def translate(self):
        """Translate entire VM file to assembly"""
        with open(self.output_file, 'w') as out:
            # Write bootstrap code
            out.write(self.code_gen.init())

            # Translate each VM command
            while self.parser.has_more_commands():
                self.parser.advance()
                asm = self.code_gen.generate(self.parser.current_command)
                out.write(asm)