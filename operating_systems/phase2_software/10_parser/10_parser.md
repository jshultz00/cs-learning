# Project 10: Syntax Analyzer (Compiler Frontend)

**Objective**: Build a tokenizer and parser for the Jack language

## Background Concepts

### What You've Built So Far

**Phase 1: Hardware Layer (Projects 1-5)**
- ✅ Logic gates from NAND primitives
- ✅ ALU with 18+ operations
- ✅ Memory hierarchy (DFF → Register → RAM)
- ✅ Complete Von Neumann computer

**Phase 2: Software Layer (Projects 6-9)**
- ✅ **Assembler (Project 6)**: Symbolic assembly → Binary machine code
- ✅ **VM Translator (Projects 7-8)**: VM code → Assembly with functions and control flow
- ✅ **Jack Language (Project 9)**: Wrote programs in high-level OOP language

**What you can do now**:
Write Jack programs with classes, methods, and OOP:
```jack
class Point {
    field int x, y;

    constructor Point new(int ax, int ay) {
        let x = ax;
        let y = ay;
        return this;
    }

    method int getX() {
        return x;
    }
}
```

**What you CANNOT do yet**:
Compile Jack to VM code! You can write Jack programs but can't run them without a compiler.

### The Problem: Jack is Just Text

Your Jack programs are just text files. The computer needs:
1. **Tokenization**: Break source into meaningful units (keywords, symbols, identifiers)
2. **Parsing**: Understand structure (classes, methods, statements, expressions)
3. **Code generation**: Translate to VM code (Project 11)

**Example transformation**:
```jack
let x = y + 5;
```

**Step 1: Tokenization** (Project 10):
```
<keyword> let </keyword>
<identifier> x </identifier>
<symbol> = </symbol>
<identifier> y </identifier>
<symbol> + </symbol>
<integerConstant> 5 </integerConstant>
<symbol> ; </symbol>
```

**Step 2: Parsing** (Project 10):
```xml
<letStatement>
  <keyword> let </keyword>
  <identifier> x </identifier>
  <symbol> = </symbol>
  <expression>
    <term>
      <identifier> y </identifier>
    </term>
    <symbol> + </symbol>
    <term>
      <integerConstant> 5 </integerConstant>
    </term>
  </expression>
  <symbol> ; </symbol>
</letStatement>
```

**Step 3: Code Generation** (Project 11):
```vm
push local 1    // y
push constant 5
add
pop local 0     // x
```

### The Solution: Syntax Analyzer

Project 10 implements the **compiler frontend**:
- **Tokenizer (Lexer)**: Breaks source code into tokens
- **Parser**: Validates syntax and builds parse tree

This is **half the compiler**. Project 11 adds code generation to complete it.

🎓 **Key insight**: Compilation is a pipeline: Source → Tokens → Parse Tree → Code. Each stage transforms the representation while preserving meaning. Breaking compilation into stages makes it manageable!

## Jack Grammar Specification

### Lexical Elements (Tokens)

Jack has five token types:

**1. Keywords** (reserved words):
```
class constructor function method field static var
int char boolean void true false null
this let do if else while return
```

**2. Symbols** (operators and punctuation):
```
{ } ( ) [ ] . , ; + - * / & | < > = ~
```

**3. Integer constants**:
- Range: 0-32767 (non-negative 16-bit integers)
- Examples: `0`, `42`, `1234`

**4. String constants**:
- Double-quoted strings without newlines or double quotes
- Examples: `"Hello"`, `"Hello, World!"`, `""`

**5. Identifiers**:
- Start with letter or underscore
- Contain letters, digits, underscores
- Case-sensitive
- Cannot be keywords
- Examples: `x`, `Point`, `get_value`, `_temp`, `var1`

**Comments** (not tokens, ignored by tokenizer):
```jack
// Single-line comment

/** Multi-line comment
 * Can span multiple lines
 */

/* Also multi-line */
```

### Grammar Rules (BNF-style)

**Program Structure**:
```
class: 'class' className '{' classVarDec* subroutineDec* '}'
className: identifier
```

**Class Variables**:
```
classVarDec: ('static' | 'field') type varName (',' varName)* ';'
type: 'int' | 'char' | 'boolean' | className
varName: identifier
```

**Subroutines**:
```
subroutineDec: ('constructor' | 'function' | 'method')
               ('void' | type) subroutineName '(' parameterList ')' subroutineBody

parameterList: ((type varName) (',' type varName)*)?

subroutineBody: '{' varDec* statements '}'

varDec: 'var' type varName (',' varName)* ';'
```

**Statements**:
```
statements: statement*

statement: letStatement | ifStatement | whileStatement | doStatement | returnStatement

letStatement: 'let' varName ('[' expression ']')? '=' expression ';'

ifStatement: 'if' '(' expression ')' '{' statements '}'
             ('else' '{' statements '}')?

whileStatement: 'while' '(' expression ')' '{' statements '}'

doStatement: 'do' subroutineCall ';'

returnStatement: 'return' expression? ';'
```

**Expressions**:
```
expression: term (op term)*

term: integerConstant | stringConstant | keywordConstant |
      varName | varName '[' expression ']' | subroutineCall |
      '(' expression ')' | unaryOp term

subroutineCall: subroutineName '(' expressionList ')' |
                (className | varName) '.' subroutineName '(' expressionList ')'

expressionList: (expression (',' expression)*)?

op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='

unaryOp: '-' | '~'

keywordConstant: 'true' | 'false' | 'null' | 'this'
```

🎓 **Key insight**: Grammar rules are **recursive**. Expressions contain terms, terms can contain expressions (via parentheses), statements contain statements (via if/while blocks). This recursion is what makes languages expressive!

## Learning Path

