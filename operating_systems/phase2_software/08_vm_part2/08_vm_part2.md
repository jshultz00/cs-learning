# Project 8: Stack-Based Virtual Machine (Part 2)

**Objective**: Extend VM translator with program flow and function call capabilities

## Background Concepts

### What You've Built So Far

**Project 7: VM Part 1 (Stack Arithmetic and Memory)**
- ✅ Stack-based computation model (push/pop operations)
- ✅ Nine arithmetic/logical operations (add, sub, neg, eq, gt, lt, and, or, not)
- ✅ Eight memory segments (constant, local, argument, this, that, temp, pointer, static)
- ✅ VM-to-assembly translation with unique label generation
- ✅ Bootstrap code for stack initialization (SP = 256)

**What you can do now**:
```vm
// Simple calculations with memory
push constant 10
pop local 0       // local[0] = 10
push constant 5
push local 0
add               // 5 + 10 = 15
pop static 0      // static[0] = 15
```

**What you CANNOT do yet**:
```vm
// Loops - NO LABEL/GOTO support!
(LOOP)
    push local 0
    push constant 1
    add
    pop local 0
    goto LOOP

// Functions - NO CALL/RETURN support!
function fibonacci 1
    // ... recursive implementation
    call fibonacci 1
    return
```

### The Problem: No Control Flow or Functions

Your VM Part 1 translator can compute expressions and manage memory, but it **executes linearly** from top to bottom. Real programs need:

**Problem 1: No conditional execution**
```vm
// How do you implement: if (x > 10) { y = 5; }?
push local 0      // x
push constant 10
gt                // x > 10 (true = -1, false = 0)
// NOW WHAT? No way to skip the next instruction!
push constant 5
pop local 1       // Always executes!
```

**Problem 2: No loops**
```vm
// How do you implement: for (i = 0; i < 10; i++) { sum += i; }?
// NO LABELS - can't mark loop start
// NO GOTO - can't jump back to loop start
// NO IF-GOTO - can't exit loop conditionally
```

**Problem 3: No functions**
```vm
// How do you call a function?
// - Where does the return address go?
// - How do you pass arguments?
// - How do you allocate local variables?
// - How do you return values?
// - How do you handle recursion?
```

**Problem 4: No code reuse**
```vm
// Want to compute factorial(5)?
// Must inline all the multiplication logic
// Want to compute factorial(3)?
// Copy-paste the same logic again!
// No function abstraction = massive code duplication
```

### The Solution: Program Flow + Function Calls

Project 8 adds three new command types to complete the VM:

**1. Program Flow Commands** (labels and jumps):
```vm
label LOOP_START          // Mark location in code
goto LOOP_START           // Unconditional jump
if-goto LOOP_START        // Conditional jump (if stack top is non-zero)
```

**2. Function Definition**:
```vm
function functionName nLocals    // Declare function with local variable count
```

**3. Function Invocation**:
```vm
call functionName nArgs          // Call function with argument count
return                           // Return from function
```

**Why this completes the VM**:
- **Turing-complete**: With conditionals + loops, can express any algorithm
- **Structured programming**: Functions enable modular code organization
- **Recursion**: Stack frames enable self-calling functions
- **High-level compilation**: Compilers can now target a complete VM

### Program Flow: Labels and Jumps

**Three program flow commands**:

```vm
label LABEL_NAME    // Mark this location (doesn't execute, just marks address)
goto LABEL_NAME     // Unconditional jump to label
if-goto LABEL_NAME  // Pop stack; if value ≠ 0, jump to label
```

**Example: Infinite loop**
```vm
label LOOP
    // ... loop body ...
    goto LOOP    // Jump back to start
```

**Example: Conditional execution**
```vm
// Implement: if (x > 10) { y = 5; }
push local 0      // x
push constant 10
gt                // x > 10 (pushes -1 if true, 0 if false)
if-goto SET_Y     // Jump if stack top is non-zero (true)
goto END          // Skip the assignment
label SET_Y
    push constant 5
    pop local 1   // y = 5
label END
```

**Example: While loop**
```vm
// Implement: while (x > 0) { x--; sum += x; }
label WHILE_START
    push local 0      // x
    push constant 0
    gt                // x > 0?
    not               // Invert (jump if false to exit)
    if-goto WHILE_END

    // Loop body
    push local 0
    push constant 1
    sub
    pop local 0       // x--

    push local 1      // sum
    push local 0      // x
    add
    pop local 1       // sum += x

    goto WHILE_START
label WHILE_END
```

🎓 **Key insight**: `if-goto` tests the **stack top value**, not a condition directly. The pattern is: (1) compute boolean → (2) if-goto → (3) branch based on result. This mirrors how real CPUs implement conditional branches!

### Function Calls: The Stack Frame

When you call a function, the VM must:
1. **Save return address**: Where to resume after function returns
2. **Pass arguments**: Make caller's values available to callee
3. **Allocate local variables**: Give function its own workspace
4. **Preserve caller state**: Save LCL, ARG, THIS, THAT pointers
5. **Return value**: Push result onto caller's stack

**Stack frame structure**:
```
Stack during function call:
┌──────────────────────────────────────┐
│  Caller's working stack              │
├──────────────────────────────────────┤
│  arg 0                               │  ← Arguments pushed by caller
│  arg 1                               │
│  ...                                 │
│  arg n-1                             │  ← ARG points here (first arg)
├──────────────────────────────────────┤
│  return address                      │  ← Where to jump after return
│  saved LCL                           │  ← Caller's LCL pointer
│  saved ARG                           │  ← Caller's ARG pointer
│  saved THIS                          │  ← Caller's THIS pointer
│  saved THAT                          │  ← Caller's THAT pointer
├──────────────────────────────────────┤
│  local 0                             │  ← LCL points here
│  local 1                             │
│  ...                                 │
│  local k-1                           │
├──────────────────────────────────────┤
│  Function's working stack            │  ← SP points here (top of stack)
└──────────────────────────────────────┘
```

**Three function commands**:

**1. Function declaration**: `function functionName nLocals`
```vm
// Declare function with 2 local variables
function multiply 2
    // Function body uses local 0, local 1
    // LCL points to first local variable
    // ARG points to first argument (set by caller)
```

