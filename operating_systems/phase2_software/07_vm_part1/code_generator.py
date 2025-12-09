class CodeGenerator:
    """Generate Hack assembly from VM commands"""

    def __init__(self):
        self.label_counter = 0  # For unique labels in comparisons

    def init(self):
        """Bootstrap code: initialize stack pointer"""
        return (
            "// Bootstrap: Initialize SP to 256\n"
            "@256\n"
            "D=A\n"
            "@SP\n"
            "M=D\n"
        )

    def generate(self, command):
        """Generate assembly for one VM command"""
        if command['type'] == 'arithmetic':
            return self.generate_arithmetic(command['operation'])
        elif command['type'] == 'push':
            return self.generate_push(command['segment'], command['index'])
        elif command['type'] == 'pop':
            return self.generate_pop(command['segment'], command['index'])

    def generate_arithmetic(self, operation):
        """Generate assembly for arithmetic/logical operations"""
        # TODO: Implement in Step 2
        pass

    def generate_push(self, segment, index):
        """Generate assembly for push commands"""
        # TODO: Implement in Step 3
        pass

    def generate_pop(self, segment, index):
        """Generate assembly for pop commands"""
        # TODO: Implement in Step 3
        pass