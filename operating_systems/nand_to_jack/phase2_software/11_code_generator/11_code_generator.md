# Project 11: Code Generator (Compiler Backend)

**Objective**: Complete the Jack compiler by generating VM code from parse trees

## Background Concepts

### What You've Built So Far

**Phase 1: Hardware Layer (Projects 1-5)**
- ✅ Complete computer from gates to Von Neumann architecture
- ✅ CPU with fetch-decode-execute cycle
- ✅ 16-bit instruction set (A-instructions and C-instructions)

**Phase 2: Software Layer (Projects 6-10)**
- ✅ **Assembler** (Project 6): Symbol resolution, assembly → machine code
- ✅ **VM Translator Part 1** (Project 7): Stack arithmetic, memory segments
- ✅ **VM Translator Part 2** (Project 8): Program flow, function calls
- ✅ **Jack Language** (Project 9): OOP language design and examples
- ✅ **Syntax Analyzer** (Project 10): Tokenizer + Parser → XML parse trees

**The Current Landscape**:

You now have a complete toolchain **except for the missing link**:

```
Jack Source Code (.jack)
        ↓
   [Tokenizer] ← Project 10
        ↓
   [Parser] ← Project 10
        ↓
   Parse Tree (XML)
        ↓
        ???  ← THIS PROJECT (Project 11)
        ↓
   VM Code (.vm)
        ↓
   [VM Translator] ← Projects 7-8
        ↓
   Assembly (.asm)
        ↓
   [Assembler] ← Project 6
        ↓
   Machine Code (.hack)
        ↓
   [Computer] ← Project 5
```

### The Problem: Parse Trees Aren't Executable

Project 10 gives you structured XML representing the program:

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

But you need **executable VM code**:

```vm
push local 1    // y
push constant 5
add
pop local 0     // x
```

**The challenge**: Traverse the parse tree and emit correct VM instructions, handling:
- Variable scoping (class-level vs subroutine-level)
- Memory segment mapping (field, static, local, argument)
- Expression evaluation (operator precedence, stack operations)
- Object construction and method dispatch
- Control flow (if, while statements)
- Arrays and string constants

### The Solution: Code Generation with Symbol Tables

Project 11 completes the compiler by adding:

**1. Symbol Table**: Tracks variables and their properties
```
Name    | Type    | Kind   | Index
--------|---------|--------|------
x       | int     | local  | 0
y       | int     | local  | 1
this    | Point   | pointer| 0
```

**2. VM Writer**: Generates VM commands
```python
vm_writer.write_push('local', 0)  # push local 0
vm_writer.write_arithmetic('add') # add
```

**3. Code Generator**: Traverses parse tree, uses symbol table, emits VM code

**What makes this challenging**:
- **Two-level scoping**: Class-level (field/static) + subroutine-level (local/argument)
- **Object-oriented features**: Constructor must allocate memory, methods receive `this`
- **Expression compilation**: Convert infix expressions to postfix stack operations
- **Type awareness**: Distinguish between primitives (int, char, boolean) and objects

## The Jack Compilation Model

### Variable Mapping

Jack has four variable kinds, each mapped to a VM memory segment:

| Jack Kind | VM Segment | Scope          | Example               |
|-----------|------------|----------------|-----------------------|
| `field`   | `this`     | Class instance | `field int x, y;`     |
| `static`  | `static`   | Class-level    | `static int count;`   |
| `var`     | `local`    | Subroutine     | `var int temp;`       |
| parameter | `argument` | Subroutine     | `function f(int n)`   |

**Key insight**: Each variable kind has its own **zero-based index** within its segment.

**Example**:
```jack
class Point {
    field int x, y;           // this 0, this 1
    static int pointCount;    // static 0

    method void move(int dx, int dy) {  // argument 0 (this), argument 1 (dx), argument 2 (dy)
        var int oldX;         // local 0
        let oldX = x;
        let x = x + dx;
        let y = y + dy;
    }
}
```

**Symbol table for `move` method**:
```
Class-level:
  x          | int | field  | 0
  y          | int | field  | 1
  pointCount | int | static | 0

Subroutine-level:
  this | Point | argument | 0  (implicit for methods!)
  dx   | int   | argument | 1
  dy   | int   | argument | 2
  oldX | int   | local    | 0
```

### Subroutine Types and `this` Handling

Jack has three subroutine types with different compilation requirements:

**1. Methods**: Operate on an instance

```jack
method int getX() {
    return x;  // Access field via 'this'
}
```

Compiled to:
```vm
function Point.getX 0    // 0 local variables
push argument 0          // Get 'this' (implicit first argument)
pop pointer 0            // Set THIS pointer
push this 0              // Access field x
return
```

**🎓 Learning Moment**: Methods **always** receive `this` as hidden `argument 0`. The compiler must:
1. Add `this` to symbol table as `argument 0`
2. Emit `push argument 0` + `pop pointer 0` at method start
3. Adjust argument numbering for explicit parameters (start at index 1)

**2. Functions**: No instance association