**2. Function call**: `call functionName nArgs`
```vm
// Call multiply with 2 arguments (already on stack)
push constant 7
push constant 8
call multiply 2    // multiply(7, 8)
// Return value is now on stack
```

**3. Function return**: `return`
```vm
function multiply 2
    // ... compute result, push onto stack ...
    return         // Return to caller with result on stack
```

**Complete example**:
```vm
// Main function
function main 1
    push constant 7
    push constant 8
    call multiply 2    // Call multiply(7, 8)
    pop local 0        // local[0] = result (56)
    push constant 0
    return

// Multiply function (a * b using repeated addition)
function multiply 2
    push constant 0
    pop local 0        // local[0] = 0 (accumulator)
    push argument 1
    pop local 1        // local[1] = b (counter)
label MULT_LOOP
    push local 1
    push constant 0
    eq
    if-goto MULT_END   // if counter == 0, exit loop

    push local 0
    push argument 0
    add
    pop local 0        // accumulator += a

    push local 1
    push constant 1
    sub
    pop local 1        // counter--

    goto MULT_LOOP
label MULT_END
    push local 0       // Push result onto stack
    return
```

🎓 **Key insight**: Each function call creates a new **activation record** (stack frame) with its own local variables and arguments. This enables recursion—factorial(5) can call factorial(4), which calls factorial(3), and each has its own independent stack frame!

### Call/Return Implementation Strategy

The `call` and `return` commands must manipulate stack frames carefully to preserve program state.

**`call functionName nArgs` implementation**:

1. **Push return address**: Where to resume after function returns
2. **Save caller's segment pointers**: LCL, ARG, THIS, THAT
3. **Set ARG for callee**: Points to first argument
4. **Set LCL for callee**: Points to first local variable
5. **Transfer control**: Jump to function's entry point

**Pseudo-code**:
```python
# call functionName nArgs
# Assume caller has already pushed nArgs arguments onto stack

# Save return address (label for instruction after call)
push return_address

# Save caller's segment pointers
push LCL
push ARG
push THIS
push THAT

# Reposition ARG for callee (points to first argument)
ARG = SP - nArgs - 5

# Reposition LCL for callee (points to first local)
LCL = SP

# Transfer control
goto functionName

(return_address)    # Label to return to
```

**`return` implementation**:

1. **Save return value**: Temp storage (already on stack)
2. **Restore caller's SP**: Remove callee's frame
3. **Restore caller's segment pointers**: LCL, ARG, THIS, THAT
4. **Transfer control**: Jump to saved return address

**Pseudo-code**:
```python
# return

# Frame pointer (where LCL points)
FRAME = LCL

# Get return address from frame
RET = *(FRAME - 5)

# Pop return value to ARG[0] (caller's stack top after removing args)
*ARG = pop()

# Restore caller's SP
SP = ARG + 1

# Restore caller's segment pointers
THAT = *(FRAME - 1)
THIS = *(FRAME - 2)
ARG = *(FRAME - 3)
LCL = *(FRAME - 4)

# Jump to return address
goto RET
```

🎓 **Critical detail**: The return value must be placed at `ARG[0]` (where the first argument was), not at the current stack top. This ensures the caller sees the return value at the correct position after the arguments are removed!

### Bootstrap Code and Sys.init

**Problem**: When the VM starts, who calls the first function?

