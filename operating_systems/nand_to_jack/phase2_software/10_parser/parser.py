"""
Jack Parser - Syntax Analysis for Jack Language

This module performs recursive descent parsing on tokenized Jack code,
generating an XML parse tree that represents the program structure.

Grammar (simplified):
- class: 'class' className '{' classVarDec* subroutineDec* '}'
- statements: statement*
- statement: letStatement | ifStatement | whileStatement | doStatement | returnStatement
- expression: term (op term)*
"""

from tokenizer import JackTokenizer


class CompilationEngine:
    """Recursive descent parser for Jack language."""

    # Operators
    OPS = {'+', '-', '*', '/', '&', '|', '<', '>', '='}

    # Unary operators
    UNARY_OPS = {'-', '~'}

    # Keyword constants
    KEYWORD_CONSTANTS = {'true', 'false', 'null', 'this'}

    def __init__(self, input_file, output_file):
        """Initialize parser with input and output files.

        Args:
            input_file: Path to .jack source file
            output_file: Path to output .xml file
        """
        self.tokenizer = JackTokenizer(input_file)
        self.output_file = output_file
        self.output_lines = []
        self.indent_level = 0

    def compile(self):
        """Compile the Jack source file."""
        self.tokenizer.advance()
        self.compile_class()
        self._write_to_file()

    def _write(self, line):
        """Write indented line to output.

        Args:
            line: XML line to write
        """
        indent = '  ' * self.indent_level
        self.output_lines.append(indent + line)

    def _write_to_file(self):
        """Write all output lines to file."""
        with open(self.output_file, 'w') as f:
            f.write('\n'.join(self.output_lines) + '\n')

    def _write_terminal(self):
        """Write current token as terminal element."""
        token_type = self.tokenizer.token_type()

        if token_type == JackTokenizer.KEYWORD:
            value = self.tokenizer.keyword()
            self._write(f'<keyword> {value} </keyword>')
        elif token_type == JackTokenizer.SYMBOL:
            value = self.tokenizer.symbol()
            # Escape XML special characters
            if value == '<':
                value = '&lt;'
            elif value == '>':
                value = '&gt;'
            elif value == '&':
                value = '&amp;'
            self._write(f'<symbol> {value} </symbol>')
        elif token_type == JackTokenizer.IDENTIFIER:
            value = self.tokenizer.identifier()
            self._write(f'<identifier> {value} </identifier>')
        elif token_type == JackTokenizer.INT_CONST:
            value = self.tokenizer.int_val()
            self._write(f'<integerConstant> {value} </integerConstant>')
        elif token_type == JackTokenizer.STRING_CONST:
            value = self.tokenizer.string_val()
            self._write(f'<stringConstant> {value} </stringConstant>')

    def _expect(self, expected):
        """Verify current token matches expected value and advance.

        Args:
            expected: Expected token string

        Raises:
            SyntaxError: If token doesn't match
        """
        token_type = self.tokenizer.token_type()

        if token_type == JackTokenizer.KEYWORD:
            actual = self.tokenizer.keyword()
        elif token_type == JackTokenizer.SYMBOL:
            actual = self.tokenizer.symbol()
        else:
            actual = self.tokenizer.current_token

        if actual != expected:
            raise SyntaxError(f'Expected "{expected}" but got "{actual}"')

        self._write_terminal()
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()

    def compile_class(self):
        """Compile a complete class.

        Grammar: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        self._write('<class>')
        self.indent_level += 1

        # 'class'
        self._expect('class')

        # className
        self._write_terminal()  # identifier
        self.tokenizer.advance()

        # '{'
        self._expect('{')

        # classVarDec*
        while (self.tokenizer.token_type() == JackTokenizer.KEYWORD and
               self.tokenizer.keyword() in {'static', 'field'}):
            self.compile_class_var_dec()

        # subroutineDec*
        while (self.tokenizer.token_type() == JackTokenizer.KEYWORD and
               self.tokenizer.keyword() in {'constructor', 'function', 'method'}):
            self.compile_subroutine()

        # '}'
        self._expect('}')

        self.indent_level -= 1
        self._write('</class>')

    def compile_class_var_dec(self):
        """Compile a static or field declaration.

        Grammar: ('static' | 'field') type varName (',' varName)* ';'
        """
        self._write('<classVarDec>')
        self.indent_level += 1

        # 'static' | 'field'
        self._write_terminal()
        self.tokenizer.advance()

        # type
        self._write_terminal()
        self.tokenizer.advance()

        # varName
        self._write_terminal()
        self.tokenizer.advance()

        # (',' varName)*
        while (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
               self.tokenizer.symbol() == ','):
            self._expect(',')
            self._write_terminal()  # varName
            self.tokenizer.advance()

        # ';'
        self._expect(';')

        self.indent_level -= 1
        self._write('</classVarDec>')

    def compile_subroutine(self):
        """Compile a method, function, or constructor.

        Grammar: ('constructor' | 'function' | 'method')
                ('void' | type) subroutineName '(' parameterList ')'
                subroutineBody
        """
        self._write('<subroutineDec>')
        self.indent_level += 1

        # 'constructor' | 'function' | 'method'
        self._write_terminal()
        self.tokenizer.advance()

        # 'void' | type
        self._write_terminal()
        self.tokenizer.advance()

        # subroutineName
        self._write_terminal()
        self.tokenizer.advance()

        # '('
        self._expect('(')

        # parameterList
        self.compile_parameter_list()

        # ')'
        self._expect(')')

        # subroutineBody
        self._write('<subroutineBody>')
        self.indent_level += 1

        # '{'
        self._expect('{')

        # varDec*
        while (self.tokenizer.token_type() == JackTokenizer.KEYWORD and
               self.tokenizer.keyword() == 'var'):
            self.compile_var_dec()

        # statements
        self.compile_statements()

        # '}'
        self._expect('}')

        self.indent_level -= 1
        self._write('</subroutineBody>')

        self.indent_level -= 1
        self._write('</subroutineDec>')

    def compile_parameter_list(self):
        """Compile a parameter list (possibly empty).

        Grammar: ((type varName) (',' type varName)*)?
        """
        self._write('<parameterList>')
        self.indent_level += 1

        # Check if parameter list is empty
        if not (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
                self.tokenizer.symbol() == ')'):
            # type
            self._write_terminal()
            self.tokenizer.advance()

            # varName
            self._write_terminal()
            self.tokenizer.advance()

            # (',' type varName)*
            while (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
                   self.tokenizer.symbol() == ','):
                self._expect(',')
                self._write_terminal()  # type
                self.tokenizer.advance()
                self._write_terminal()  # varName
                self.tokenizer.advance()

        self.indent_level -= 1
        self._write('</parameterList>')

    def compile_var_dec(self):
        """Compile a var declaration.

        Grammar: 'var' type varName (',' varName)* ';'
        """
        self._write('<varDec>')
        self.indent_level += 1

        # 'var'
        self._expect('var')

        # type
        self._write_terminal()
        self.tokenizer.advance()

        # varName
        self._write_terminal()
        self.tokenizer.advance()

        # (',' varName)*
        while (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
               self.tokenizer.symbol() == ','):
            self._expect(',')
            self._write_terminal()  # varName
            self.tokenizer.advance()

        # ';'
        self._expect(';')

        self.indent_level -= 1
        self._write('</varDec>')

    def compile_statements(self):
        """Compile a sequence of statements.

        Grammar: statement*
        """
        self._write('<statements>')
        self.indent_level += 1

        while (self.tokenizer.token_type() == JackTokenizer.KEYWORD and
               self.tokenizer.keyword() in {'let', 'if', 'while', 'do', 'return'}):
            keyword = self.tokenizer.keyword()

            if keyword == 'let':
                self.compile_let()
            elif keyword == 'if':
                self.compile_if()
            elif keyword == 'while':
                self.compile_while()
            elif keyword == 'do':
                self.compile_do()
            elif keyword == 'return':
                self.compile_return()

        self.indent_level -= 1
        self._write('</statements>')

    def compile_let(self):
        """Compile a let statement.

        Grammar: 'let' varName ('[' expression ']')? '=' expression ';'
        """
        self._write('<letStatement>')
        self.indent_level += 1

        # 'let'
        self._expect('let')

        # varName
        self._write_terminal()
        self.tokenizer.advance()

        # ('[' expression ']')?
        if (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
            self.tokenizer.symbol() == '['):
            self._expect('[')
            self.compile_expression()
            self._expect(']')

        # '='
        self._expect('=')

        # expression
        self.compile_expression()

        # ';'
        self._expect(';')

        self.indent_level -= 1
        self._write('</letStatement>')

    def compile_if(self):
        """Compile an if statement.

        Grammar: 'if' '(' expression ')' '{' statements '}'
                ('else' '{' statements '}')?
        """
        self._write('<ifStatement>')
        self.indent_level += 1

        # 'if'
        self._expect('if')

        # '('
        self._expect('(')

        # expression
        self.compile_expression()

        # ')'
        self._expect(')')

        # '{'
        self._expect('{')

        # statements
        self.compile_statements()

        # '}'
        self._expect('}')

        # ('else' '{' statements '}')?
        if (self.tokenizer.token_type() == JackTokenizer.KEYWORD and
            self.tokenizer.keyword() == 'else'):
            self._expect('else')
            self._expect('{')
            self.compile_statements()
            self._expect('}')

        self.indent_level -= 1
        self._write('</ifStatement>')

    def compile_while(self):
        """Compile a while statement.

        Grammar: 'while' '(' expression ')' '{' statements '}'
        """
        self._write('<whileStatement>')
        self.indent_level += 1

        # 'while'
        self._expect('while')

        # '('
        self._expect('(')

        # expression
        self.compile_expression()

        # ')'
        self._expect(')')

        # '{'
        self._expect('{')

        # statements
        self.compile_statements()

        # '}'
        self._expect('}')

        self.indent_level -= 1
        self._write('</whileStatement>')

    def compile_do(self):
        """Compile a do statement.

        Grammar: 'do' subroutineCall ';'
        """
        self._write('<doStatement>')
        self.indent_level += 1

        # 'do'
        self._expect('do')

        # subroutineCall: subroutineName '(' expressionList ')' |
        #                 (className | varName) '.' subroutineName '(' expressionList ')'
        self._write_terminal()  # identifier
        self.tokenizer.advance()

        # Check for '.' (method call)
        if (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
            self.tokenizer.symbol() == '.'):
            self._expect('.')
            self._write_terminal()  # subroutineName
            self.tokenizer.advance()

        # '('
        self._expect('(')

        # expressionList
        self.compile_expression_list()

        # ')'
        self._expect(')')

        # ';'
        self._expect(';')

        self.indent_level -= 1
        self._write('</doStatement>')

    def compile_return(self):
        """Compile a return statement.

        Grammar: 'return' expression? ';'
        """
        self._write('<returnStatement>')
        self.indent_level += 1

        # 'return'
        self._expect('return')

        # expression?
        if not (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
                self.tokenizer.symbol() == ';'):
            self.compile_expression()

        # ';'
        self._expect(';')

        self.indent_level -= 1
        self._write('</returnStatement>')

    def compile_expression(self):
        """Compile an expression.

        Grammar: term (op term)*
        """
        self._write('<expression>')
        self.indent_level += 1

        # term
        self.compile_term()

        # (op term)*
        while (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
               self.tokenizer.symbol() in self.OPS):
            self._write_terminal()  # op
            self.tokenizer.advance()
            self.compile_term()

        self.indent_level -= 1
        self._write('</expression>')

    def compile_term(self):
        """Compile a term.

        Grammar: integerConstant | stringConstant | keywordConstant |
                varName | varName '[' expression ']' | subroutineCall |
                '(' expression ')' | unaryOp term
        """
        self._write('<term>')
        self.indent_level += 1

        token_type = self.tokenizer.token_type()

        # integerConstant | stringConstant | keywordConstant
        if token_type in {JackTokenizer.INT_CONST, JackTokenizer.STRING_CONST}:
            self._write_terminal()
            self.tokenizer.advance()
        elif (token_type == JackTokenizer.KEYWORD and
              self.tokenizer.keyword() in self.KEYWORD_CONSTANTS):
            self._write_terminal()
            self.tokenizer.advance()
        # '(' expression ')'
        elif (token_type == JackTokenizer.SYMBOL and
              self.tokenizer.symbol() == '('):
            self._expect('(')
            self.compile_expression()
            self._expect(')')
        # unaryOp term
        elif (token_type == JackTokenizer.SYMBOL and
              self.tokenizer.symbol() in self.UNARY_OPS):
            self._write_terminal()  # unaryOp
            self.tokenizer.advance()
            self.compile_term()
        # varName | varName '[' expression ']' | subroutineCall
        elif token_type == JackTokenizer.IDENTIFIER:
            self._write_terminal()  # identifier
            self.tokenizer.advance()

            # varName '[' expression ']'
            if (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
                self.tokenizer.symbol() == '['):
                self._expect('[')
                self.compile_expression()
                self._expect(']')
            # subroutineCall: '(' expressionList ')' or '.' subroutineName '(' expressionList ')'
            elif (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
                  self.tokenizer.symbol() in {'(', '.'}):
                if self.tokenizer.symbol() == '.':
                    self._expect('.')
                    self._write_terminal()  # subroutineName
                    self.tokenizer.advance()
                self._expect('(')
                self.compile_expression_list()
                self._expect(')')

        self.indent_level -= 1
        self._write('</term>')

    def compile_expression_list(self):
        """Compile a (possibly empty) comma-separated list of expressions.

        Grammar: (expression (',' expression)*)?
        """
        self._write('<expressionList>')
        self.indent_level += 1

        # Check if expression list is empty
        if not (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
                self.tokenizer.symbol() == ')'):
            # expression
            self.compile_expression()

            # (',' expression)*
            while (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
                   self.tokenizer.symbol() == ','):
                self._expect(',')
                self.compile_expression()

        self.indent_level -= 1
        self._write('</expressionList>')