### Step 1: Understand the Grammar (1-2 hours)

Before implementing anything, study the grammar rules above.

**Exercise 1**: Parse this by hand:
```jack
let x = 10;
```

**Answer**:
```
letStatement:
  'let' (keyword)
  x (varName/identifier)
  '=' (symbol)
  expression:
    term:
      10 (integerConstant)
  ';' (symbol)
```

**Exercise 2**: Parse this:
```jack
if (x > 0) {
    let y = x;
}
```

**Answer**:
```
ifStatement:
  'if' (keyword)
  '(' (symbol)
  expression:
    term: x (identifier)
    '>' (op/symbol)
    term: 0 (integerConstant)
  ')' (symbol)
  '{' (symbol)
  statements:
    letStatement:
      'let' x '=' expression(term(x)) ';'
  '}' (symbol)
```

**Exercise 3**: Identify token types:
```jack
class Point {
    field int x;
}
```

**Answer**:
- `class`: keyword
- `Point`: identifier
- `{`: symbol
- `field`: keyword
- `int`: keyword
- `x`: identifier
- `;`: symbol
- `}`: symbol

### Step 2: Implement the Tokenizer (3-4 hours)

The tokenizer reads Jack source and produces a stream of tokens.

**Create file**: `tokenizer.py`

```python
"""
Jack Tokenizer - Lexical analyzer for Jack language

Breaks Jack source code into tokens:
- Keywords: class, method, function, etc.
- Symbols: { } ( ) [ ] . , ; + - * / & | < > = ~
- Integer constants: 0-32767
- String constants: "..."
- Identifiers: variable/class/function names
"""

class JackTokenizer:
    """Tokenizes Jack source code"""

    # Token type constants
    KEYWORD = 'KEYWORD'
    SYMBOL = 'SYMBOL'
    IDENTIFIER = 'IDENTIFIER'
    INT_CONST = 'INT_CONST'
    STRING_CONST = 'STRING_CONST'

    # Keywords set
    KEYWORDS = {
        'class', 'constructor', 'function', 'method', 'field', 'static',
        'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null',
        'this', 'let', 'do', 'if', 'else', 'while', 'return'
    }

    # Symbols set
    SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ',', ';',
                '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'}

    def __init__(self, input_file):
        """Initialize tokenizer with Jack source file"""
        with open(input_file, 'r') as f:
            self.lines = f.readlines()

        # Remove comments and tokenize
        self.tokens = []
        self._remove_comments()
        self._tokenize()

        self.current_token_index = -1
        self.current_token = None

    def _remove_comments(self):
        """Remove comments from source lines"""
        clean_lines = []
        in_block_comment = False

        for line in self.lines:
            # Handle block comments
            while '/*' in line or '*/' in line or in_block_comment:
                if not in_block_comment:
                    if '/*' in line:
                        # Start of block comment
                        start = line.index('/*')
                        if '*/' in line[start:]:
                            # Comment ends on same line
                            end = line.index('*/', start) + 2
                            line = line[:start] + line[end:]
                        else:
                            # Comment continues to next line
                            line = line[:start]
                            in_block_comment = True
                            break
                    else:
                        break
                else:
                    # Currently in block comment
                    if '*/' in line:
                        # End of block comment
                        end = line.index('*/') + 2
                        line = line[end:]
                        in_block_comment = False
                    else:
                        # Comment continues
                        line = ''
                        break

            # Handle single-line comments
            if '//' in line:
                line = line[:line.index('//')]

            # Strip whitespace
            line = line.strip()

            if line:
                clean_lines.append(line)

        self.clean_lines = clean_lines

    def _tokenize(self):
        """Break cleaned source into tokens"""
        for line in self.clean_lines:
            i = 0
            while i < len(line):
                # Skip whitespace
                if line[i].isspace():
                    i += 1
                    continue

                # Symbol
                if line[i] in self.SYMBOLS:
                    self.tokens.append((self.SYMBOL, line[i]))
                    i += 1

                # String constant
                elif line[i] == '"':
                    j = i + 1
                    while j < len(line) and line[j] != '"':
                        j += 1
                    if j >= len(line):
                        raise SyntaxError(f"Unterminated string: {line[i:]}")
                    string_val = line[i+1:j]  # Without quotes
                    self.tokens.append((self.STRING_CONST, string_val))
                    i = j + 1

                # Integer constant
                elif line[i].isdigit():
                    j = i
                    while j < len(line) and line[j].isdigit():
                        j += 1
                    int_val = int(line[i:j])
                    if int_val > 32767:
                        raise SyntaxError(f"Integer constant too large: {int_val}")
                    self.tokens.append((self.INT_CONST, int_val))
                    i = j

                # Identifier or keyword
                elif line[i].isalpha() or line[i] == '_':
                    j = i
                    while j < len(line) and (line[j].isalnum() or line[j] == '_'):
                        j += 1
                    word = line[i:j]
                    if word in self.KEYWORDS:
                        self.tokens.append((self.KEYWORD, word))
                    else:
                        self.tokens.append((self.IDENTIFIER, word))
                    i = j

                else:
                    raise SyntaxError(f"Unexpected character: {line[i]}")

    def has_more_tokens(self):
        """Are there more tokens in the input?"""
        return self.current_token_index < len(self.tokens) - 1

    def advance(self):
        """Get the next token from input and make it current"""
        if self.has_more_tokens():
            self.current_token_index += 1
            self.current_token = self.tokens[self.current_token_index]

    def token_type(self):
        """Return type of current token"""
        if self.current_token:
            return self.current_token[0]
        return None

    def keyword(self):
        """Return keyword (if current token is keyword)"""
        if self.token_type() == self.KEYWORD:
            return self.current_token[1]
        return None

    def symbol(self):
        """Return character (if current token is symbol)"""
        if self.token_type() == self.SYMBOL:
            return self.current_token[1]
        return None

    def identifier(self):
        """Return identifier (if current token is identifier)"""
        if self.token_type() == self.IDENTIFIER:
            return self.current_token[1]
        return None

    def int_val(self):
        """Return integer value (if current token is integer constant)"""
        if self.token_type() == self.INT_CONST:
            return self.current_token[1]
        return None

    def string_val(self):
        """Return string value without quotes (if current token is string constant)"""
        if self.token_type() == self.STRING_CONST:
            return self.current_token[1]
        return None

    def peek(self):
        """Look at next token without advancing"""
        if self.current_token_index < len(self.tokens) - 1:
            return self.tokens[self.current_token_index + 1]
        return None
```

