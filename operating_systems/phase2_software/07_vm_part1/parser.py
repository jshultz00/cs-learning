class Parser:
    """Parse VM commands from input file"""

    def __init__(self, input_file):
        with open(input_file, 'r') as f:
            self.lines = f.readlines()
        self.current_line = 0
        self.current_command = None

    def has_more_commands(self):
        """Are there more commands to parse?"""
        return self.current_line < len(self.lines)

    def advance(self):
        """Read next command, parse into components"""
        while self.has_more_commands():
            line = self.lines[self.current_line].strip()
            self.current_line += 1

            # Skip blank lines and comments
            if not line or line.startswith('//'):
                continue

            # Remove inline comments
            line = line.split('//')[0].strip()

            # Parse command
            self.current_command = self.parse_command(line)
            break

    def parse_command(self, line):
        """Parse command into {type, arg1, arg2}"""
        parts = line.split()
        cmd_type = parts[0]

        if cmd_type in ['add', 'sub', 'neg', 'eq', 'gt', 'lt',
                        'and', 'or', 'not']:
            return {'type': 'arithmetic', 'operation': cmd_type}

        elif cmd_type == 'push':
            return {'type': 'push', 'segment': parts[1], 'index': int(parts[2])}

        elif cmd_type == 'pop':
            return {'type': 'pop', 'segment': parts[1], 'index': int(parts[2])}

        else:
            raise ValueError(f"Unknown command: {cmd_type}")