**Solution**: Bootstrap code that:
1. Initializes SP to 256 (stack base)
2. Calls `Sys.init` (the system initialization function)
3. `Sys.init` then calls `Main.main` (user's entry point)

**Bootstrap sequence**:
```assembly
// Bootstrap code (generated by VM translator)
@256
D=A
@SP
M=D           // SP = 256

// Call Sys.init (which will call Main.main)
call Sys.init 0
```

**Why Sys.init?**
- Provides system-level initialization (if needed)
- Ensures consistent entry point across all programs
- Enables OS-level setup before user code runs (Projects 11-12)

**Example program structure**:
```vm
// Sys.vm (system code)
function Sys.init 0
    call Main.main 0
    pop temp 0       // Discard Main.main return value
label SYS_HALT
    goto SYS_HALT    // Infinite loop (halt)

// Main.vm (user code)
function Main.main 0
    // ... user program ...
    push constant 0
    return
```

### VM-to-Assembly Translation Strategy

**New translations needed**:

**1. Label command**:
```vm
label LOOP_START
```

**Assembly**:
```assembly
// label LOOP_START
(functionName$LOOP_START)    // Scoped to current function
```

**Why scope labels?** Different functions might use the same label name (`LOOP`). Prefixing with function name prevents collisions.

**2. Goto command**:
```vm
goto LOOP_START
```

**Assembly**:
```assembly
// goto LOOP_START
@functionName$LOOP_START
0;JMP
```

**3. If-goto command**:
```vm
if-goto LOOP_START
```

**Assembly**:
```assembly
// if-goto LOOP_START
@SP
M=M-1         // SP--
A=M           // A = SP
D=M           // D = popped value
@functionName$LOOP_START
D;JNE         // Jump if D ≠ 0 (non-zero = true)
```

**4. Function declaration**:
```vm
function multiply 2
```

**Assembly**:
```assembly
// function multiply 2
(multiply)         // Entry point label
// Initialize local 0 = 0
@SP
A=M
M=0
@SP
M=M+1
// Initialize local 1 = 0
@SP
A=M
M=0
@SP
M=M+1
// (Pattern: push constant 0 for each local variable)
```

**5. Function call**:
```vm
call multiply 2
```

**Assembly** (complex!):
```assembly
// call multiply 2
// Push return address
@multiply$ret.1       // Unique return label
D=A
@SP
A=M
M=D
@SP
M=M+1

// Push LCL
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1

// Push ARG
@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1

// Push THIS
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1

// Push THAT
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1

// ARG = SP - nArgs - 5
@SP
D=M
@7            // 7 = nArgs (2) + 5
D=D-A
@ARG
M=D

// LCL = SP
@SP
D=M
@LCL
M=D

// goto multiply
@multiply
0;JMP

// Return address label
(multiply$ret.1)
```

**6. Function return**:
```vm
return
```

**Assembly** (also complex!):
```assembly
// return
// FRAME = LCL (use R13 as temp)
@LCL
D=M
@R13
M=D           // R13 = FRAME

// RET = *(FRAME - 5) (use R14 as temp)
@5
A=D-A         // A = FRAME - 5
D=M           // D = *(FRAME - 5) = return address
@R14
M=D           // R14 = RET

// *ARG = pop() (return value goes to caller's stack top)
@SP
M=M-1
A=M
D=M           // D = popped return value
@ARG
A=M
M=D           // *ARG = return value

// SP = ARG + 1 (restore caller's SP)
@ARG
D=M+1
@SP
M=D

// THAT = *(FRAME - 1)
@R13
D=M
@1
A=D-A
D=M
@THAT
M=D

// THIS = *(FRAME - 2)
@R13
D=M
@2
A=D-A
D=M
@THIS
M=D

// ARG = *(FRAME - 3)
@R13
D=M
@3
A=D-A
D=M
@ARG
M=D

// LCL = *(FRAME - 4)
@R13
D=M
@4
A=D-A
D=M
@LCL
M=D

// goto RET
@R14
A=M
0;JMP
```

🎓 **Key insight**: Function calls generate ~30-40 assembly instructions! This overhead is why real VMs use **native calling conventions** and **JIT compilation** to optimize hot paths.

## Learning Path

### Step 1: Implement Program Flow Commands (2-3 hours)

Add label, goto, and if-goto support to your VM translator.

**Update Parser** (add to `parser.py`):

```python
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

    # NEW: Program flow commands
    elif cmd_type == 'label':
        return {'type': 'label', 'label': parts[1]}

    elif cmd_type == 'goto':
        return {'type': 'goto', 'label': parts[1]}

    elif cmd_type == 'if-goto':
        return {'type': 'if-goto', 'label': parts[1]}

    else:
        raise ValueError(f"Unknown command: {cmd_type}")
```

**Update CodeGenerator** (add to `code_generator.py`):

```python
class CodeGenerator:
    def __init__(self, filename=None):
        self.label_counter = 0
        self.current_file = filename.replace('.vm', '').split('/')[-1] if filename else "default"
        self.current_function = ""  # Track current function for label scoping

    def generate(self, command):
        """Generate assembly for one VM command"""
        if command['type'] == 'arithmetic':
            return self.generate_arithmetic(command['operation'])
        elif command['type'] == 'push':
            return self.generate_push(command['segment'], command['index'])
        elif command['type'] == 'pop':
            return self.generate_pop(command['segment'], command['index'])
        # NEW: Program flow
        elif command['type'] == 'label':
            return self.generate_label(command['label'])
        elif command['type'] == 'goto':
            return self.generate_goto(command['label'])
        elif command['type'] == 'if-goto':
            return self.generate_if_goto(command['label'])

    def generate_label(self, label):
        """Generate assembly for label command"""
        # Labels are scoped to current function to prevent collisions
        scoped_label = f"{self.current_function}${label}"
        return f"// label {label}\n({scoped_label})\n"

    def generate_goto(self, label):
        """Generate assembly for goto command"""
        scoped_label = f"{self.current_function}${label}"
        return (
            f"// goto {label}\n"
            f"@{scoped_label}\n"
            "0;JMP\n"
        )

    def generate_if_goto(self, label):
        """Generate assembly for if-goto command"""
        scoped_label = f"{self.current_function}${label}"
        return (
            f"// if-goto {label}\n"
            "@SP\n"
            "M=M-1\n"      # SP--
            "A=M\n"        # A = SP
            "D=M\n"        # D = popped value
            f"@{scoped_label}\n"
            "D;JNE\n"      # Jump if D ≠ 0
        )
```

**Testing program flow**:

Create `examples/simple_loop.vm`:
```vm
// Count from 0 to 5
push constant 0
pop local 0        // local[0] = 0 (counter)

label LOOP_START
    push local 0
    push constant 5
    eq
    if-goto LOOP_END

    push local 0
    push constant 1
    add
    pop local 0    // counter++

    goto LOOP_START

label LOOP_END
    push local 0   // Final value (5) on stack
```

**Run test**:
```python
# test_program_flow.py
def test_simple_loop(self):
    """Test: Loop from 0 to 5"""
    init_segs = {'LCL': 300}  # Initialize LCL pointer
    cpu = self.run_vm_program('examples/simple_loop.vm',
                               max_cycles=20000,
                               init_segments=init_segs)
    stack = self.get_stack_contents(cpu)
    self.assertEqual(stack[-1], 5)
```

### Step 2: Implement Function Declaration (2-3 hours)

Add `function` command support.

**Update Parser**:
```python
elif cmd_type == 'function':
    return {'type': 'function', 'name': parts[1], 'nLocals': int(parts[2])}
```

**Update CodeGenerator**:
```python
def generate(self, command):
    # ... existing cases ...
    elif command['type'] == 'function':
        return self.generate_function(command['name'], command['nLocals'])

def generate_function(self, name, n_locals):
    """Generate assembly for function declaration"""
    # Update current function context for label scoping
    self.current_function = name

    asm = f"// function {name} {n_locals}\n"
    asm += f"({name})\n"  # Entry point label

    # Initialize all local variables to 0
    for i in range(n_locals):
        asm += (
            "// Initialize local variable to 0\n"
            "@SP\n"
            "A=M\n"
            "M=0\n"
            "@SP\n"
            "M=M+1\n"
        )

    return asm
```

**Testing function declaration**:

Create `examples/simple_function.vm`:
```vm
// Function with 2 local variables
function test 2
    push constant 42
    pop local 0
    push constant 99
    pop local 1
    push local 0
    push local 1
    add
    return         // (Not implemented yet, will add in next step)
```

### Step 3: Implement Function Call (4-5 hours)

Add `call` command support. This is the most complex translation!

**Update Parser**:
```python
elif cmd_type == 'call':
    return {'type': 'call', 'name': parts[1], 'nArgs': int(parts[2])}
```

**Update CodeGenerator**:
```python
def __init__(self, filename=None):
    self.label_counter = 0
    self.return_counter = 0  # NEW: For unique return addresses
    self.current_file = filename.replace('.vm', '').split('/')[-1] if filename else "default"
    self.current_function = ""

def generate(self, command):
    # ... existing cases ...
    elif command['type'] == 'call':
        return self.generate_call(command['name'], command['nArgs'])

def generate_call(self, function_name, n_args):
    """Generate assembly for function call"""
    # Generate unique return address label
    return_label = f"{function_name}$ret.{self.return_counter}"
    self.return_counter += 1

    asm = f"// call {function_name} {n_args}\n"

    # Push return address
    asm += (
        f"@{return_label}\n"
        "D=A\n"
        "@SP\n"
        "A=M\n"
        "M=D\n"
        "@SP\n"
        "M=M+1\n"
    )

    # Push LCL
    asm += (
        "@LCL\n"
        "D=M\n"
        "@SP\n"
        "A=M\n"
        "M=D\n"
        "@SP\n"
        "M=M+1\n"
    )

    # Push ARG
    asm += (
        "@ARG\n"
        "D=M\n"
        "@SP\n"
        "A=M\n"
        "M=D\n"
        "@SP\n"
        "M=M+1\n"
    )

    # Push THIS
    asm += (
        "@THIS\n"
        "D=M\n"
        "@SP\n"
        "A=M\n"
        "M=D\n"
        "@SP\n"
        "M=M+1\n"
    )

    # Push THAT
    asm += (
        "@THAT\n"
        "D=M\n"
        "@SP\n"
        "A=M\n"
        "M=D\n"
        "@SP\n"
        "M=M+1\n"
    )

    # ARG = SP - nArgs - 5
    asm += (
        "@SP\n"
        "D=M\n"
        f"@{n_args + 5}\n"
        "D=D-A\n"
        "@ARG\n"
        "M=D\n"
    )

    # LCL = SP
    asm += (
        "@SP\n"
        "D=M\n"
        "@LCL\n"
        "M=D\n"
    )

    # goto function_name
    asm += (
        f"@{function_name}\n"
        "0;JMP\n"
    )

    # Return address label
    asm += f"({return_label})\n"

    return asm
```

🎓 **Key insight**: The `call` command pushes 5 values before the function executes: return address + 4 segment pointers (LCL, ARG, THIS, THAT). This is why `ARG = SP - nArgs - 5` works—it points to the first argument, skipping over these 5 saved values.

### Step 4: Implement Function Return (3-4 hours)

Add `return` command support. This must carefully restore caller state.

**Update Parser**:
```python
elif cmd_type == 'return':
    return {'type': 'return'}
```

**Update CodeGenerator**:
```python
def generate(self, command):
    # ... existing cases ...
    elif command['type'] == 'return':
        return self.generate_return()

def generate_return(self):
    """Generate assembly for function return"""
    asm = "// return\n"

    # FRAME = LCL (save in R13)
    asm += (
        "@LCL\n"
        "D=M\n"
        "@R13\n"
        "M=D          // R13 = FRAME\n"
    )

    # RET = *(FRAME - 5) (save return address in R14)
    asm += (
        "@5\n"
        "A=D-A        // A = FRAME - 5\n"
        "D=M          // D = *(FRAME - 5)\n"
        "@R14\n"
        "M=D          // R14 = RET (return address)\n"
    )

    # *ARG = pop() (put return value at top of caller's stack)
    asm += (
        "@SP\n"
        "M=M-1\n"
        "A=M\n"
        "D=M          // D = return value\n"
        "@ARG\n"
        "A=M\n"
        "M=D          // *ARG = return value\n"
    )

    # SP = ARG + 1 (restore caller's SP)
    asm += (
        "@ARG\n"
        "D=M+1\n"
        "@SP\n"
        "M=D\n"
    )

    # THAT = *(FRAME - 1)
    asm += (
        "@R13\n"
        "D=M\n"
        "@1\n"
        "A=D-A\n"
        "D=M\n"
        "@THAT\n"
        "M=D\n"
    )

    # THIS = *(FRAME - 2)
    asm += (
        "@R13\n"
        "D=M\n"
        "@2\n"
        "A=D-A\n"
        "D=M\n"
        "@THIS\n"
        "M=D\n"
    )

    # ARG = *(FRAME - 3)
    asm += (
        "@R13\n"
        "D=M\n"
        "@3\n"
        "A=D-A\n"
        "D=M\n"
        "@ARG\n"
        "M=D\n"
    )

    # LCL = *(FRAME - 4)
    asm += (
        "@R13\n"
        "D=M\n"
        "@4\n"
        "A=D-A\n"
        "D=M\n"
        "@LCL\n"
        "M=D\n"
    )

    # goto RET
    asm += (
        "@R14\n"
        "A=M\n"
        "0;JMP\n"
    )

    return asm
```

**Testing call/return**:

Create `examples/simple_call.vm`:
```vm
// Main function
function main 1
    push constant 7
    push constant 3
    call add 2      // add(7, 3)
    pop local 0     // local[0] = result (10)
    push local 0
    return

// Add function
function add 0
    push argument 0
    push argument 1
    add
    return
```

### Step 5: Implement Bootstrap Code (1-2 hours)

The bootstrap code initializes the VM and calls `Sys.init`.

**Update CodeGenerator.init()**:

```python
def init(self):
    """Bootstrap code: initialize VM and call Sys.init"""
    asm = (
        "// ===== Bootstrap: Initialize VM State =====\n"
        "@256\n"
        "D=A\n"
        "@SP\n"
        "M=D           // SP = 256\n"
        "\n"
    )

    # Call Sys.init
    # Use a special case since there's no caller to save
    asm += (
        "// Call Sys.init\n"
        "@Sys.init$ret.bootstrap\n"
        "D=A\n"
        "@SP\n"
        "A=M\n"
        "M=D\n"
        "@SP\n"
        "M=M+1\n"

        # Push dummy values for LCL, ARG, THIS, THAT
        # (Sys.init has no caller, but we maintain convention)
        "@SP\n"
        "A=M\n"
        "M=0\n"
        "@SP\n"
        "M=M+1\n"

        "@SP\n"
        "A=M\n"
        "M=0\n"
        "@SP\n"
        "M=M+1\n"

        "@SP\n"
        "A=M\n"
        "M=0\n"
        "@SP\n"
        "M=M+1\n"

        "@SP\n"
        "A=M\n"
        "M=0\n"
        "@SP\n"
        "M=M+1\n"

        # ARG = SP - 5 (0 arguments)
        "@SP\n"
        "D=M\n"
        "@5\n"
        "D=D-A\n"
        "@ARG\n"
        "M=D\n"

        # LCL = SP
        "@SP\n"
        "D=M\n"
        "@LCL\n"
        "M=D\n"

        # goto Sys.init
        "@Sys.init\n"
        "0;JMP\n"

        "(Sys.init$ret.bootstrap)\n"
    )

    return asm
```

**Create Sys.vm**:
```vm
// System initialization
function Sys.init 0
    call Main.main 0
    pop temp 0         // Discard return value
label SYS_HALT
    goto SYS_HALT      // Infinite loop (program halt)
```

### Step 6: Handle Multiple Files (2-3 hours)

Real programs consist of multiple `.vm` files. Update your translator to handle directories.

**Update VMTranslator**:

```python
import os
import glob

class VMTranslator:
    """Main VM-to-Assembly translator"""

    def __init__(self, input_path):
        self.input_path = input_path

        # Determine if input is file or directory
        if os.path.isfile(input_path):
            # Single file
            self.vm_files = [input_path]
            self.output_file = input_path.replace('.vm', '.asm')
        elif os.path.isdir(input_path):
            # Directory: find all .vm files
            self.vm_files = glob.glob(os.path.join(input_path, '*.vm'))
            # Output file named after directory
            dir_name = os.path.basename(input_path.rstrip('/'))
            self.output_file = os.path.join(input_path, f"{dir_name}.asm")
        else:
            raise ValueError(f"Invalid input path: {input_path}")

        self.code_gen = CodeGenerator()

    def translate(self):
        """Translate all VM files to single assembly file"""
        with open(self.output_file, 'w') as out:
            # Write bootstrap code (only once for entire program)
            out.write(self.code_gen.init())

            # Translate each VM file
            for vm_file in self.vm_files:
                # Extract filename for static scoping
                filename = os.path.basename(vm_file)
                self.code_gen.current_file = filename.replace('.vm', '')

                # Parse and translate file
                parser = Parser(vm_file)
                while parser.has_more_commands():
                    parser.advance()
                    if parser.current_command:
                        asm = self.code_gen.generate(parser.current_command)
                        out.write(asm)
```

**Update main()**:
```python
def main():
    """Command-line interface for VM translator"""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python vm_translator.py <file.vm|directory>")
        sys.exit(1)

    input_path = sys.argv[1]

    print(f"Translating {input_path}...")
    translator = VMTranslator(input_path)
    translator.translate()
    print(f"Generated {translator.output_file}")
```

**Usage**:
```bash
# Single file
python vm_translator.py examples/simple_call.vm

# Entire directory
python vm_translator.py examples/FibonacciSeries/
# Generates examples/FibonacciSeries/FibonacciSeries.asm
```

### Step 7: Test with Complex Programs (3-4 hours)

Test your translator with recursive programs and multi-file projects.

**Fibonacci Series** (iterative, tests loops + functions):

Create `examples/FibonacciSeries/Main.vm`:
```vm
// Compute first 10 Fibonacci numbers
function Main.main 0
    push constant 10
    call Main.fibonacci 1
    pop temp 0
    push constant 0
    return

// Compute Fibonacci series iteratively
function Main.fibonacci 4
    // local 0 = n (counter)
    // local 1 = a (previous)
    // local 2 = b (current)
    // local 3 = temp

    push argument 0
    pop local 0

    push constant 0
    pop local 1       // a = 0

    push constant 1
    pop local 2       // b = 1

label FIB_LOOP
    push local 0
    push constant 0
    eq
    if-goto FIB_END

    // Print current Fibonacci number (b)
    push local 2
    call Output.printInt 1
    pop temp 0

    // temp = a + b
    push local 1
    push local 2
    add
    pop local 3

    // a = b
    push local 2
    pop local 1

    // b = temp
    push local 3
    pop local 2

    // n--
    push local 0
    push constant 1
    sub
    pop local 0

    goto FIB_LOOP

label FIB_END
    push constant 0
    return
```

Create `examples/FibonacciSeries/Sys.vm`:
```vm
function Sys.init 0
    call Main.main 0
    pop temp 0
label SYS_HALT
    goto SYS_HALT
```

**Factorial** (recursive, tests call stack depth):

Create `examples/Factorial/Main.vm`:
```vm
// Compute factorial(5) = 120
function Main.main 1
    push constant 5
    call Main.factorial 1
    pop local 0       // local[0] = 120
    push local 0
    return

// Recursive factorial
function Main.factorial 0
    push argument 0
    push constant 2
    lt
    if-goto FACT_BASE_CASE

    // Recursive case: n * factorial(n-1)
    push argument 0
    push argument 0
    push constant 1
    sub
    call Main.factorial 1
    call Math.multiply 2
    return

label FACT_BASE_CASE
    // Base case: factorial(0) = factorial(1) = 1
    push constant 1
    return
```

Create `examples/Factorial/Math.vm`:
```vm
// Multiply using repeated addition
function Math.multiply 2
    push constant 0
    pop local 0       // accumulator = 0
    push argument 1
    pop local 1       // counter = b

label MULT_LOOP
    push local 1
    push constant 0
    eq
    if-goto MULT_END

    push local 0
    push argument 0
    add
    pop local 0       // accumulator += a

    push local 1
    push constant 1
    sub
    pop local 1       // counter--

    goto MULT_LOOP

label MULT_END
    push local 0
    return
```

Create `examples/Factorial/Sys.vm`:
```vm
function Sys.init 0
    call Main.main 0
    pop temp 0
label SYS_HALT
    goto SYS_HALT
```

**Run test**:
```bash
python vm_translator.py examples/Factorial/
# Generates examples/Factorial/Factorial.asm
```

**Verify in CPU simulator**:
```python
def test_factorial(self):
    """Test: factorial(5) = 120"""
    # Translate entire directory
    translator = VMTranslator('examples/Factorial/')
    translator.translate()

    # Assemble
    self.asm.assemble('examples/Factorial/Factorial.asm',
                      'examples/Factorial/Factorial.hack')

    # Load and run
    with open('examples/Factorial/Factorial.hack', 'r') as f:
        binary = [line.strip() for line in f]

    self.cpu.reset()
    self.cpu.load_program(binary)
    self.cpu.run(max_cycles=100000)  # Recursion needs more cycles

    # Check result in Main's local 0 (stored on stack during execution)
    # Final result should be 120
    # (Exact location depends on stack state at halt)
```

### Step 8: Debugging and Optimization (2-3 hours)

**Common bugs**:

1. **Return address label collision**: Not incrementing return counter
2. **Label scoping wrong**: Forgetting to prefix with function name
3. **ARG pointer calculation**: Off-by-one in `SP - nArgs - 5`
4. **Frame restoration order**: Must restore THAT, THIS, ARG, LCL in correct sequence
5. **Recursive stack overflow**: Not enough cycles in test, or infinite recursion

**Debugging strategies**:

**1. Add verbose mode**:
```python
class CodeGenerator:
    def __init__(self, filename=None, verbose=False):
        self.verbose = verbose
        # ... existing init ...

    def generate_call(self, function_name, n_args):
        asm = f"// call {function_name} {n_args}\n"

        if self.verbose:
            asm += (
                "// DEBUG: About to call function\n"
                "// SP before call: (check RAM[0])\n"
            )

        # ... rest of implementation ...
```

**2. Trace stack frames**:
```python
# Add to tests
def trace_stack_frame(self, cpu):
    """Print current stack frame for debugging"""
    sp = cpu.ram[0]
    lcl = cpu.ram[1]
    arg = cpu.ram[2]
    this_ptr = cpu.ram[3]
    that_ptr = cpu.ram[4]

    print(f"SP:   {sp}")
    print(f"LCL:  {lcl}")
    print(f"ARG:  {arg}")
    print(f"THIS: {this_ptr}")
    print(f"THAT: {that_ptr}")
    print(f"Stack: {self.get_stack_contents(cpu)}")
```

**3. Visual stack inspection**:
```python
def visualize_stack(self, cpu, start=256, end=None):
    """Print stack contents with segment markers"""
    sp = cpu.ram[0]
    lcl = cpu.ram[1]
    arg = cpu.ram[2]

    if end is None:
        end = sp

    for addr in range(start, end):
        marker = ""
        if addr == sp:
            marker += " ← SP"
        if addr == lcl:
            marker += " ← LCL"
        if addr == arg:
            marker += " ← ARG"

        value = cpu.ram[addr]
        print(f"RAM[{addr}] = {value}{marker}")
```

**Performance notes**:

Your implementation prioritizes correctness. Function call overhead:
- ~35 instructions per `call`
- ~30 instructions per `return`
- Total: ~65 instructions per function call

Real VMs optimize this:
- **Inlining**: Replace small function calls with body
- **Register windows**: SPARC architecture keeps arguments in registers
- **Native calling conventions**: Use hardware call/ret instructions
- **JIT compilation**: Compile hot functions to native code

## Deep Dive: Implementation Insights

### Stack Frame Layout in Detail

Understanding the exact stack frame structure is critical for implementing `call` and `return`.

**Before function call** (caller has pushed arguments):
```
RAM[256]: (caller's stack)
...
RAM[SP-2]: arg 0          ← First argument
RAM[SP-1]: arg 1          ← Second argument (for 2-arg function)
RAM[SP]:   (next free)    ← SP points here
```

**After `call functionName 2`** (function about to execute):
```
RAM[256]: (caller's stack)
...
RAM[SP-7]: arg 0          ← ARG points here
RAM[SP-6]: arg 1
RAM[SP-5]: return address
RAM[SP-4]: saved LCL
RAM[SP-3]: saved ARG
RAM[SP-2]: saved THIS
RAM[SP-1]: saved THAT
RAM[SP]:   (local 0 will be here)  ← LCL points here, SP points here
```

**After `function functionName 3`** (function initialized):
```
RAM[256]: (caller's stack)
...
RAM[SP-7]: arg 0          ← ARG points here
RAM[SP-6]: arg 1
RAM[SP-5]: return address
RAM[SP-4]: saved LCL
RAM[SP-3]: saved ARG
RAM[SP-2]: saved THIS
RAM[SP-1]: saved THAT
RAM[SP]:   local 0        ← LCL points here
RAM[SP+1]: local 1
RAM[SP+2]: local 2
RAM[SP+3]: (working stack) ← SP points here
```

**During function execution**:
- `push argument 0` accesses RAM[ARG + 0]
- `push local 1` accesses RAM[LCL + 1]
- Working stack grows from RAM[SP]

**Before `return`** (function has pushed return value):
```
RAM[256]: (caller's stack)
...
RAM[SP-7]: arg 0          ← ARG points here
RAM[SP-6]: arg 1
RAM[SP-5]: return address
RAM[SP-4]: saved LCL
RAM[SP-3]: saved ARG
RAM[SP-2]: saved THIS
RAM[SP-1]: saved THAT
RAM[SP]:   local 0        ← LCL points here
RAM[SP+1]: local 1
RAM[SP+2]: local 2
...
RAM[SP+N]: return value   ← SP points after this
```

**After `return`** (caller resumes):
```
RAM[256]: (caller's stack)
...
RAM[SP-1]: return value   ← Placed at ARG[0], SP = ARG + 1
```

🎓 **Critical insight**: The return value MUST be placed at `ARG[0]` (where the first argument was), not at the current stack top. This is because the caller expects the arguments to be gone and the return value to be at the top of *its* stack.

### Why ARG = SP - nArgs - 5?

This calculation positions ARG to point at the first argument:

```
Stack before call (caller pushed 2 arguments):
...
arg 0
arg 1
← SP

After pushing 5 values (return, LCL, ARG, THIS, THAT):
...
arg 0          ← We want ARG to point here
arg 1
return addr
saved LCL
saved ARG
saved THIS
saved THAT
← SP (SP has moved forward 5 positions)

Calculation:
ARG = SP - 5 - nArgs
ARG = SP - 5 - 2
ARG = SP - 7

Counting back from SP:
SP - 1: saved THAT
SP - 2: saved THIS
SP - 3: saved ARG
SP - 4: saved LCL
SP - 5: return addr
SP - 6: arg 1
SP - 7: arg 0  ✓ This is where ARG should point!
```

### Return Implementation: Why This Order?

The `return` implementation must restore state in a specific order:

**Step 1**: Save FRAME and RET first
```assembly
@LCL
D=M
@R13
M=D           // R13 = FRAME (LCL value before we change it)

@5
A=D-A
D=M
@R14
M=D           // R14 = RET (return address)
```

**Why?** We're about to overwrite LCL when restoring caller state, so we must save it now.

**Step 2**: Move return value to caller's stack top
```assembly
@SP
M=M-1
A=M
D=M           // D = return value (popped from stack)
@ARG
A=M
M=D           // *ARG = return value
```

**Why this location?** The caller pushed arguments onto the stack, then called the function. The caller expects arguments to be gone and the return value to be where the first argument was.

**Step 3**: Restore caller's SP
```assembly
@ARG
D=M+1
@SP
M=D           // SP = ARG + 1 (just after return value)
```

**Step 4**: Restore segment pointers in reverse order
```assembly
// THAT = *(FRAME - 1)
// THIS = *(FRAME - 2)
// ARG = *(FRAME - 3)
// LCL = *(FRAME - 4)
```

**Why reverse order?** Doesn't actually matter—we saved FRAME in R13, so we can restore in any order. Convention matches the push order (makes debugging easier).

**Step 5**: Jump to return address
```assembly
@R14
A=M
0;JMP
```

### Label Scoping Strategy

**Problem**: Different functions might use the same label names:
```vm
function foo 0
label LOOP
    goto LOOP

function bar 0
label LOOP      // Collision!
    goto LOOP
```

**Solution**: Prefix labels with function name:
```assembly
(foo)
(foo$LOOP)      // Scoped label
@foo$LOOP
0;JMP

(bar)
(bar$LOOP)      // Different label
@bar$LOOP
0;JMP
```

**Implementation**:
```python
def generate_label(self, label):
    scoped_label = f"{self.current_function}${label}"
    return f"({scoped_label})\n"

def generate_goto(self, label):
    scoped_label = f"{self.current_function}${label}"
    return f"@{scoped_label}\n0;JMP\n"
```

**When to update `self.current_function`?**
- At the start of `generate_function()`, before emitting the function label
- This ensures all labels within the function are correctly scoped

### Bootstrap vs. Regular Calls

**Regular function call**:
- Caller has already pushed arguments
- Caller's segment pointers (LCL, ARG, THIS, THAT) are meaningful
- Return address points to next instruction after call

**Bootstrap call to Sys.init**:
- No caller exists (VM startup)
- No arguments (Sys.init takes 0 arguments)
- Segment pointers don't exist yet (we push dummy zeros)
- Return address is a special label (bootstrap never returns)

**Why push dummy values in bootstrap?**
- Maintains stack frame structure consistency
- `return` implementation expects segment pointers at fixed offsets
- If Sys.init calls other functions, those functions will save real values

## What You Should Understand After This Project

- ✅ **Program flow**: Labels, goto, and conditional jumps enable loops and branching
- ✅ **Stack frames**: Each function call creates an activation record with saved state
- ✅ **Calling conventions**: Standardized way to pass arguments and return values
- ✅ **Recursion**: Stack frames enable functions to call themselves safely
- ✅ **Bootstrap sequence**: System initialization before user code runs
- ✅ **Multi-file translation**: Combining multiple VM files into one assembly program
- ✅ **Label scoping**: Function-prefixed labels prevent naming collisions
- ✅ **Return value placement**: Return values replace arguments on caller's stack

## Common Pitfalls

**1. ARG pointer off-by-one**
```python
# WRONG:
ARG = SP - nArgs - 4    # Missing the saved segment pointers!

# RIGHT:
ARG = SP - nArgs - 5    # 5 = return address + 4 segment pointers
```

**2. Return value placement**
```python
# WRONG (leaves return value on current stack):
@SP
M=M-1
A=M
D=M
@SP
A=M
M=D    # Writes to wrong location!

# RIGHT (places return value at caller's stack top):
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D    # Writes to ARG[0]
```

**3. Forgetting to save FRAME before modifying LCL**
```python
# WRONG:
# Restore LCL first
@LCL
D=M
@4
A=D-A
D=M
@LCL
M=D    # Now LCL has changed, can't access FRAME-1, FRAME-2, etc.!

# RIGHT:
# Save FRAME in R13 first
@LCL
D=M
@R13
M=D    # R13 = FRAME
# Now safe to modify LCL
```

**4. Label scoping**
```python
# WRONG (global labels collide):
def generate_label(self, label):
    return f"({label})\n"    # foo$LOOP and bar$LOOP both become (LOOP)

# RIGHT (function-scoped labels):
def generate_label(self, label):
    scoped_label = f"{self.current_function}${label}"
    return f"({scoped_label})\n"    # (foo$LOOP) and (bar$LOOP)
```

**5. Return address label reuse**
```python
# WRONG (same label for all calls to foo):
return_label = f"{function_name}$ret"    # All calls to foo use foo$ret!

# RIGHT (unique label per call site):
return_label = f"{function_name}$ret.{self.return_counter}"
self.return_counter += 1
```

**6. If-goto condition logic**
```python
# WRONG (jumps if zero):
D=M
@label
D;JEQ    # Jumps when false!

# RIGHT (jumps if non-zero):
D=M
@label
D;JNE    # Jumps when true (any non-zero value)
```

## Extension Ideas

**Level 1: Enhance Translation**
- Add tail call optimization (convert tail recursion to loop)
- Implement function inlining for small functions
- Generate assembly comments showing VM stack state
- Add call graph visualization (which functions call which)

**Level 2: Advanced Features**
- Add exception handling (try/catch/throw VM commands)
- Implement coroutines (yield/resume for generators)
- Add multi-threading primitives (spawn, join, mutex)
- Support variable-argument functions (varargs)

**Level 3: Optimization**
- Register allocation (keep stack top in D register)
- Dead code elimination (remove unreachable functions)
- Constant propagation (replace `push constant 5; pop local 0` sequences)
- Loop unrolling (expand small loops for speed)

**Level 4: Debugging Tools**
- VM debugger with breakpoints and single-stepping
- Profiler showing function call counts and time spent
- Stack frame visualizer (graphical display)
- Call stack tracer (show active function calls)

**Level 5: Real-World Features**
- Just-In-Time (JIT) compilation for hot functions
- Garbage collection support (mark/sweep/compact)
- Foreign function interface (call C libraries)
- Compile to other targets (x86, ARM, LLVM IR)

## Real-World Connection

**Your VM calling convention is similar to**:

**System V ABI (x86-64 Linux)**:
- Arguments passed via registers + stack ✓
- Return address saved on stack ✓
- Callee saves registers (like LCL, ARG, THIS, THAT) ✓
- Difference: System V uses 6 registers for arguments before stack

**ARM Procedure Call Standard (AAPCS)**:
- First 4 arguments in registers r0-r3 ✓
- Return address in link register (LR) ✓
- Stack frames for local variables ✓
- Difference: ARM uses register windows, no stack for first 4 args

**JavaScript V8 Engine**:
- Stack-based VM like yours ✓
- Function frames with saved state ✓
- Optimizing JIT compiler for hot functions ✓
- Difference: V8 uses hidden classes, inline caching, complex GC

**JVM (Java Virtual Machine)**:
- Stack frames for method calls ✓
- Arguments and locals in frame ✓
- Return value on operand stack ✓
- Difference: JVM has objects, exceptions, garbage collection

**Why calling conventions matter**:
1. **Interoperability**: Code compiled by different compilers must agree on ABI
2. **Debugging**: Debuggers rely on standard frame layouts
3. **Optimization**: Compiler can optimize knowing calling convention
4. **Security**: Stack canaries and DEP depend on consistent stack structure

## Success Criteria

You've mastered this project when you can:

1. **Explain stack frames**: Describe what gets saved during `call` and why
2. **Trace function calls**: Follow execution through recursive calls manually
3. **Debug translation**: Identify bugs in generated assembly for `call`/`return`
4. **Design new VM commands**: Add features by defining VM semantics + translation
5. **Understand recursion**: Explain why factorial(5) → factorial(4) → factorial(3) works
6. **Optimize generated code**: Identify opportunities to reduce instruction count

## Next Steps

**Project 9-10: High-Level Language (Jack)**

With a complete VM, you'll design and implement a high-level language:
- **Syntax**: Classes, methods, fields, expressions, statements
- **Lexer**: Tokenize source code (keywords, symbols, identifiers)
- **Parser**: Build abstract syntax tree from tokens
- **Semantic analysis**: Type checking, symbol tables, scope resolution
- **Code generation**: Compile Jack to VM commands

**Example Jack program**:
```jack
class Main {
    function void main() {
        var int sum, i;
        let sum = 0;
        let i = 1;
        while (i < 11) {
            let sum = sum + i;
            let i = i + 1;
        }
        do Output.printInt(sum);  // Prints 55
        return;
    }
}
```

**This compiles to VM code** (which your translator converts to assembly):
```vm
function Main.main 2
    push constant 0
    pop local 0       // sum = 0
    push constant 1
    pop local 1       // i = 1
label WHILE_EXP0
    push local 1
    push constant 11
    lt
    not
    if-goto WHILE_END0
    push local 0
    push local 1
    add
    pop local 0       // sum = sum + i
    push local 1
    push constant 1
    add
    pop local 1       // i = i + 1
    goto WHILE_EXP0
label WHILE_END0
    push local 0
    call Output.printInt 1
    pop temp 0
    push constant 0
    return
```

**Project 11-12: Operating System**

With a compiler, you'll build a minimal OS in Jack:
- **Math**: Multiply, divide, square root
- **String**: String manipulation and comparison
- **Array**: Dynamic arrays
- **Output**: Text output to screen
- **Screen**: Graphics (pixel, line, circle, rectangle)
- **Keyboard**: Input handling
- **Memory**: Heap allocation (malloc/free)
- **Sys**: System initialization, halt, error handling

---

**Congratulations!** You've completed the VM layer—the bridge between high-level languages and assembly. You can now express **any algorithm** with loops, conditionals, and recursion. The next step is building a language that compiles to this VM!

The journey from hardware to software is nearly complete. You've built:
- ✅ Logic gates from NAND
- ✅ ALU for arithmetic
- ✅ Memory hierarchy
- ✅ Complete computer architecture
- ✅ Assembler with symbol resolution
- ✅ Stack-based virtual machine with functions

**Next**: High-level language → Compiler → Operating System → Your own complete computer system from first principles! 🎉

---

## Summary: What You Built

**You have implemented a Turing-complete virtual machine translator** that:

1. **Parses** VM commands including program flow and function calls
2. **Generates** Hack assembly for labels, jumps, function declarations, calls, and returns
3. **Manages** stack frames with automatic state preservation
4. **Implements** calling conventions for argument passing and return values
5. **Handles** multi-file programs with proper symbol scoping
6. **Produces** working machine code for recursive and iterative algorithms

**Technical accomplishments**:
- ✅ Program flow with labels and conditional/unconditional jumps
- ✅ Function call frames with automatic LCL/ARG/THIS/THAT preservation
- ✅ Recursive function support through stack-based activation records
- ✅ Bootstrap sequence for system initialization
- ✅ Multi-file translation with file-scoped static variables
- ✅ Function-scoped label naming to prevent collisions

**Why this matters**:
You've built the **complete runtime environment** for high-level languages:
- Variables and expressions → stack operations (Project 7)
- Control flow → labels and jumps (Project 8)
- Functions → call/return with stack frames (Project 8)
- Objects and arrays → memory segments + heap allocation (Projects 11-12)

**The stack machine you built powers every modern language runtime:**
- Java bytecode → JVM
- Python → CPython interpreter
- JavaScript → V8 engine
- C# → CLR
- WebAssembly → WASM runtime

You've now built **every layer from NAND gates to a Turing-complete virtual machine**. The journey to high-level programming is complete! 🚀
