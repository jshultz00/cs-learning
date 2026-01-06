"""
VM Writer - VM code generation for Jack compiler

This module provides an abstraction layer for emitting VM commands.
All VM code generation goes through this interface.

VM Command Types:
- Arithmetic: add, sub, neg, eq, gt, lt, and, or, not
- Memory: push <segment> <index>, pop <segment> <index>
- Program flow: label <label>, goto <label>, if-goto <label>
- Function: function <name> <nLocals>, call <name> <nArgs>, return
"""


class VMWriter:
    """Generates VM commands and writes to output file."""

    def __init__(self, output_file):
        """Initialize with output file path.

        Args:
            output_file: Path to .vm output file
        """
        self.output_file = output_file
        self.commands = []

    def write_push(self, segment, index):
        """Write push command.

        Args:
            segment: Memory segment ('constant', 'local', 'argument', 'this',
                    'that', 'temp', 'pointer', 'static')
            index: Segment index (non-negative integer)
        """
        self.commands.append(f'push {segment} {index}')

    def write_pop(self, segment, index):
        """Write pop command.

        Args:
            segment: Memory segment ('local', 'argument', 'this', 'that',
                    'temp', 'pointer', 'static')
            index: Segment index (non-negative integer)

        Note: Cannot pop to 'constant' segment
        """
        self.commands.append(f'pop {segment} {index}')

    def write_arithmetic(self, command):
        """Write arithmetic/logical command.

        Args:
            command: One of 'add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not'
        """
        valid_commands = {'add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not'}
        if command not in valid_commands:
            raise ValueError(f'Invalid arithmetic command: {command}')

        self.commands.append(command)

    def write_label(self, label):
        """Write label command.

        Args:
            label: Label name (used for control flow)
        """
        self.commands.append(f'label {label}')

    def write_goto(self, label):
        """Write unconditional goto command.

        Args:
            label: Label name to jump to
        """
        self.commands.append(f'goto {label}')

    def write_if(self, label):
        """Write conditional if-goto command.

        Pops top of stack; if non-zero, jumps to label.

        Args:
            label: Label name to jump to if condition is true
        """
        self.commands.append(f'if-goto {label}')

    def write_call(self, name, n_args):
        """Write function call.

        Args:
            name: Function name (e.g., 'Math.multiply', 'String.appendChar')
            n_args: Number of arguments already pushed onto stack
        """
        self.commands.append(f'call {name} {n_args}')

    def write_function(self, name, n_locals):
        """Write function declaration.

        Args:
            name: Function name (e.g., 'Main.main', 'Point.distance')
            n_locals: Number of local variables to allocate
        """
        self.commands.append(f'function {name} {n_locals}')

    def write_return(self):
        """Write return command.

        Returns from current function, popping return value onto caller's stack.
        """
        self.commands.append('return')

    def write_comment(self, comment):
        """Write comment to VM file (for debugging).

        Args:
            comment: Comment text (// will be prepended)
        """
        self.commands.append(f'// {comment}')

    def close(self):
        """Write all commands to file and close."""
        with open(self.output_file, 'w') as f:
            f.write('\n'.join(self.commands) + '\n')

    def get_output(self):
        """Get generated VM code as string (for testing).

        Returns:
            All VM commands as single string
        """
        return '\n'.join(self.commands) + '\n'
