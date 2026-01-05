"""
Jack Tokenizer - Lexical Analysis for Jack Language

This module breaks Jack source code into tokens, removing comments
and whitespace while categorizing each token type.

Token Types:
- KEYWORD: class, constructor, function, method, field, static, var, int,
  char, boolean, void, true, false, null, this, let, do, if, else, while, return
- SYMBOL: { } ( ) [ ] . , ; + - * / & | < > = ~
- IDENTIFIER: variable/class/method names
- INT_CONST: integer constants (0-32767)
- STRING_CONST: string constants (not including quotes)
"""

import re


class JackTokenizer:
    """Lexical analyzer for Jack language."""

    # Token type constants
    KEYWORD = 'KEYWORD'
    SYMBOL = 'SYMBOL'
    IDENTIFIER = 'IDENTIFIER'
    INT_CONST = 'INT_CONST'
    STRING_CONST = 'STRING_CONST'

    # Jack keywords
    KEYWORDS = {
        'class', 'constructor', 'function', 'method', 'field', 'static',
        'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null',
        'this', 'let', 'do', 'if', 'else', 'while', 'return'
    }

    # Jack symbols
    SYMBOLS = {
        '{', '}', '(', ')', '[', ']', '.', ',', ';',
        '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'
    }

    def __init__(self, input_file):
        """Initialize tokenizer with Jack source file.

        Args:
            input_file: Path to .jack source file
        """
        with open(input_file, 'r') as f:
            self.source = f.read()

        # Remove comments and tokenize
        self.source = self._remove_comments(self.source)
        self.tokens = self._tokenize(self.source)
        self.current_token = None
        self.current_index = -1

    def _remove_comments(self, source):
        """Remove single-line and multi-line comments.

        Args:
            source: Jack source code string

        Returns:
            Source code with comments removed
        """
        # Remove multi-line comments /* ... */
        source = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)

        # Remove single-line comments //
        source = re.sub(r'//.*', '', source)

        return source

    def _tokenize(self, source):
        """Break source into tokens.

        Args:
            source: Comment-free Jack source code

        Returns:
            List of token strings
        """
        tokens = []
        i = 0

        while i < len(source):
            char = source[i]

            # Skip whitespace
            if char.isspace():
                i += 1
                continue

            # String constant
            if char == '"':
                j = i + 1
                while j < len(source) and source[j] != '"':
                    j += 1
                tokens.append(source[i:j+1])  # Include quotes
                i = j + 1
                continue

            # Symbol
            if char in self.SYMBOLS:
                tokens.append(char)
                i += 1
                continue

            # Integer constant or identifier/keyword
            if char.isdigit() or char.isalpha() or char == '_':
                j = i
                while j < len(source) and (source[j].isalnum() or source[j] == '_'):
                    j += 1
                tokens.append(source[i:j])
                i = j
                continue

            # Unknown character - skip
            i += 1

        return tokens

    def has_more_tokens(self):
        """Check if more tokens are available.

        Returns:
            True if more tokens exist
        """
        return self.current_index + 1 < len(self.tokens)

    def advance(self):
        """Move to next token (should only be called if has_more_tokens is true)."""
        self.current_index += 1
        self.current_token = self.tokens[self.current_index]

    def token_type(self):
        """Get type of current token.

        Returns:
            Token type constant (KEYWORD, SYMBOL, etc.)
        """
        token = self.current_token

        # String constant
        if token.startswith('"'):
            return self.STRING_CONST

        # Keyword
        if token in self.KEYWORDS:
            return self.KEYWORD

        # Symbol
        if token in self.SYMBOLS:
            return self.SYMBOL

        # Integer constant
        if token.isdigit():
            return self.INT_CONST

        # Identifier
        return self.IDENTIFIER

    def keyword(self):
        """Get keyword value (only call if token_type is KEYWORD).

        Returns:
            Keyword string
        """
        return self.current_token

    def symbol(self):
        """Get symbol character (only call if token_type is SYMBOL).

        Returns:
            Symbol character
        """
        return self.current_token

    def identifier(self):
        """Get identifier string (only call if token_type is IDENTIFIER).

        Returns:
            Identifier string
        """
        return self.current_token

    def int_val(self):
        """Get integer value (only call if token_type is INT_CONST).

        Returns:
            Integer value (0-32767)
        """
        return int(self.current_token)

    def string_val(self):
        """Get string value without quotes (only call if token_type is STRING_CONST).

        Returns:
            String value (without surrounding quotes)
        """
        return self.current_token[1:-1]  # Remove quotes