**Test the tokenizer**:

Create `test_tokenizer.py`:
```python
from tokenizer import JackTokenizer

def test_tokenizer(input_file):
    """Test tokenizer on Jack file"""
    tokenizer = JackTokenizer(input_file)

    print(f"Tokenizing {input_file}:")
    print("=" * 50)

    while tokenizer.has_more_tokens():
        tokenizer.advance()
        token_type = tokenizer.token_type()

        if token_type == JackTokenizer.KEYWORD:
            print(f"KEYWORD: {tokenizer.keyword()}")
        elif token_type == JackTokenizer.SYMBOL:
            print(f"SYMBOL: {tokenizer.symbol()}")
        elif token_type == JackTokenizer.IDENTIFIER:
            print(f"IDENTIFIER: {tokenizer.identifier()}")
        elif token_type == JackTokenizer.INT_CONST:
            print(f"INT_CONST: {tokenizer.int_val()}")
        elif token_type == JackTokenizer.STRING_CONST:
            print(f"STRING_CONST: \"{tokenizer.string_val()}\"")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python test_tokenizer.py <file.jack>")
        sys.exit(1)

    test_tokenizer(sys.argv[1])
```

**Test input** (`SimpleTest.jack`):
```jack
class Main {
    function void main() {
        var int x;
        let x = 10 + 5;
        return;
    }
}
```

**Run test**:
```bash
python test_tokenizer.py SimpleTest.jack
```

**Expected output**:
```
Tokenizing SimpleTest.jack:
==================================================
KEYWORD: class
IDENTIFIER: Main
SYMBOL: {
KEYWORD: function
KEYWORD: void
IDENTIFIER: main
SYMBOL: (
SYMBOL: )
SYMBOL: {
KEYWORD: var
KEYWORD: int
IDENTIFIER: x
SYMBOL: ;
KEYWORD: let
IDENTIFIER: x
SYMBOL: =
INT_CONST: 10
SYMBOL: +
INT_CONST: 5
SYMBOL: ;
KEYWORD: return
SYMBOL: ;
SYMBOL: }
SYMBOL: }
```

### Step 3: Implement the Parser (5-6 hours)

The parser validates syntax and builds XML parse tree.

**Create file**: `parser.py`