```jack
function int abs(int x) {
    if (x < 0) {
        return -x;
    }
    return x;
}
```

Compiled to:
```vm
function Math.abs 0      // 0 local variables
push argument 0          // x
push constant 0
lt                       // x < 0
if-goto ABS_NEGATIVE
push argument 0
return
label ABS_NEGATIVE
push argument 0
neg
return
```

**3. Constructors**: Allocate and initialize instance

```jack
constructor Point new(int ax, int ay) {
    let x = ax;
    let y = ay;
    return this;
}
```

Compiled to:
```vm
function Point.new 0                    // 0 local variables
push constant 2                         // Size = 2 fields
call Memory.alloc 1                     // Allocate memory
pop pointer 0                           // Set THIS to allocated memory
push argument 0                         // ax
pop this 0                              // x = ax
push argument 1                         // ay
pop this 1                              // y = ay
push pointer 0                          // Return 'this'
return
```

**🎓 Learning Moment**: Constructors must:
1. Count field variables to determine allocation size
2. Call `Memory.alloc` to get memory block
3. Set `pointer 0` (THIS) to allocated address
4. Initialize fields
5. Return `this` (even if source says `return this;` explicitly)

### Expression Compilation: Infix to Postfix

Jack expressions use infix notation, but stack machines use postfix:

**Infix**: `(x + 5) * (y - 2)`
**Postfix**: `x 5 + y 2 - *`

**Compilation strategy**: Recursive descent with operators applied AFTER operands

```jack
let result = x + y * 3;
```

Parse tree:
```
expression
├── term: x
├── op: +
└── term
    ├── term: y
    ├── op: *
    └── term: 3
```

Compilation (recursive):
1. Compile `x`: `push local 0`
2. Compile `y * 3`:
   - Compile `y`: `push local 1`
   - Compile `3`: `push constant 3`
   - Apply `*`: `call Math.multiply 2`
3. Apply `+`: `add`

Generated VM code:
```vm
push local 0              // x
push local 1              // y
push constant 3           // 3
call Math.multiply 2      // y * 3
add                       // x + (y * 3)
pop local 2               // result
```

**🎓 Learning Moment**: The recursive structure of the parser naturally produces postfix evaluation order. Each `compile_expression()` call:
1. Compiles left term → value on stack
2. Compiles right term → another value on stack
3. Emits operator → consumes top two, pushes result

### Array Access Compilation

Arrays in Jack are heap-allocated objects accessed via pointer arithmetic:

```jack
let arr[i] = 5;
```

**VM code strategy**:
1. Compute base address: `push local 0` (arr variable holds base address)
2. Compute index: `push local 1` (i)
3. Add them: `add` → stack top = address of `arr[i]`
4. Store in `that`: `pop pointer 1` → sets THAT segment base
5. Push value: `push constant 5`
6. Store via THAT: `pop that 0` → memory[arr+i] = 5

Generated code:
```vm
push local 0     // Base address of arr
push local 1     // Index i
add              // Address of arr[i]
push constant 5  // Value to store
pop temp 0       // Save value temporarily
pop pointer 1    // Set THAT = arr + i
push temp 0      // Restore value
pop that 0       // Memory[THAT + 0] = 5
```

**Simpler pattern** (used in practice):
```vm
push local 1     // i
push local 0     // arr
add              // arr + i
push constant 5  // value
pop temp 0       // Save value
pop pointer 1    // THAT = arr + i
push temp 0      // Restore value
pop that 0       // Store to arr[i]
```

### Method Call Compilation

Method calls require computing the object reference:

```jack
do point.move(dx, dy);
```

**Compilation steps**:
1. Push object reference as hidden first argument
2. Push explicit arguments
3. Call method
4. Handle return value (for `do` statements, discard it)

```vm
push local 2        // 'point' variable (object reference)
push local 3        // dx
push local 4        // dy
call Point.move 3   // 3 arguments (object + dx + dy)
pop temp 0          // Discard return value (do statement)
```

**🎓 Learning Moment**: Methods receive object reference as `argument 0`. The caller must push the object before explicit arguments. Total argument count = 1 + number of parameters.

### String Constant Compilation

String literals require special handling:

```jack
do Output.printString("Hello");
```

**Compilation strategy**:
1. Create String object: `call String.new 1` (with character count)
2. Append each character: `call String.appendChar 2` (for each char)
3. Use the string

```vm
push constant 5           // Length of "Hello"
call String.new 1         // Allocate string object
push constant 72          // 'H'
call String.appendChar 2  // Append to string
push constant 101         // 'e'
call String.appendChar 2
push constant 108         // 'l'
call String.appendChar 2
push constant 108         // 'l'
call String.appendChar 2
push constant 111         // 'o'
call String.appendChar 2  // String is now on stack
call Output.printString 1 // Print it
pop temp 0                // Discard return value
```

## Learning Path

### Step 1: Symbol Table Foundation (2-3 hours)

**Goal**: Implement two-level symbol table for variable tracking

