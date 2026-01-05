"""
Symbol Table - Variable tracking for Jack compiler

This module implements a two-level symbol table for tracking variables:
- Class-level: field and static variables
- Subroutine-level: local and argument variables

Each variable is tracked with:
- name: Variable identifier
- type: Data type (int, char, boolean, or class name)
- kind: field, static, local, or argument
- index: Zero-based index within its kind
"""


class SymbolTable:
    """Two-level symbol table for Jack compiler."""

    def __init__(self):
        """Initialize class-level and subroutine-level tables."""
        self.class_table = {}        # Fields and statics (persistent across subroutines)
        self.subroutine_table = {}   # Locals and arguments (reset per subroutine)
        self.indexes = {
            'field': 0,
            'static': 0,
            'local': 0,
            'argument': 0
        }

    def start_subroutine(self):
        """Start new subroutine scope (clear subroutine table).

        Resets subroutine-level variables and indexes for new method/function/constructor.
        Class-level variables (fields and statics) persist.
        """
        self.subroutine_table = {}
        self.indexes['local'] = 0
        self.indexes['argument'] = 0

    def define(self, name, var_type, kind):
        """Add variable to appropriate table.

        Args:
            name: Variable name (identifier)
            var_type: Variable type (int, char, boolean, or class name)
            kind: 'field', 'static', 'local', or 'argument'
        """
        if kind not in {'field', 'static', 'local', 'argument'}:
            raise ValueError(f'Invalid kind: {kind}')

        index = self.indexes[kind]
        entry = {
            'type': var_type,
            'kind': kind,
            'index': index
        }

        # Add to appropriate table
        if kind in ('field', 'static'):
            self.class_table[name] = entry
        else:  # local or argument
            self.subroutine_table[name] = entry

        # Increment index for this kind
        self.indexes[kind] += 1

    def var_count(self, kind):
        """Get count of variables of given kind.

        Args:
            kind: 'field', 'static', 'local', or 'argument'

        Returns:
            Number of variables of that kind defined so far
        """
        return self.indexes[kind]

    def kind_of(self, name):
        """Get kind of named variable.

        Args:
            name: Variable name

        Returns:
            'field', 'static', 'local', 'argument', or None if not found
        """
        # Check subroutine table first (shadows class-level)
        if name in self.subroutine_table:
            return self.subroutine_table[name]['kind']
        elif name in self.class_table:
            return self.class_table[name]['kind']
        return None

    def type_of(self, name):
        """Get type of named variable.

        Args:
            name: Variable name

        Returns:
            Type string (int, char, boolean, or class name), or None if not found
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name]['type']
        elif name in self.class_table:
            return self.class_table[name]['type']
        return None

    def index_of(self, name):
        """Get index of named variable within its kind.

        Args:
            name: Variable name

        Returns:
            Zero-based index within its segment, or None if not found
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name]['index']
        elif name in self.class_table:
            return self.class_table[name]['index']
        return None

    def __str__(self):
        """String representation for debugging."""
        result = ['Symbol Table:']
        result.append('\nClass-level variables:')
        for name, entry in self.class_table.items():
            result.append(f'  {name}: {entry["type"]} ({entry["kind"]} {entry["index"]})')

        result.append('\nSubroutine-level variables:')
        for name, entry in self.subroutine_table.items():
            result.append(f'  {name}: {entry["type"]} ({entry["kind"]} {entry["index"]})')

        return '\n'.join(result)