```python
"""
Jack Parser - Syntax analyzer for Jack language

Implements recursive descent parser that:
- Validates syntax against Jack grammar
- Builds XML parse tree
- Reports syntax errors with context
"""

from tokenizer import JackTokenizer

class CompilationEngine:
    """Recursive descent parser for Jack"""

    def __init__(self, tokenizer, output_file):
        """Initialize parser with tokenizer and output file"""
        self.tokenizer = tokenizer
        self.output = open(output_file, 'w')
        self.indent_level = 0

    def close(self):
        """Close output file"""
        self.output.close()

    # Helper methods

    def _write_open_tag(self, tag):
        """Write opening XML tag with indentation"""
        self.output.write('  ' * self.indent_level + f'<{tag}>\n')
        self.indent_level += 1

    def _write_close_tag(self, tag):
        """Write closing XML tag with indentation"""
        self.indent_level -= 1
        self.output.write('  ' * self.indent_level + f'</{tag}>\n')

    def _write_terminal(self):
        """Write current token as terminal"""
        token_type = self.tokenizer.token_type()

        if token_type == JackTokenizer.KEYWORD:
            value = self.tokenizer.keyword()
            self.output.write('  ' * self.indent_level +
                             f'<keyword> {value} </keyword>\n')
        elif token_type == JackTokenizer.SYMBOL:
            value = self.tokenizer.symbol()
            # Escape XML special characters
            if value == '<':
                value = '&lt;'
            elif value == '>':
                value = '&gt;'
            elif value == '&':
                value = '&amp;'
            self.output.write('  ' * self.indent_level +
                             f'<symbol> {value} </symbol>\n')
        elif token_type == JackTokenizer.IDENTIFIER:
            value = self.tokenizer.identifier()
            self.output.write('  ' * self.indent_level +
                             f'<identifier> {value} </identifier>\n')
        elif token_type == JackTokenizer.INT_CONST:
            value = self.tokenizer.int_val()
            self.output.write('  ' * self.indent_level +
                             f'<integerConstant> {value} </integerConstant>\n')
        elif token_type == JackTokenizer.STRING_CONST:
            value = self.tokenizer.string_val()
            self.output.write('  ' * self.indent_level +
                             f'<stringConstant> {value} </stringConstant>\n')

    def _expect(self, expected_value):
        """Consume token if it matches expected value, else error"""
        if self.tokenizer.token_type() == JackTokenizer.KEYWORD:
            actual = self.tokenizer.keyword()
        elif self.tokenizer.token_type() == JackTokenizer.SYMBOL:
            actual = self.tokenizer.symbol()
        else:
            actual = None

        if actual != expected_value:
            raise SyntaxError(f"Expected '{expected_value}', got '{actual}'")

        self._write_terminal()
        self.tokenizer.advance()

    # Grammar rule methods

    def compile_class(self):
        """
        Compile complete class.
        Grammar: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        self._write_open_tag('class')

        self.tokenizer.advance()  # Start parsing

        # 'class'
        self._expect('class')

        # className
        if self.tokenizer.token_type() != JackTokenizer.IDENTIFIER:
            raise SyntaxError("Expected class name (identifier)")
        self._write_terminal()
        self.tokenizer.advance()

        # '{'
        self._expect('{')

        # classVarDec*
        while (self.tokenizer.token_type() == JackTokenizer.KEYWORD and
               self.tokenizer.keyword() in ['static', 'field']):
            self.compile_class_var_dec()

        # subroutineDec*
        while (self.tokenizer.token_type() == JackTokenizer.KEYWORD and
               self.tokenizer.keyword() in ['constructor', 'function', 'method']):
            self.compile_subroutine()

        # '}'
        self._expect('}')

        self._write_close_tag('class')

    def compile_class_var_dec(self):
        """
        Compile static or field declaration.
        Grammar: ('static' | 'field') type varName (',' varName)* ';'
        """
        self._write_open_tag('classVarDec')

        # 'static' | 'field'
        self._write_terminal()
        self.tokenizer.advance()

        # type
        self._write_terminal()
        self.tokenizer.advance()

        # varName
        if self.tokenizer.token_type() != JackTokenizer.IDENTIFIER:
            raise SyntaxError("Expected variable name (identifier)")
        self._write_terminal()
        self.tokenizer.advance()

        # (',' varName)*
        while (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
               self.tokenizer.symbol() == ','):
            self._expect(',')
            if self.tokenizer.token_type() != JackTokenizer.IDENTIFIER:
                raise SyntaxError("Expected variable name after ','")
            self._write_terminal()
            self.tokenizer.advance()

        # ';'
        self._expect(';')

        self._write_close_tag('classVarDec')

    def compile_subroutine(self):
        """
        Compile method, function, or constructor.
        Grammar: ('constructor' | 'function' | 'method')
                 ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        """
        self._write_open_tag('subroutineDec')

        # 'constructor' | 'function' | 'method'
        self._write_terminal()
        self.tokenizer.advance()

        # 'void' | type
        self._write_terminal()
        self.tokenizer.advance()

        # subroutineName
        if self.tokenizer.token_type() != JackTokenizer.IDENTIFIER:
            raise SyntaxError("Expected subroutine name (identifier)")
        self._write_terminal()
        self.tokenizer.advance()

        # '('
        self._expect('(')

        # parameterList
        self.compile_parameter_list()

        # ')'
        self._expect(')')

        # subroutineBody
        self.compile_subroutine_body()

        self._write_close_tag('subroutineDec')

    def compile_parameter_list(self):
        """
        Compile parameter list (possibly empty).
        Grammar: ((type varName) (',' type varName)*)?
        """
        self._write_open_tag('parameterList')

        # Check if parameter list is empty
        if not (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
                self.tokenizer.symbol() == ')'):

            # type
            self._write_terminal()
            self.tokenizer.advance()

            # varName
            if self.tokenizer.token_type() != JackTokenizer.IDENTIFIER:
                raise SyntaxError("Expected parameter name (identifier)")
            self._write_terminal()
            self.tokenizer.advance()

            # (',' type varName)*
            while (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
                   self.tokenizer.symbol() == ','):
                self._expect(',')

                # type
                self._write_terminal()
                self.tokenizer.advance()

                # varName
                if self.tokenizer.token_type() != JackTokenizer.IDENTIFIER:
                    raise SyntaxError("Expected parameter name after ','")
                self._write_terminal()
                self.tokenizer.advance()

        self._write_close_tag('parameterList')

    def compile_subroutine_body(self):
        """
        Compile subroutine body.
        Grammar: '{' varDec* statements '}'
        """
        self._write_open_tag('subroutineBody')

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

        self._write_close_tag('subroutineBody')

    def compile_var_dec(self):
        """
        Compile var declaration.
        Grammar: 'var' type varName (',' varName)* ';'
        """
        self._write_open_tag('varDec')

        # 'var'
        self._expect('var')

        # type
        self._write_terminal()
        self.tokenizer.advance()

        # varName
        if self.tokenizer.token_type() != JackTokenizer.IDENTIFIER:
            raise SyntaxError("Expected variable name (identifier)")
        self._write_terminal()
        self.tokenizer.advance()

        # (',' varName)*
        while (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
               self.tokenizer.symbol() == ','):
            self._expect(',')
            if self.tokenizer.token_type() != JackTokenizer.IDENTIFIER:
                raise SyntaxError("Expected variable name after ','")
            self._write_terminal()
            self.tokenizer.advance()

        # ';'
        self._expect(';')

        self._write_close_tag('varDec')

    def compile_statements(self):
        """
        Compile sequence of statements.
        Grammar: statement*
        """
        self._write_open_tag('statements')

        # Keep compiling statements until we hit '}'
        while not (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
                   self.tokenizer.symbol() == '}'):

            if self.tokenizer.token_type() != JackTokenizer.KEYWORD:
                break

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
            else:
                break  # Not a statement keyword

        self._write_close_tag('statements')

    def compile_let(self):
        """
        Compile let statement.
        Grammar: 'let' varName ('[' expression ']')? '=' expression ';'
        """
        self._write_open_tag('letStatement')

        # 'let'
        self._expect('let')

        # varName
        if self.tokenizer.token_type() != JackTokenizer.IDENTIFIER:
            raise SyntaxError("Expected variable name after 'let'")
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

        self._write_close_tag('letStatement')

    def compile_if(self):
        """
        Compile if statement.
        Grammar: 'if' '(' expression ')' '{' statements '}'
                 ('else' '{' statements '}')?
        """
        self._write_open_tag('ifStatement')

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

        self._write_close_tag('ifStatement')

    def compile_while(self):
        """
        Compile while statement.
        Grammar: 'while' '(' expression ')' '{' statements '}'
        """
        self._write_open_tag('whileStatement')

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

        self._write_close_tag('whileStatement')

    def compile_do(self):
        """
        Compile do statement.
        Grammar: 'do' subroutineCall ';'
        """
        self._write_open_tag('doStatement')

        # 'do'
        self._expect('do')

        # subroutineCall
        self._compile_subroutine_call()

        # ';'
        self._expect(';')

        self._write_close_tag('doStatement')

    def compile_return(self):
        """
        Compile return statement.
        Grammar: 'return' expression? ';'
        """
        self._write_open_tag('returnStatement')

        # 'return'
        self._expect('return')

        # expression?
        if not (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
                self.tokenizer.symbol() == ';'):
            self.compile_expression()

        # ';'
        self._expect(';')

        self._write_close_tag('returnStatement')

    def compile_expression(self):
        """
        Compile expression.
        Grammar: term (op term)*
        """
        self._write_open_tag('expression')

        # term
        self.compile_term()

        # (op term)*
        ops = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        while (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
               self.tokenizer.symbol() in ops):
            # op
            self._write_terminal()
            self.tokenizer.advance()

            # term
            self.compile_term()

        self._write_close_tag('expression')

    def compile_term(self):
        """
        Compile term.
        Grammar: integerConstant | stringConstant | keywordConstant |
                 varName | varName '[' expression ']' | subroutineCall |
                 '(' expression ')' | unaryOp term
        """
        self._write_open_tag('term')

        token_type = self.tokenizer.token_type()

        # integerConstant
        if token_type == JackTokenizer.INT_CONST:
            self._write_terminal()
            self.tokenizer.advance()

        # stringConstant
        elif token_type == JackTokenizer.STRING_CONST:
            self._write_terminal()
            self.tokenizer.advance()

        # keywordConstant (true | false | null | this)
        elif (token_type == JackTokenizer.KEYWORD and
              self.tokenizer.keyword() in ['true', 'false', 'null', 'this']):
            self._write_terminal()
            self.tokenizer.advance()

        # '(' expression ')'
        elif token_type == JackTokenizer.SYMBOL and self.tokenizer.symbol() == '(':
            self._expect('(')
            self.compile_expression()
            self._expect(')')

        # unaryOp term
        elif token_type == JackTokenizer.SYMBOL and self.tokenizer.symbol() in ['-', '~']:
            self._write_terminal()  # unaryOp
            self.tokenizer.advance()
            self.compile_term()

        # varName | varName '[' expression ']' | subroutineCall
        elif token_type == JackTokenizer.IDENTIFIER:
            self._write_terminal()  # varName or className or subroutineName
            self.tokenizer.advance()

            # '[' expression ']' (array indexing)
            if (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
                self.tokenizer.symbol() == '['):
                self._expect('[')
                self.compile_expression()
                self._expect(']')

            # '(' expressionList ')' or '.' subroutineName '(' expressionList ')'
            elif (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
                  self.tokenizer.symbol() in ['(', '.']):

                if self.tokenizer.symbol() == '.':
                    self._expect('.')
                    if self.tokenizer.token_type() != JackTokenizer.IDENTIFIER:
                        raise SyntaxError("Expected subroutine name after '.'")
                    self._write_terminal()  # subroutineName
                    self.tokenizer.advance()

                self._expect('(')
                self.compile_expression_list()
                self._expect(')')

        else:
            raise SyntaxError(f"Unexpected term: {self.tokenizer.current_token}")

        self._write_close_tag('term')

    def _compile_subroutine_call(self):
        """
        Helper to compile subroutine call (used by do statement and term).
        Grammar: subroutineName '(' expressionList ')' |
                 (className | varName) '.' subroutineName '(' expressionList ')'
        """
        # subroutineName or className or varName
        if self.tokenizer.token_type() != JackTokenizer.IDENTIFIER:
            raise SyntaxError("Expected subroutine/class/variable name")
        self._write_terminal()
        self.tokenizer.advance()

        # Check for '.' (method call)
        if (self.tokenizer.token_type() == JackTokenizer.SYMBOL and
            self.tokenizer.symbol() == '.'):
            self._expect('.')
            if self.tokenizer.token_type() != JackTokenizer.IDENTIFIER:
                raise SyntaxError("Expected subroutine name after '.'")
            self._write_terminal()  # subroutineName
            self.tokenizer.advance()

        # '(' expressionList ')'
        self._expect('(')
        self.compile_expression_list()
        self._expect(')')

    def compile_expression_list(self):
        """
        Compile comma-separated list of expressions.
        Grammar: (expression (',' expression)*)?
        """
        self._write_open_tag('expressionList')

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

        self._write_close_tag('expressionList')
```