**Concepts**:
- Variable properties: name, type, kind (field/static/var/argument), index
- Scope levels: class-level (fields, statics) and subroutine-level (locals, arguments)
- Index allocation: Zero-based per kind

**Implementation**:

```python
class SymbolTable:
    """Two-level symbol table for Jack compiler."""

    def __init__(self):
        """Initialize class-level and subroutine-level tables."""
        self.class_table = {}        # Fields and statics
        self.subroutine_table = {}   # Locals and arguments
        self.indexes = {
            'field': 0,
            'static': 0,
            'local': 0,
            'argument': 0
        }

    def start_subroutine(self):
        """Start new subroutine scope (clear subroutine table)."""
        self.subroutine_table = {}
        self.indexes['local'] = 0
        self.indexes['argument'] = 0

    def define(self, name, var_type, kind):
        """Add variable to appropriate table.

        Args:
            name: Variable name
            var_type: Variable type (int, char, boolean, or class name)
            kind: 'field', 'static', 'local', or 'argument'
        """
        index = self.indexes[kind]
        entry = {
            'type': var_type,
            'kind': kind,
            'index': index
        }

        if kind in ('field', 'static'):
            self.class_table[name] = entry
        else:  # local or argument
            self.subroutine_table[name] = entry

        self.indexes[kind] += 1

    def var_count(self, kind):
        """Get count of variables of given kind.

        Args:
            kind: 'field', 'static', 'local', or 'argument'

        Returns:
            Number of variables of that kind
        """
        return self.indexes[kind]

    def kind_of(self, name):
        """Get kind of named variable.

        Args:
            name: Variable name

        Returns:
            'field', 'static', 'local', 'argument', or None if not found
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name]['kind']
        elif name in self.class_table:
            return self.class_table[name]['kind']
        return None

    def type_of(self, name):
        """Get type of named variable."""
        if name in self.subroutine_table:
            return self.subroutine_table[name]['type']
        elif name in self.class_table:
            return self.class_table[name]['type']
        return None

    def index_of(self, name):
        """Get index of named variable."""
        if name in self.subroutine_table:
            return self.subroutine_table[name]['index']
        elif name in self.class_table:
            return self.class_table[name]['index']
        return None
```

**Testing**:

```python
symbol_table = SymbolTable()

# Class-level variables
symbol_table.define('x', 'int', 'field')
symbol_table.define('y', 'int', 'field')
symbol_table.define('pointCount', 'int', 'static')

# Method parameters and locals
symbol_table.start_subroutine()
symbol_table.define('this', 'Point', 'argument')  # Implicit for methods
symbol_table.define('dx', 'int', 'argument')
symbol_table.define('dy', 'int', 'argument')
symbol_table.define('temp', 'int', 'local')

# Verify lookups
assert symbol_table.kind_of('x') == 'field'
assert symbol_table.index_of('x') == 0
assert symbol_table.index_of('dx') == 1  # argument 0 is 'this'
assert symbol_table.var_count('field') == 2
assert symbol_table.var_count('local') == 1
```

**🎓 Key Insight**: The symbol table is the compiler's "memory" of what variables exist and where they live in VM memory.

### Step 2: VM Writer (1-2 hours)

**Goal**: Create abstraction layer for emitting VM commands

**Implementation**:

```python
class VMWriter:
    """Generates VM commands."""

    def __init__(self, output_file):
        """Initialize with output file path."""
        self.output_file = output_file
        self.commands = []

    def write_push(self, segment, index):
        """Write push command.

        Args:
            segment: 'constant', 'local', 'argument', 'this', 'that', 'temp', 'pointer', 'static'
            index: Segment index (integer)
        """
        self.commands.append(f'push {segment} {index}')

    def write_pop(self, segment, index):
        """Write pop command."""
        self.commands.append(f'pop {segment} {index}')

    def write_arithmetic(self, command):
        """Write arithmetic/logical command.

        Args:
            command: 'add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not'
        """
        self.commands.append(command)

    def write_label(self, label):
        """Write label command."""
        self.commands.append(f'label {label}')

    def write_goto(self, label):
        """Write goto command."""
        self.commands.append(f'goto {label}')

    def write_if(self, label):
        """Write if-goto command."""
        self.commands.append(f'if-goto {label}')

    def write_call(self, name, n_args):
        """Write function call.

        Args:
            name: Function name (e.g., 'Math.multiply')
            n_args: Number of arguments
        """
        self.commands.append(f'call {name} {n_args}')

    def write_function(self, name, n_locals):
        """Write function declaration.

        Args:
            name: Function name (e.g., 'Point.move')
            n_locals: Number of local variables
        """
        self.commands.append(f'function {name} {n_locals}')

    def write_return(self):
        """Write return command."""
        self.commands.append('return')

    def close(self):
        """Write all commands to file."""
        with open(self.output_file, 'w') as f:
            f.write('\n'.join(self.commands) + '\n')
```

**Testing**:

```python
vm = VMWriter('test.vm')
vm.write_function('Main.main', 1)
vm.write_push('constant', 10)
vm.write_pop('local', 0)
vm.write_push('local', 0)
vm.write_push('constant', 5)
vm.write_arithmetic('add')
vm.write_return()
vm.close()

# Should produce:
# function Main.main 1
# push constant 10
# pop local 0
# push local 0
# push constant 5
# add
# return
```

### Step 3: Expression Compilation (3-4 hours)

**Goal**: Compile expressions to VM stack operations

**Concepts**:
- Terms: integerConstant, stringConstant, keywordConstant, varName, array[index], subroutineCall, (expression), unaryOp term
- Binary operators: +, -, *, /, &, |, <, >, =
- Unary operators: -, ~ (negation, bitwise NOT)
- Operator mapping to VM commands

**Expression Compilation Algorithm**:

```python
def compile_expression(self):
    """Compile expression: term (op term)*"""
    self.compile_term()  # First term

    while self.current_token in {'+', '-', '*', '/', '&', '|', '<', '>', '='}:
        op = self.current_token
        self.advance()  # Consume operator
        self.compile_term()  # Second term
        self.compile_operator(op)  # Apply operator

def compile_operator(self, op):
    """Emit VM code for operator."""
    if op == '+':
        self.vm_writer.write_arithmetic('add')
    elif op == '-':
        self.vm_writer.write_arithmetic('sub')
    elif op == '=':
        self.vm_writer.write_arithmetic('eq')
    elif op == '>':
        self.vm_writer.write_arithmetic('gt')
    elif op == '<':
        self.vm_writer.write_arithmetic('lt')
    elif op == '&':
        self.vm_writer.write_arithmetic('and')
    elif op == '|':
        self.vm_writer.write_arithmetic('or')
    elif op == '*':
        self.vm_writer.write_call('Math.multiply', 2)
    elif op == '/':
        self.vm_writer.write_call('Math.divide', 2)

def compile_term(self):
    """Compile a term."""
    # Integer constant
    if self.token_type() == 'INT_CONST':
        value = self.int_val()
        self.vm_writer.write_push('constant', value)
        self.advance()

    # String constant
    elif self.token_type() == 'STRING_CONST':
        string_val = self.string_val()
        self.compile_string_constant(string_val)
        self.advance()

    # Keyword constant (true, false, null, this)
    elif self.token_type() == 'KEYWORD':
        keyword = self.keyword()
        if keyword == 'true':
            self.vm_writer.write_push('constant', 1)
            self.vm_writer.write_arithmetic('neg')  # -1 (all bits set)
        elif keyword == 'false' or keyword == 'null':
            self.vm_writer.write_push('constant', 0)
        elif keyword == 'this':
            self.vm_writer.write_push('pointer', 0)
        self.advance()

    # Variable, array access, or subroutine call
    elif self.token_type() == 'IDENTIFIER':
        name = self.identifier()
        self.advance()

        # Array access: varName[expression]
        if self.current_token == '[':
            self.compile_array_access(name)

        # Subroutine call: name(...) or name.method(...)
        elif self.current_token in {'(', '.'}:
            self.compile_subroutine_call(name)

        # Variable reference
        else:
            kind = self.symbol_table.kind_of(name)
            index = self.symbol_table.index_of(name)
            segment = self.kind_to_segment(kind)
            self.vm_writer.write_push(segment, index)

    # (expression)
    elif self.current_token == '(':
        self.advance()  # Consume '('
        self.compile_expression()
        self.advance()  # Consume ')'

    # unaryOp term
    elif self.current_token in {'-', '~'}:
        op = self.current_token
        self.advance()
        self.compile_term()
        if op == '-':
            self.vm_writer.write_arithmetic('neg')
        elif op == '~':
            self.vm_writer.write_arithmetic('not')

def kind_to_segment(self, kind):
    """Map symbol table kind to VM segment."""
    if kind == 'field':
        return 'this'
    elif kind == 'static':
        return 'static'
    elif kind == 'local':
        return 'local'
    elif kind == 'argument':
        return 'argument'
```

**Example**:

```jack
let x = (y + 5) * 3;
```

Generates:
```vm
push local 1    // y
push constant 5
add             // y + 5
push constant 3
call Math.multiply 2  // (y + 5) * 3
pop local 0     // x
```

**🎓 Key Insight**: Recursive descent naturally produces postfix (stack-friendly) evaluation order from infix expressions.

### Step 4: Statement Compilation (2-3 hours)

**Goal**: Compile Jack statements to VM code

**Let Statement**: `let varName = expression;` or `let arr[index] = expression;`