### Step 4: Create Main Analyzer (1 hour)

Create the main program that ties tokenizer and parser together.

**Create file**: `jack_analyzer.py`

```python
"""
Jack Analyzer - Main program for Jack syntax analyzer

Usage:
    python jack_analyzer.py <file.jack>       # Analyze single file
    python jack_analyzer.py <directory>       # Analyze all .jack files in directory
"""

import os
import sys
from tokenizer import JackTokenizer
from parser import CompilationEngine

def analyze_file(input_file):
    """Analyze single Jack file and generate XML"""
    if not input_file.endswith('.jack'):
        print(f"Skipping non-Jack file: {input_file}")
        return

    output_file = input_file.replace('.jack', '.xml')

    print(f"Analyzing {input_file}...")

    try:
        # Tokenize
        tokenizer = JackTokenizer(input_file)

        # Parse and generate XML
        parser = CompilationEngine(tokenizer, output_file)
        parser.compile_class()
        parser.close()

        print(f"  → Generated {output_file}")

    except SyntaxError as e:
        print(f"  ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"  UNEXPECTED ERROR: {e}")
        sys.exit(1)

def analyze_directory(directory):
    """Analyze all .jack files in directory"""
    jack_files = [f for f in os.listdir(directory) if f.endswith('.jack')]

    if not jack_files:
        print(f"No .jack files found in {directory}")
        return

    print(f"Found {len(jack_files)} Jack file(s) in {directory}")

    for jack_file in jack_files:
        analyze_file(os.path.join(directory, jack_file))

def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python jack_analyzer.py <file.jack|directory>")
        sys.exit(1)

    path = sys.argv[1]

    if os.path.isfile(path):
        analyze_file(path)
    elif os.path.isdir(path):
        analyze_directory(path)
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

### Step 5: Test with Examples (2-3 hours)

Test the analyzer with progressively complex programs.

**Test 1**: Simple class (`test/Simple.jack`)
```jack
class Main {
    function void main() {
        return;
    }
}
```

**Run**:
```bash
python jack_analyzer.py test/Simple.jack
```

**Expected output** (`test/Simple.xml`):
```xml
<class>
  <keyword> class </keyword>
  <identifier> Main </identifier>
  <symbol> { </symbol>
  <subroutineDec>
    <keyword> function </keyword>
    <keyword> void </keyword>
    <identifier> main </identifier>
    <symbol> ( </symbol>
    <parameterList>
    </parameterList>
    <symbol> ) </symbol>
    <subroutineBody>
      <symbol> { </symbol>
      <statements>
        <returnStatement>
          <keyword> return </keyword>
          <symbol> ; </symbol>
        </returnStatement>
      </statements>
      <symbol> } </symbol>
    </subroutineBody>
  </subroutineDec>
  <symbol> } </symbol>