```python
def compile_let(self):
    """Compile let statement."""
    self.advance()  # Consume 'let'
    var_name = self.identifier()
    self.advance()

    # Array assignment: arr[index] = expression
    if self.current_token == '[':
        self.advance()  # Consume '['

        # Compute arr + index
        kind = self.symbol_table.kind_of(var_name)
        index = self.symbol_table.index_of(var_name)
        segment = self.kind_to_segment(kind)
        self.vm_writer.write_push(segment, index)  # Base address
        self.compile_expression()  # Index
        self.vm_writer.write_arithmetic('add')  # arr + index

        self.advance()  # Consume ']'
        self.advance()  # Consume '='

        # Compile value to store
        self.compile_expression()

        # Store to array
        self.vm_writer.write_pop('temp', 0)    # Save value
        self.vm_writer.write_pop('pointer', 1)  # THAT = arr + index
        self.vm_writer.write_push('temp', 0)    # Restore value
        self.vm_writer.write_pop('that', 0)     # Memory[arr+index] = value

    # Simple assignment: var = expression
    else:
        self.advance()  # Consume '='
        self.compile_expression()
        kind = self.symbol_table.kind_of(var_name)
        index = self.symbol_table.index_of(var_name)
        segment = self.kind_to_segment(kind)
        self.vm_writer.write_pop(segment, index)

    self.advance()  # Consume ';'
```

**If Statement**: `if (expression) { statements } else { statements }`

```python
def compile_if(self):
    """Compile if statement."""
    self.label_counter += 1
    label_true = f'IF_TRUE{self.label_counter}'
    label_false = f'IF_FALSE{self.label_counter}'
    label_end = f'IF_END{self.label_counter}'

    self.advance()  # Consume 'if'
    self.advance()  # Consume '('

    # Compile condition
    self.compile_expression()
    self.vm_writer.write_arithmetic('not')  # Negate (jump if false)
    self.vm_writer.write_if(label_false)

    self.advance()  # Consume ')'
    self.advance()  # Consume '{'

    # Compile if-true statements
    self.compile_statements()
    self.vm_writer.write_goto(label_end)

    self.advance()  # Consume '}'

    # Else clause?
    self.vm_writer.write_label(label_false)
    if self.current_token == 'else':
        self.advance()  # Consume 'else'
        self.advance()  # Consume '{'
        self.compile_statements()
        self.advance()  # Consume '}'

    self.vm_writer.write_label(label_end)
```

**While Statement**: `while (expression) { statements }`

```python
def compile_while(self):
    """Compile while statement."""
    self.label_counter += 1
    label_start = f'WHILE_START{self.label_counter}'
    label_end = f'WHILE_END{self.label_counter}'

    self.vm_writer.write_label(label_start)

    self.advance()  # Consume 'while'
    self.advance()  # Consume '('

    # Compile condition
    self.compile_expression()
    self.vm_writer.write_arithmetic('not')  # Negate
    self.vm_writer.write_if(label_end)  # Exit if false

    self.advance()  # Consume ')'
    self.advance()  # Consume '{'

    # Compile loop body
    self.compile_statements()
    self.vm_writer.write_goto(label_start)  # Loop back

    self.advance()  # Consume '}'
    self.vm_writer.write_label(label_end)
```

**Do Statement**: `do subroutineCall;`

```python
def compile_do(self):
    """Compile do statement."""
    self.advance()  # Consume 'do'

    # Compile subroutine call
    name = self.identifier()
    self.advance()
    self.compile_subroutine_call(name)

    # Discard return value (do statements ignore return value)
    self.vm_writer.write_pop('temp', 0)

    self.advance()  # Consume ';'
```

**Return Statement**: `return expression?;`

```python
def compile_return(self):
    """Compile return statement."""
    self.advance()  # Consume 'return'

    # Void function: return 0
    if self.current_token == ';':
        self.vm_writer.write_push('constant', 0)
    else:
        self.compile_expression()

    self.vm_writer.write_return()
    self.advance()  # Consume ';'
```

### Step 5: Subroutine and Class Compilation (3-4 hours)

**Goal**: Compile functions, methods, constructors, and complete classes

**Subroutine Compilation**:

```python
def compile_subroutine(self):
    """Compile method, function, or constructor."""
    subroutine_type = self.keyword()  # 'function', 'method', 'constructor'
    self.advance()

    return_type = self.current_token
    self.advance()

    subroutine_name = self.identifier()
    self.advance()

    # Start new subroutine scope
    self.symbol_table.start_subroutine()

    # Methods have implicit 'this' as argument 0
    if subroutine_type == 'method':
        self.symbol_table.define('this', self.class_name, 'argument')

    # Compile parameter list
    self.advance()  # Consume '('
    self.compile_parameter_list()
    self.advance()  # Consume ')'

    # Compile subroutine body
    self.advance()  # Consume '{'

    # Compile variable declarations
    while self.current_token == 'var':
        self.compile_var_dec()

    # Emit function declaration
    n_locals = self.symbol_table.var_count('local')
    function_name = f'{self.class_name}.{subroutine_name}'
    self.vm_writer.write_function(function_name, n_locals)

    # Constructor: Allocate memory for object
    if subroutine_type == 'constructor':
        n_fields = self.symbol_table.var_count('field')
        self.vm_writer.write_push('constant', n_fields)
        self.vm_writer.write_call('Memory.alloc', 1)
        self.vm_writer.write_pop('pointer', 0)  # THIS = allocated memory

    # Method: Set up 'this' pointer
    elif subroutine_type == 'method':
        self.vm_writer.write_push('argument', 0)  # Get 'this'
        self.vm_writer.write_pop('pointer', 0)    # Set THIS pointer

    # Compile statements
    self.compile_statements()

    self.advance()  # Consume '}'
```

**Class Compilation**:

```python
def compile_class(self):
    """Compile a complete class."""
    self.advance()  # Consume 'class'

    self.class_name = self.identifier()
    self.advance()

    self.advance()  # Consume '{'

    # Compile class variable declarations
    while self.current_token in {'static', 'field'}:
        self.compile_class_var_dec()

    # Compile subroutines
    while self.current_token in {'constructor', 'function', 'method'}:
        self.compile_subroutine()

    self.advance()  # Consume '}'

def compile_class_var_dec(self):
    """Compile field or static variable declaration."""
    kind = self.current_token  # 'field' or 'static'
    self.advance()

    var_type = self.current_token
    self.advance()

    # First variable
    var_name = self.identifier()
    self.symbol_table.define(var_name, var_type, kind)
    self.advance()

    # Additional variables: (, varName)*
    while self.current_token == ',':
        self.advance()  # Consume ','
        var_name = self.identifier()
        self.symbol_table.define(var_name, var_type, kind)
        self.advance()

    self.advance()  # Consume ';'
```

**🎓 Key Insight**: The compiler must handle three distinct subroutine patterns:
- **Functions**: No special setup
- **Methods**: Push `argument 0` → pop to `pointer 0` (set THIS)
- **Constructors**: Allocate memory → set THIS → initialize fields

### Step 6: Full Compiler Integration (2-3 hours)

**Goal**: Integrate all components into a complete compiler

**Main Compiler Class**:

```python
from tokenizer import JackTokenizer
from symbol_table import SymbolTable
from vm_writer import VMWriter

class CompilationEngine:
    """Jack compiler: source code → VM code."""

    def __init__(self, input_file, output_file):
        self.tokenizer = JackTokenizer(input_file)
        self.symbol_table = SymbolTable()
        self.vm_writer = VMWriter(output_file)
        self.class_name = None
        self.label_counter = 0

        # Advance to first token
        self.tokenizer.advance()

    def compile(self):
        """Compile the Jack source file."""
        self.compile_class()
        self.vm_writer.close()

    # ... all compilation methods from previous steps ...
```

**Main Program**:

```python
#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from compilation_engine import CompilationEngine

def compile_file(jack_file):
    """Compile a single Jack file to VM code."""
    vm_file = jack_file.replace('.jack', '.vm')
    print(f'Compiling: {jack_file}')

    try:
        compiler = CompilationEngine(jack_file, vm_file)
        compiler.compile()
        print(f'  Output: {vm_file}')
    except Exception as e:
        print(f'  ERROR: {e}')

def compile_directory(directory):
    """Compile all .jack files in a directory."""
    path = Path(directory)
    jack_files = sorted(path.glob('*.jack'))

    if not jack_files:
        print(f'No .jack files found in {directory}')
        return

    print(f'Found {len(jack_files)} Jack file(s)\n')
    for jack_file in jack_files:
        compile_file(str(jack_file))
        print()

def main():
    if len(sys.argv) != 2:
        print('Usage: python3 jack_compiler.py <input>')
        print('  <input>: .jack file or directory')
        sys.exit(1)

    input_path = sys.argv[1]

    if os.path.isfile(input_path):
        if not input_path.endswith('.jack'):
            print('ERROR: Input file must have .jack extension')
            sys.exit(1)
        compile_file(input_path)
    elif os.path.isdir(input_path):
        compile_directory(input_path)
    else:
        print(f'ERROR: {input_path} not found')
        sys.exit(1)

if __name__ == '__main__':
    main()
```

## Deep Dive: Critical Implementation Details

### Subroutine Call Compilation

Subroutine calls have three forms:

**1. Function call**: `Math.abs(x)`

```python
# No object reference needed
self.vm_writer.write_push('local', 0)  # Push x
self.vm_writer.write_call('Math.abs', 1)  # 1 argument
```

**2. Method call on variable**: `point.move(dx, dy)`

```python
# Push object reference first
kind = self.symbol_table.kind_of('point')
index = self.symbol_table.index_of('point')
segment = self.kind_to_segment(kind)
self.vm_writer.write_push(segment, index)  # Object reference

# Push arguments
self.vm_writer.write_push('local', 1)  # dx
self.vm_writer.write_push('local', 2)  # dy

# Call method (object + 2 arguments = 3 total)
self.vm_writer.write_call('Point.move', 3)
```

**3. Method call on `this`**: `move(dx, dy)` (inside Point class)

```python
# Push 'this' as argument 0
self.vm_writer.write_push('pointer', 0)

# Push arguments
self.vm_writer.write_push('argument', 1)  # dx
self.vm_writer.write_push('argument', 2)  # dy

# Call method
self.vm_writer.write_call('Point.move', 3)
```