</class>
```

**Test 2**: Variables (`test/Variables.jack`)
```jack
class Main {
    static int count;
    field int x, y;

    function void main() {
        var int i, sum;
        let i = 0;
        let sum = 0;
        return;
    }
}
```

**Test 3**: Expressions (`test/Expression.jack`)
```jack
class Main {
    function int calculate(int a, int b) {
        return (a + b) * (a - b);
    }
}
```

**Test 4**: Control flow (`test/Loop.jack`)
```jack
class Main {
    function void main() {
        var int i;
        let i = 0;
        while (i < 10) {
            let i = i + 1;
        }
        return;
    }
}
```

**Test 5**: Complete class from Project 9

Use the `Point.jack` file from Project 9 examples:

```bash
python jack_analyzer.py ../09_language_design/examples/04_point_class/Point.jack
```

Verify the XML output is correctly structured with all class variables, constructor, and methods.

## Deep Dive: Implementation Insights

### Tokenizer Design Decisions

**Why pre-tokenize everything?**

We chose **upfront tokenization** (tokenize entire file into list):

**Pros**:
- Simple token navigation (array indexing)
- Easy lookahead (`peek()` method)
- Can backtrack if needed
- Easier debugging (inspect token list)

**Cons**:
- Memory usage for large files
- Must read entire file first

**Alternative** (lazy tokenization):
Generate tokens on demand in `advance()`.

**Pros**: Lower memory
**Cons**: Complex lookahead, can't backtrack

🎓 **Key insight**: For Jack, upfront tokenization is the right choice. Files are small (~500 lines max), and simplicity beats memory efficiency.

### Comment Removal Strategy

**Challenge**: Handle three comment types:
```jack
// Single-line comment

/** API documentation comment
 * Multiple lines
 */

/* Block comment */
```

**Solution**: Track state while scanning:
```python
in_block_comment = False

for line in self.lines:
    # Handle /* and */
    if '/*' in line and not in_block_comment:
        in_block_comment = True
        # Extract text before /*
        line = line[:line.index('/*')]

    if '*/' in line and in_block_comment:
        in_block_comment = False
        # Extract text after */
        line = line[line.index('*/') + 2:]

    if in_block_comment:
        continue  # Skip entire line

    # Handle //
    if '//' in line:
        line = line[:line.index('//')]
```

**Edge cases**:
- Comment inside string: `"This is // not a comment"` (Handle strings first)
- Nested comments: Not allowed in Jack
- Comment markers in strings: `let x = "/*";` (Tokenize strings before checking comments)

### Recursive Descent Parsing

**Why recursive descent?**

Jack's grammar is **LL(1)**: Can be parsed with one-token lookahead.

**Grammar rule**:
```
statement: letStatement | ifStatement | whileStatement | doStatement | returnStatement
```

**Parser code** (direct mapping):
```python
def compile_statement(self):
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
```

Each grammar rule → one parsing function
Grammar recursion → code recursion

**Example**: `expression` contains `term`, `term` can contain `expression` (via parentheses).

```python
def compile_expression(self):
    self.compile_term()  # term can recursively call compile_expression

def compile_term(self):
    if token == '(':
        self.compile_expression()  # Recursion!