**Implementation**:

```python
def compile_subroutine_call(self, name):
    """Compile subroutine call: name(...) or obj.method(...)"""
    n_args = 0

    # Method call: obj.method() or Class.function()
    if self.current_token == '.':
        self.advance()  # Consume '.'
        method_name = self.identifier()
        self.advance()

        # Check if 'name' is a variable (object reference)
        if self.symbol_table.kind_of(name) is not None:
            # Method call on object: push object reference
            kind = self.symbol_table.kind_of(name)
            index = self.symbol_table.index_of(name)
            var_type = self.symbol_table.type_of(name)
            segment = self.kind_to_segment(kind)

            self.vm_writer.write_push(segment, index)
            n_args = 1  # Object is hidden first argument

            # Full method name: ClassName.methodName
            full_name = f'{var_type}.{method_name}'
        else:
            # Function call or constructor: Class.function()
            full_name = f'{name}.{method_name}'

    # Method call on 'this': method() (implicit this.method())
    else:
        full_name = f'{self.class_name}.{name}'
        self.vm_writer.write_push('pointer', 0)  # Push 'this'
        n_args = 1

    # Compile argument list
    self.advance()  # Consume '('
    n_args += self.compile_expression_list()
    self.advance()  # Consume ')'

    # Emit call
    self.vm_writer.write_call(full_name, n_args)

def compile_expression_list(self):
    """Compile comma-separated expression list. Returns count."""
    n_args = 0

    if self.current_token != ')':
        self.compile_expression()
        n_args = 1

        while self.current_token == ',':
            self.advance()  # Consume ','
            self.compile_expression()
            n_args += 1

    return n_args
```

### String Constant Compilation

```python
def compile_string_constant(self, string_val):
    """Compile string constant using String library."""
    # Create String object with capacity
    self.vm_writer.write_push('constant', len(string_val))
    self.vm_writer.write_call('String.new', 1)

    # Append each character
    for char in string_val:
        self.vm_writer.write_push('constant', ord(char))
        self.vm_writer.write_call('String.appendChar', 2)

    # String object is now on stack
```

### Operator Precedence

Jack has **no operator precedence** in the grammar—all operators are left-associative with equal precedence. This simplifies parsing but requires parentheses for clarity:

```jack
// These are DIFFERENT:
let x = a + b * c;  // Parsed as: (a + b) * c
let x = a + (b * c);  // Explicit precedence
```

In practice, this doesn't affect compilation because the grammar enforces left-to-right evaluation regardless of the operators involved.

## Common Pitfalls

### Pitfall 1: Forgetting `this` for Methods

**Wrong**:
```python
# Method compilation
self.vm_writer.write_function('Point.move', n_locals)
# MISSING: Set up 'this' pointer!
```

**Right**:
```python
# Method compilation
self.vm_writer.write_function('Point.move', n_locals)
self.vm_writer.write_push('argument', 0)  # Get 'this'
self.vm_writer.write_pop('pointer', 0)    # Set THIS
```

### Pitfall 2: Incorrect Array Assignment

**Wrong**:
```python
# let arr[i] = value
self.vm_writer.write_push('local', 0)  # arr
self.vm_writer.write_push('local', 1)  # i
self.vm_writer.write_arithmetic('add')
self.compile_expression()  # value
self.vm_writer.write_pop('that', 0)  # WRONG: THAT not set!
```

**Right**:
```python
# let arr[i] = value
self.vm_writer.write_push('local', 0)  # arr
self.vm_writer.write_push('local', 1)  # i
self.vm_writer.write_arithmetic('add')  # arr + i
self.compile_expression()  # value
self.vm_writer.write_pop('temp', 0)    # Save value
self.vm_writer.write_pop('pointer', 1)  # THAT = arr + i
self.vm_writer.write_push('temp', 0)    # Restore value
self.vm_writer.write_pop('that', 0)     # Memory[THAT] = value
```

### Pitfall 3: Wrong Argument Count for Methods

**Wrong**:
```python
# Calling point.move(dx, dy)
self.vm_writer.write_push('local', 2)  # dx
self.vm_writer.write_push('local', 3)  # dy
self.vm_writer.write_call('Point.move', 2)  # WRONG: Missing object!
```

**Right**:
```python
# Calling point.move(dx, dy)
self.vm_writer.write_push('local', 0)  # point (object reference)
self.vm_writer.write_push('local', 2)  # dx
self.vm_writer.write_push('local', 3)  # dy
self.vm_writer.write_call('Point.move', 3)  # 3 arguments (obj + dx + dy)
```

### Pitfall 4: Constructor Not Returning `this`

**Wrong**:
```python
# Constructor compilation
self.vm_writer.write_function('Point.new', 0)
self.vm_writer.write_push('constant', 2)
self.vm_writer.write_call('Memory.alloc', 1)
self.vm_writer.write_pop('pointer', 0)
# ... initialize fields ...
self.vm_writer.write_return()  # WRONG: Returning 0!
```