```

🎓 **Key insight**: Recursive descent naturally expresses recursive grammars. The code structure mirrors the grammar structure, making it easy to implement and debug.

### Expression Parsing Simplification

**Jack's design choice**: All binary operators have **equal precedence** and are **left-associative**.

**Grammar**:
```
expression: term (op term)*
```

This means:
- `a + b * c` parses as `(a + b) * c`, not `a + (b * c)`
- `a - b - c` parses as `(a - b) - c` (left-associative)

**Why?**
- Simpler grammar (one precedence level)
- Simpler parser (no precedence climbing)
- Shifts complexity to Project 11 (code generator handles evaluation order)

**Alternative** (standard approach):
```
expression: additive
additive: multiplicative (('+' | '-') multiplicative)*
multiplicative: unary (('*' | '/') unary)*
unary: ('-' | '~')? primary
primary: number | identifier | '(' expression ')'
```

This correctly handles precedence but requires more parsing functions.

🎓 **Key insight**: Language design involves tradeoffs. Jack chose simplicity in parsing over natural expression evaluation. The compiler compensates in code generation.

### Lookahead in Term Parsing

**Challenge**: Terms starting with identifier need lookahead:
- `x` - variable
- `x[i]` - array access
- `x.method()` - method call
- `func()` - function call

**Solution**: Consume identifier, then check next token:

```python
if token_type == IDENTIFIER:
    self._write_terminal()  # Write identifier
    self.tokenizer.advance()  # Move to next token

    # Lookahead determines what follows
    if self.tokenizer.symbol() == '[':
        # Array access: x[expression]
        self._expect('[')
        self.compile_expression()
        self._expect(']')

    elif self.tokenizer.symbol() == '(':
        # Function call: func(args)
        self._expect('(')
        self.compile_expression_list()
        self._expect(')')

    elif self.tokenizer.symbol() == '.':
        # Method call: obj.method(args)
        self._expect('.')
        self._write_terminal()  # method name
        self.tokenizer.advance()
        self._expect('(')
        self.compile_expression_list()
        self._expect(')')
```

**LL(1) property**: One-token lookahead is always sufficient. After seeing identifier, the next token uniquely determines the parse.

### XML Output Structure

**Terminal nodes** (tokens):
```xml
<keyword> let </keyword>
<symbol> = </symbol>
<identifier> x </identifier>
<integerConstant> 42 </integerConstant>
<stringConstant> Hello </stringConstant>
```

**Non-terminal nodes** (grammar constructs):
```xml
<class>
  <subroutineDec>
    <statements>
      <letStatement>
        ...
      </letStatement>
    </statements>
  </subroutineDec>
</class>
```

**XML escaping**:
```python
if symbol == '<':
    symbol = '&lt;'
elif symbol == '>':
    symbol = '&gt;'
elif symbol == '&':
    symbol = '&amp;'
```

**Why XML?**
- Human-readable
- Self-validating (matching tags)
- Easy to process in Project 11
- Standard format (can use XML tools to visualize)

**Alternative**: AST as Python objects. Project 11 might use this internally.

## What You Should Understand After This Project

- ✅ **Lexical analysis**: Breaking source into tokens
- ✅ **Syntax analysis**: Validating structure with grammar rules
- ✅ **Recursive descent parsing**: Grammar rules → parsing functions
- ✅ **LL(1) parsing**: How one-token lookahead enables deterministic parsing
- ✅ **Parse trees**: Representing program structure as tree
- ✅ **Grammar design**: How grammar rules define language syntax

## Common Pitfalls

**1. Forgetting to advance tokenizer**
```python
# WRONG:
self._expect('let')
# Forgot to move to next token!
self._expect('=')  # Will fail - still on 'let'

# RIGHT:
self._expect('let')
self._write_terminal()  # varName
self.tokenizer.advance()  # Move forward
self._expect('=')
```

**2. Not handling empty constructs**
```python
# WRONG (crashes on empty parameter list):
def compile_parameter_list(self):
    self._write_terminal()  # Assumes parameter exists!

# RIGHT:
def compile_parameter_list(self):
    # Check if empty first
    if not (self.tokenizer.symbol() == ')'):
        # Not empty, compile parameters
        self._write_terminal()
```

**3. Incorrect lookahead check**
```python
# WRONG (doesn't verify token type):
if self.tokenizer.symbol() == '[':
    # Crash if current token is not a symbol!

# RIGHT:
if (self.tokenizer.token_type() == SYMBOL and
    self.tokenizer.symbol() == '['):
    # Safe - verified type first
```

**4. Missing XML escaping**
```python
# WRONG:
self.output.write('<symbol> < </symbol>')  # Invalid XML!

# RIGHT:
symbol = '<'
if symbol == '<':
    symbol = '&lt;'
self.output.write(f'<symbol> {symbol} </symbol>')
```

**5. Improper indentation tracking**
```python
# WRONG:
def _write_open_tag(self, tag):
    self.indent_level += 1  # Increment first
    self.output.write('  ' * self.indent_level + f'<{tag}>\n')
    # Now indentation is wrong!

# RIGHT:
def _write_open_tag(self, tag):
    self.output.write('  ' * self.indent_level + f'<{tag}>\n')
    self.indent_level += 1  # Increment after writing
```

**6. Not handling string tokenization**
```python
# WRONG (breaks on strings with spaces):
tokens = line.split()  # "Hello World" becomes ["Hello", "World"]

# RIGHT:
# Handle strings specially
if line[i] == '"':
    j = i + 1
    while j < len(line) and line[j] != '"':
        j += 1
    string_val = line[i+1:j]  # Entire string
    tokens.append(('STRING_CONST', string_val))
```

## Extension Ideas

**Level 1: Better Error Messages**
- Report line number and column for errors
- Show context: `let x 10;` → "Expected '=' after variable name 'x' (line 5)"
- Suggest fixes: Did you mean `;` instead of `,`?

**Level 2: AST Instead of XML**
- Build Abstract Syntax Tree as Python objects
- Define node classes: `ClassNode`, `MethodNode`, `LetStatementNode`
- Implement visitor pattern for tree traversal
- Use AST in Project 11 for code generation

**Level 3: Pretty Printer**
- Read XML and regenerate formatted Jack code
- Automatic indentation and spacing
- Code formatting tool

**Level 4: Syntax Highlighting**
- Generate HTML with colored tokens
- CSS classes for keywords, symbols, identifiers
- Interactive web-based code viewer

**Level 5: Language Extensions**
- Add `for` loops to grammar
- Support `break` and `continue` statements
- Add multi-dimensional array syntax: `int[][] matrix;`
- Implement `switch/case` statements

## Real-World Connection

**Your parser is similar to**:

**Python's parser** (CPython through 3.8):
- Used LL(1) recursive descent (shifted to PEG in 3.9)
- Built AST for code generation
- Grammar defined in `.pgen` file
- Difference: More complex grammar, error recovery

**JavaScript parsers** (V8, SpiderMonkey):
- Recursive descent with operator precedence climbing
- Lookahead for disambiguation
- AST construction
- Difference: Regex literals, destructuring, arrow functions add complexity

**GCC/Clang C/C++ parsers**:
- Recursive descent with backtracking
- Complex lookahead for templates
- Extensive error recovery
- Difference: Preprocessor, ambiguous grammar, template metaprogramming

**Modern parsers** (Rust, Go):
- Hand-written recursive descent
- Excellent error messages
- Fast compilation
- Similar simplicity to Jack parser

**Why parsing matters**:
1. **IDEs**: Syntax highlighting, autocomplete, refactoring use parsers
2. **Linters**: ESLint, Pylint parse code to find issues
3. **Formatters**: Prettier, Black parse and reformat code
4. **Transpilers**: Babel, TypeScript parse and transform code
5. **Static analysis**: Security tools parse code for vulnerabilities
6. **AI tools**: GitHub Copilot uses parsers to understand code context

## Success Criteria

You've mastered this project when you can:

1. **Explain tokenization**: Describe how source text becomes tokens
2. **Read grammar rules**: Understand BNF and translate to parsing functions
3. **Trace parsing manually**: Parse Jack code by hand following grammar
4. **Debug parse errors**: Identify why parsing fails and fix issues
5. **Extend grammar**: Add new language features to Jack
6. **Understand LL(1)**: Explain why one-token lookahead suffices

## Next Steps

**Project 11: Code Generator (Compiler Backend)**

With a parser producing XML parse trees, you'll complete the compiler:
- **Symbol tables**: Track variables, types, scopes
- **Expression compilation**: Convert parse tree → stack-based VM code
- **Statement compilation**: Generate VM for control flow
- **Class compilation**: Handle constructors, methods, field access
- **Memory management**: Allocate objects, arrays

**Example transformation**:

**Jack source**:
```jack
let x = y + 5;
```

**Parse tree** (Project 10 output):
```xml
<letStatement>
  <identifier> x </identifier>
  <expression>
    <term><identifier> y </identifier></term>
    <symbol> + </symbol>
    <term><integerConstant> 5 </integerConstant></term>
  </expression>
</letStatement>
```

**VM code** (Project 11 output):
```vm
push local 1    // y
push constant 5
add
pop local 0     // x
```

**Complete the toolchain**:
```
Jack source (you write)
    ↓ [Project 10: Tokenizer + Parser YOU JUST BUILT]
Parse tree (XML)
    ↓ [Project 11: Code generator]
VM code
    ↓ [Projects 7-8: VM translator you built]
Assembly code
    ↓ [Project 6: Assembler you built]
Machine code
    ↓ [Projects 1-5: Computer you built]
EXECUTION!
```

**Project 12: Operating System**

Finally, implement Jack OS in Jack itself:
- **Math**: Multiply, divide, sqrt using bit operations
- **Memory**: Heap allocator (malloc/free)
- **Screen**: Pixel/line/circle drawing
- **Keyboard**: Input buffering
- **String**: String manipulation
- **Array**: Array class
- **Sys**: System initialization

---

**Congratulations!** You've built a complete syntax analyzer for Jack. You can now tokenize source code and validate its syntax, producing parse trees that represent program structure. The next step is generating executable VM code from those trees!

The journey continues:
- ✅ Hardware layer (gates → computer)
- ✅ Assembly language (symbolic programming)
- ✅ Virtual machine (stack-based execution)
- ✅ High-level language (Jack programming)
- ✅ **Compiler frontend (tokenizer + parser)** ← You are here
- 🚧 Compiler backend (code generation)
- 🚧 Operating system (Jack OS library)

**Next**: Build the code generator that completes the compiler! 🚀

---

## Summary: What You Built

**You have implemented a complete syntax analyzer for Jack**:

1. **Tokenizer**: Breaks Jack source into tokens
   - Keywords, symbols, identifiers, constants
   - Comment removal
   - Error detection for invalid characters

2. **Parser**: Validates syntax using recursive descent
   - Follows Jack grammar rules
   - One-token lookahead (LL(1))
   - Error messages with context

3. **Parse tree builder**: Generates XML representation
   - Terminal nodes (tokens)
   - Non-terminal nodes (grammar constructs)
   - Proper indentation and structure

**Technical accomplishments**:
- ✅ Lexical analysis with comment removal
- ✅ Recursive descent parsing
- ✅ LL(1) parsing with lookahead
- ✅ XML parse tree generation
- ✅ Syntax validation for all Jack constructs
- ✅ Error detection and reporting

**Why this matters**:
You've built **half the compiler**—the part that understands syntax:
- Tokenizer: Source text → Tokens
- Parser: Tokens → Parse tree
- Next (Project 11): Parse tree → VM code

**The frontend understands code structure. The backend (Project 11) will generate executable instructions. Together, they form a complete compiler!** 🎉