**Right**:
```python
# Constructor compilation
self.vm_writer.write_function('Point.new', 0)
self.vm_writer.write_push('constant', 2)
self.vm_writer.write_call('Memory.alloc', 1)
self.vm_writer.write_pop('pointer', 0)
# ... initialize fields ...
self.vm_writer.write_push('pointer', 0)  # Push 'this'
self.vm_writer.write_return()  # Return 'this'
```

### Pitfall 5: Not Discarding `do` Statement Return Values

**Wrong**:
```python
# do Output.printString("Hello");
self.vm_writer.write_push('constant', 5)  # String length
# ... build string ...
self.vm_writer.write_call('Output.printString', 1)
# WRONG: Return value stays on stack!
```

**Right**:
```python
# do Output.printString("Hello");
self.vm_writer.write_push('constant', 5)
# ... build string ...
self.vm_writer.write_call('Output.printString', 1)
self.vm_writer.write_pop('temp', 0)  # Discard return value
```

## Extension Ideas

### Level 1: Optimization
- **Constant folding**: Evaluate constant expressions at compile time
- **Dead code elimination**: Skip code after `return` statements
- **Peephole optimization**: Replace `push constant 1; add` with `inc`

### Level 2: Error Handling
- **Type checking**: Verify type compatibility in assignments and calls
- **Undefined variable detection**: Catch references to undeclared variables
- **Return path verification**: Ensure all code paths return values

### Level 3: Language Extensions
- **For loops**: Add `for (init; condition; increment) { ... }` syntax
- **Switch statements**: Multi-way branching
- **Break/continue**: Early loop exit

### Level 4: Advanced Features
- **Array literals**: `let arr = [1, 2, 3, 4, 5];`
- **String interpolation**: `"Hello, {name}!"`
- **Anonymous functions**: Lambda expressions

### Level 5: Compiler Infrastructure
- **Intermediate representation**: Convert to SSA form before VM emission
- **Register allocation**: Simulate registers using temp variables
- **Separate compilation**: Compile classes independently, link later

## Real-World Connections

### Production Compilers

**JavaScript (V8)**:
- Tokenizer → Parser → AST → Bytecode → JIT compiler → Machine code
- Similar two-phase design: Frontend (parsing) + Backend (code generation)

**Python (CPython)**:
- Tokenizer → Parser → AST → Bytecode → Interpreter
- Stack-based bytecode like Jack VM

**Java (javac)**:
- Source → Bytecode (.class files) → JVM interprets/JITs
- `.vm` files are analogous to `.class` files

**C (gcc/clang)**:
- C source → Intermediate representation (LLVM IR) → Machine code
- Multi-pass compilation with symbol tables and optimization phases

### Symbol Tables in Practice

**Scope handling**:
- Jack: Two levels (class, subroutine)
- C: Multiple levels (global, function, block)
- Python: LEGB rule (Local, Enclosing, Global, Built-in)

**Type systems**:
- Jack: Statically typed (types known at compile time)
- JavaScript: Dynamically typed (runtime type checking)
- TypeScript: Static type checking over JavaScript

### Code Generation Techniques

**Stack-based VMs**:
- JVM (Java Virtual Machine)
- CPython bytecode
- WebAssembly (stack machine with some register operations)

**Register-based VMs**:
- Lua VM
- Dalvik (Android, before ART)
- Generally faster but more complex to compile to

**Direct machine code generation**:
- Rust: Compiles to native code via LLVM
- Go: Custom backend generating machine code
- Faster execution, platform-specific binaries

## Success Criteria

Your compiler is working correctly when:

1. **Variables compile correctly**: Fields, statics, locals, arguments map to correct segments
2. **Expressions evaluate properly**: Arithmetic, logical, comparison operators work
3. **Statements execute as expected**: let, if, while, do, return produce correct control flow
4. **Functions work**: Can call functions and receive return values
5. **Methods work**: Object methods access fields correctly via `this`
6. **Constructors allocate memory**: Objects created with correct size and initialization
7. **Arrays function**: Array access reads/writes correct memory locations
8. **Strings work**: String constants compile to String.new + appendChar calls
9. **Programs run**: Complete Jack programs compile to VM code that executes correctly
10. **All test programs pass**: Seven, ConvertToBin, Square, Average, Pong, ComplexArrays, etc.

**Testing workflow**:
```bash
# Compile Jack source to VM code
python3 jack_compiler.py Seven.jack

# Translate VM code to assembly
python3 vm_translator.py Seven.vm

# Assemble to machine code
python3 assembler.py Seven.asm

# Run on computer emulator or hardware
# (Or use VM emulator to run .vm file directly)
```

Congratulations on completing the compiler! You've built a complete toolchain from high-level source code to executable machine instructions. This is one of the most significant achievements in computer science education.

**Total Learning Time**: 15-20 hours
**Lines of Code**: ~800-1000 (Python implementation)
**Complexity**: Advanced - requires integrating multiple concepts simultaneously
