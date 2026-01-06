# Project 9: High-Level Language Design (Jack)

**Objective**: Design and write programs in an object-oriented language that compiles to VM code

## Background Concepts

### What You've Built So Far

**Phase 1: Hardware Layer (Projects 1-5)**
- ✅ Logic gates from NAND primitives
- ✅ ALU with 18+ operations
- ✅ Memory hierarchy (DFF → Register → RAM)
- ✅ Complete Von Neumann computer

**Phase 2: Software Layer (Projects 6-8)**
- ✅ **Assembler (Project 6)**: Symbolic assembly → Binary machine code
- ✅ **VM Translator Part 1 (Project 7)**: Stack arithmetic and memory segments
- ✅ **VM Translator Part 2 (Project 8)**: Program flow (labels/goto) and function calls

**What you can do now**:
Write VM programs with functions, recursion, and control flow:
```vm
function Main.fibonacci 2
    push argument 0
    push constant 2
    lt
    if-goto BASE_CASE

    // Recursive case: fib(n-1) + fib(n-2)
    push argument 0
    push constant 1
    sub
    call Main.fibonacci 1

    push argument 0
    push constant 2
    sub
    call Main.fibonacci 1

    add
    return

label BASE_CASE
    push argument 0
    return
```

**What you CANNOT do yet**:
Write in a high-level language with:
- Classes and object-oriented programming
- Variable declarations with meaningful names
- Expressions: `let x = (a + b) * c;`
- Control structures: `while (x > 0) { ... }`
- Method calls: `obj.doSomething(arg1, arg2);`

### The Problem: VM Code is Too Low-Level

Your VM is powerful and Turing-complete, but writing non-trivial programs is tedious:

**Problem 1: No variables with scope**
```vm
// What does this even do?
push local 0
push local 1
add
pop local 2

// Compare to high-level code:
// let c = a + b;
```

**Problem 2: No type system**
```vm
// Is this an integer? A boolean? A pointer to an object?
push local 0
// No way to tell from the code
```

**Problem 3: Complex expression evaluation requires manual stack manipulation**
```vm
// Evaluate: (a + b) * (c - d)
push local 0    // a
push local 1    // b
add             // a + b
push local 2    // c
push local 3    // d
sub             // c - d
call Math.multiply 2

// Compare to high-level: let result = (a + b) * (c - d);
```

**Problem 4: No object-oriented abstraction**
```vm
// How do you represent objects? Methods? Fields?
// How do you manage object construction and memory?
// No language-level support for OOP concepts
```

### The Solution: Jack - A High-Level Object-Oriented Language

Project 9 introduces **Jack**, a Java-like language that compiles to your VM code. Jack provides:

1. **Object-Oriented Programming**: Classes, methods, fields, constructors
2. **Static Typing**: int, boolean, char, class types, arrays
3. **Structured Control Flow**: if/else, while loops
4. **Expression Syntax**: Infix operators, method calls, array indexing
5. **Readable Syntax**: Human-friendly code that compiles to VM

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

This compiles to **28 lines of VM code**, which your VM translator converts to **~200 lines of assembly**.

🎓 **Key insight**: Each layer of abstraction hides complexity. High-level code (10 lines) → VM code (28 lines) → Assembly (~200 lines) → Machine code (~200 binary instructions). Abstraction is what makes programming scalable!

## Jack Language Specification

### Program Structure

**Every Jack program consists of one or more classes**:
- Each class is in its own `.jack` file
- Filename must match class name: `Main.jack` contains `class Main`
- Programs start by calling `Main.main()`

**Basic structure**:
```jack
class ClassName {
    // Class-level variables (fields)
    field int x, y;
    field boolean active;
    static int count;

    // Constructor
    constructor ClassName new(int ax, int ay) {
        let x = ax;
        let y = ay;
        let active = true;
        return this;
    }

    // Methods (operate on instance data)
    method int getX() {
        return x;
    }

    method void setX(int newX) {
        let x = newX;
        return;
    }

    // Functions (static methods, no instance)
    function int max(int a, int b) {
        if (a > b) {
            return a;
        } else {
            return b;
        }
    }
}
```

### Data Types

**Primitive types**:
- `int`: 16-bit signed integer (-32768 to 32767)
- `boolean`: `true` or `false`
- `char`: Single ASCII character

**Class types** (objects):
- `String`: Built-in string class
- `Array`: Built-in array class
- User-defined classes: `Point`, `Circle`, `Game`, etc.

**Type declaration**:
```jack
var int x, y, sum;              // Three integer variables
var boolean done;               // Boolean variable
var Point p;                    // Object reference (null until constructed)
var Array arr;                  // Array reference
```

🎓 **Key insight**: In Jack, class types are **references** (pointers). `var Point p;` declares a pointer that's initially null. You must construct the object: `let p = Point.new(10, 20);`

### Variables and Scope

**Four variable kinds**:

**1. Field variables** (instance variables):
```jack
class Circle {
    field int x, y;      // Center coordinates
    field int radius;    // Radius

    // Each Circle object has its own x, y, radius
}
```
- One copy per object instance
- Compiled to VM segment: `this`

**2. Static variables** (class variables):
```jack
class Math {
    static Array twoToThe;    // Shared by all instances

    function void init() {
        let twoToThe = Array.new(16);
        // Initialize powers of 2
        return;
    }
}
```
- One copy shared by all instances
- Compiled to VM segment: `static`

**3. Local variables** (method/function locals):
```jack
function int sum(int n) {
    var int result, i;    // Local to this function call
    let result = 0;
    let i = 1;

    while (i < (n + 1)) {
        let result = result + i;
        let i = i + 1;
    }

    return result;
}
```
- One copy per function activation (stack frame)
- Compiled to VM segment: `local`

**4. Parameter variables** (arguments):
```jack
method void setLocation(int ax, int ay) {
    // ax, ay are parameters
    let x = ax;
    let y = ay;
    return;
}
```
- Passed by caller
- Compiled to VM segment: `argument`
- For methods: `argument 0` is always `this` (implicit)

**Scope rules**:
- Field/static: Accessible throughout class
- Local/parameter: Accessible only within method/function
- Shadowing: Local variables can shadow field names (use `this.fieldName` to disambiguate)

### Expressions and Operators

**Arithmetic operators**:
```jack
let x = a + b;      // Addition
let y = a - b;      // Subtraction
let z = a * b;      // Multiplication (calls Math.multiply)
let w = a / b;      // Division (calls Math.divide)
```

**Comparison operators**:
```jack
let eq = (a = b);   // Equality
let gt = (a > b);   // Greater than
let lt = (a < b);   // Less than
```

**Logical operators**:
```jack
let result = (a & b);    // AND
let result = (a | b);    // OR
let result = ~a;         // NOT
```

**Operator precedence** (highest to lowest):
1. Unary: `~`, `-` (negation)
2. Multiplication/Division: `*`, `/`
3. Addition/Subtraction: `+`, `-`
4. Comparison: `<`, `>`, `=`
5. Logical AND: `&`
6. Logical OR: `|`

**Use parentheses for clarity**:
```jack
let result = (a + b) * (c - d);
let isValid = (x > 0) & (y > 0);
```

**Array access**:
```jack
let arr = Array.new(10);
let arr[0] = 100;
let arr[5] = arr[0] + 50;
let x = arr[5];         // x = 150
```

**Method calls**:
```jack
// Static function call
let result = Math.multiply(5, 10);

// Method call on object
let p = Point.new(10, 20);
let x = p.getX();

// Method call with no return value
do p.setX(30);
do Output.printString("Hello, World!");
```

### Statements

**Let statement** (assignment):
```jack
let x = 10;
let y = x + 5;
let arr[i] = arr[i] + 1;
```

**If statement**:
```jack
if (x > 0) {
    let y = x;
} else {
    let y = -x;
}

// Else clause is optional
if (done) {
    return;
}
```

**While statement**:
```jack
while (x > 0) {
    let x = x - 1;
    let sum = sum + x;
}
```

**Do statement** (void method call):
```jack
// Call method that returns void or discard return value
do Output.printInt(42);
do game.run();
do Memory.deAlloc(this);
```

**Return statement**:
```jack
// Functions/methods must return
return x + y;

// Void methods return nothing
return;
```

🎓 **Key insight**: Jack has **no for loops**. Use while loops for iteration. This simplicity makes the compiler easier to implement while remaining Turing-complete.

### Methods vs. Functions

**Methods** (operate on instance):
```jack
method int getX() {
    return x;    // Access instance field
}

method void move(int dx, int dy) {
    let x = x + dx;    // Modify instance state
    let y = y + dy;
    return;
}
```
- Implicitly receive `this` as `argument 0`
- Can access instance fields directly
- Compiled as: `call ClassName.methodName nArgs+1` (extra arg for `this`)

**Functions** (static, no instance):
```jack
function int max(int a, int b) {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}

function Point new(int ax, int ay) {
    var Point p;
    let p = Memory.alloc(2);    // Allocate memory for 2 fields
    let p.x = ax;
    let p.y = ay;
    return p;
}
```
- No access to instance fields (no `this`)
- Often used for constructors, utility functions
- Compiled as: `call ClassName.functionName nArgs`

**Constructors** (special functions that return instance):
```jack
constructor Circle new(int ax, int ay, int ar) {
    let x = ax;
    let y = ay;
    let radius = ar;
    return this;    // Must return 'this'
}
```
- Must be declared as `constructor`
- Must allocate memory: `Memory.alloc(nFields)`
- Must return `this`

### Arrays

**Array creation**:
```jack
var Array a;
let a = Array.new(5);    // Array of 5 elements
```

**Array access**:
```jack
let a[0] = 10;
let a[1] = 20;
let sum = a[0] + a[1];
```

**Multi-dimensional arrays** (array of arrays):
```jack
var Array matrix;
let matrix = Array.new(3);        // 3 rows
let matrix[0] = Array.new(4);     // Row 0 has 4 columns
let matrix[1] = Array.new(4);
let matrix[2] = Array.new(4);

let matrix[1][2] = 99;            // Set element at row 1, col 2
```

**Memory management**:
```jack
var Array a;
let a = Array.new(100);
// ... use array ...
do a.dispose();         // Free memory when done
```

🎓 **Key insight**: Jack has **manual memory management**. You must explicitly call `dispose()` to free heap memory. This is like C's `malloc`/`free`, not Java's garbage collection.

### Strings

**String creation**:
```jack
var String s;
let s = String.new(10);      // Max length 10
do s.appendChar(72);         // 'H'
do s.appendChar(105);        // 'i'
```

**String literals** (in do/let statements):
```jack
do Output.printString("Hello, World!");
```

**String operations**:
```jack
let len = s.length();
let ch = s.charAt(0);
do s.setCharAt(0, 74);       // Change 'H' to 'J'
do s.eraseLastChar();
```

### The Jack Standard Library

Jack programs rely on a standard library (OS) that you'll implement in Projects 11-12:

**Math** - Mathematical operations:
```jack
Math.multiply(x, y)      // x * y
Math.divide(x, y)        // x / y
Math.sqrt(x)             // √x
Math.min(x, y)           // minimum
Math.max(x, y)           // maximum
Math.abs(x)              // |x|
```

**String** - String manipulation:
```jack
String.new(maxLen)       // Create string
s.length()               // Length
s.charAt(i)              // Get character
s.setCharAt(i, c)        // Set character
s.appendChar(c)          // Append character
s.eraseLastChar()        // Remove last char
s.intValue()             // Parse as integer
s.setInt(i)              // Convert int to string
```

**Array** - Array creation:
```jack
Array.new(size)          // Create array
a.dispose()              // Free array memory
```

**Output** - Text output:
```jack
Output.printChar(c)      // Print character
Output.printString(s)    // Print string
Output.printInt(i)       // Print integer
Output.println()         // Print newline
Output.backSpace()       // Backspace
```

**Screen** - Graphics:
```jack
Screen.clearScreen()     // Clear screen
Screen.setColor(b)       // Set draw color (black/white)
Screen.drawPixel(x, y)   // Draw pixel
Screen.drawLine(x1, y1, x2, y2)
Screen.drawRectangle(x1, y1, x2, y2)
Screen.drawCircle(x, y, r)
```

**Keyboard** - Input:
```jack
Keyboard.keyPressed()    // Get current key code (0 if none)
Keyboard.readChar()      // Read next character (blocking)
Keyboard.readLine(msg)   // Read line of text
Keyboard.readInt(msg)    // Read integer
```

**Memory** - Heap management:
```jack
Memory.peek(addr)        // Read RAM[addr]
Memory.poke(addr, val)   // Write RAM[addr] = val
Memory.alloc(size)       // Allocate heap block
Memory.deAlloc(obj)      // Free heap block
```

**Sys** - System functions:
```jack
Sys.halt()               // Stop execution
Sys.error(errCode)       // Display error and halt
Sys.wait(duration)       // Wait N milliseconds
```

## Learning Path

### Step 1: Understand Jack Syntax (2-3 hours)

Read through the language specification above and study example programs.

**Study this complete program**:

File: `Main.jack`
```jack
/**
 * Compute sum of integers 1 to n
 */
class Main {
    function void main() {
        var int n, sum;

        do Output.printString("Enter n: ");
        let n = Keyboard.readInt("");
        let sum = Main.sumTo(n);

        do Output.printString("Sum = ");
        do Output.printInt(sum);
        do Output.println();

        return;
    }

    /** Compute 1 + 2 + ... + n */
    function int sumTo(int n) {
        var int sum, i;
        let sum = 0;
        let i = 1;

        while (i < (n + 1)) {
            let sum = sum + i;
            let i = i + 1;
        }

        return sum;
    }
}
```

**Trace through execution**:
1. Program starts at `Main.main()` (entry point)
2. Prompt user for input
3. Call `Main.sumTo(n)` to compute sum
4. Print result
5. Return from main (program halts)

**Questions to answer**:
- What VM segments store `n`, `sum`, `i`?
- How is `Main.sumTo` called from `Main.main`?
- What VM code implements the while loop?
- How does `Keyboard.readInt` work?

### Step 2: Write Simple Programs (3-4 hours)

Start with basic programs to get comfortable with Jack syntax.

**Program 1: Hello World**
```jack
class Main {
    function void main() {
        do Output.printString("Hello, World!");
        do Output.println();
        return;
    }
}
```

**Program 2: Factorial**
```jack
class Main {
    function void main() {
        do Output.printString("Factorial of 5 = ");
        do Output.printInt(Main.factorial(5));
        do Output.println();
        return;
    }

    function int factorial(int n) {
        var int result;

        if (n < 2) {
            return 1;
        } else {
            let result = Main.factorial(n - 1);
            return n * result;
        }
    }
}
```

**Program 3: Array Average**
```jack
class Main {
    function void main() {
        var Array arr;
        var int i, sum, avg;

        let arr = Array.new(5);
        let arr[0] = 10;
        let arr[1] = 20;
        let arr[2] = 30;
        let arr[3] = 40;
        let arr[4] = 50;

        let sum = 0;
        let i = 0;
        while (i < 5) {
            let sum = sum + arr[i];
            let i = i + 1;
        }

        let avg = sum / 5;

        do Output.printString("Average = ");
        do Output.printInt(avg);
        do Output.println();

        do arr.dispose();
        return;
    }
}
```

### Step 3: Implement a Class (4-5 hours)

Create a non-trivial class with fields, methods, and a constructor.

**Example: Point class**

File: `Point.jack`
```jack
/**
 * Represents a 2D point with x,y coordinates
 */
class Point {
    field int x, y;

    /** Constructor */
    constructor Point new(int ax, int ay) {
        let x = ax;
        let y = ay;
        return this;
    }

    /** Destructor */
    method void dispose() {
        do Memory.deAlloc(this);
        return;
    }

    /** Getters */
    method int getX() {
        return x;
    }

    method int getY() {
        return y;
    }

    /** Setters */
    method void setX(int newX) {
        let x = newX;
        return;
    }

    method void setY(int newY) {
        let y = newY;
        return;
    }

    /** Move point by dx, dy */
    method void move(int dx, int dy) {
        let x = x + dx;
        let y = y + dy;
        return;
    }

    /** Distance from origin (approx using Manhattan distance) */
    method int distanceFromOrigin() {
        var int absX, absY;
        let absX = Math.abs(x);
        let absY = Math.abs(y);
        return absX + absY;
    }

    /** Print point */
    method void print() {
        do Output.printString("(");
        do Output.printInt(x);
        do Output.printString(", ");
        do Output.printInt(y);
        do Output.printString(")");
        return;
    }
}
```

File: `Main.jack`
```jack
class Main {
    function void main() {
        var Point p1, p2;

        let p1 = Point.new(10, 20);
        let p2 = Point.new(30, 40);

        do Output.printString("p1 = ");
        do p1.print();
        do Output.println();

        do Output.printString("p2 = ");
        do p2.print();
        do Output.println();

        do p1.move(5, -3);
        do Output.printString("After move, p1 = ");
        do p1.print();
        do Output.println();

        do p1.dispose();
        do p2.dispose();

        return;
    }
}
```

**What to learn**:
- How constructors allocate memory
- How methods access instance fields via `this`
- How to manage object lifecycle (construct → use → dispose)

### Step 4: Build a Data Structure (5-6 hours)

Implement a linked list or stack to understand OOP composition.

**Example: Linked List**

File: `Node.jack`
```jack
/** Linked list node */
class Node {
    field int data;
    field Node next;

    constructor Node new(int value) {
        let data = value;
        let next = null;
        return this;
    }

    method void dispose() {
        // Don't recursively dispose 'next' here
        // (List class handles that)
        do Memory.deAlloc(this);
        return;
    }

    method int getData() {
        return data;
    }

    method Node getNext() {
        return next;
    }

    method void setNext(Node n) {
        let next = n;
        return;
    }
}
```

File: `List.jack`
```jack
/** Singly-linked list */
class List {
    field Node head;
    field int size;

    constructor List new() {
        let head = null;
        let size = 0;
        return this;
    }

    method void dispose() {
        var Node current, next;
        let current = head;

        while (~(current = null)) {
            let next = current.getNext();
            do current.dispose();
            let current = next;
        }

        do Memory.deAlloc(this);
        return;
    }

    /** Add element to front (O(1)) */
    method void addFront(int value) {
        var Node newNode;
        let newNode = Node.new(value);
        do newNode.setNext(head);
        let head = newNode;
        let size = size + 1;
        return;
    }

    /** Get size */
    method int getSize() {
        return size;
    }

    /** Print list */
    method void print() {
        var Node current;
        let current = head;

        do Output.printString("[");

        while (~(current = null)) {
            do Output.printInt(current.getData());
            let current = current.getNext();

            if (~(current = null)) {
                do Output.printString(", ");
            }
        }

        do Output.printString("]");
        return;
    }
}
```

File: `Main.jack`
```jack
class Main {
    function void main() {
        var List list;

        let list = List.new();

        do list.addFront(10);
        do list.addFront(20);
        do list.addFront(30);

        do Output.printString("List: ");
        do list.print();
        do Output.println();

        do Output.printString("Size: ");
        do Output.printInt(list.getSize());
        do Output.println();

        do list.dispose();

        return;
    }
}
```

**Expected output**:
```
List: [30, 20, 10]
Size: 3
```

### Step 5: Implement a Game (10-15 hours)

Build a complete interactive application. This is the capstone project for Jack programming.

**Example: Snake Game**

I'll provide a simplified version. You can extend it with scoring, levels, etc.

File: `Snake.jack`
```jack
/** Snake game */
class Snake {
    field Array bodyX, bodyY;    // Snake body coordinates
    field int length;            // Current length
    field int maxLength;         // Max capacity
    field int dirX, dirY;        // Current direction
    field boolean alive;

    constructor Snake new() {
        let maxLength = 100;
        let bodyX = Array.new(maxLength);
        let bodyY = Array.new(maxLength);

        // Start at center, length 3
        let length = 3;
        let bodyX[0] = 128;
        let bodyY[0] = 128;
        let bodyX[1] = 127;
        let bodyY[1] = 128;
        let bodyX[2] = 126;
        let bodyY[2] = 128;

        let dirX = 1;      // Moving right
        let dirY = 0;
        let alive = true;

        return this;
    }

    method void dispose() {
        do bodyX.dispose();
        do bodyY.dispose();
        do Memory.deAlloc(this);
        return;
    }

    method void setDirection(int dx, int dy) {
        // Prevent 180-degree turns
        if (~((dirX + dx) = 0) | ~((dirY + dy) = 0)) {
            let dirX = dx;
            let dirY = dy;
        }
        return;
    }

    method void move() {
        var int i, newX, newY;

        if (~alive) {
            return;
        }

        // Calculate new head position
        let newX = bodyX[0] + dirX;
        let newY = bodyY[0] + dirY;

        // Check wall collision
        if ((newX < 0) | (newX > 255) | (newY < 0) | (newY > 255)) {
            let alive = false;
            return;
        }

        // Check self collision
        let i = 0;
        while (i < length) {
            if ((bodyX[i] = newX) & (bodyY[i] = newY)) {
                let alive = false;
                return;
            }
            let i = i + 1;
        }

        // Move body (shift all segments back)
        let i = length - 1;
        while (i > 0) {
            let bodyX[i] = bodyX[i - 1];
            let bodyY[i] = bodyY[i - 1];
            let i = i - 1;
        }

        // Move head
        let bodyX[0] = newX;
        let bodyY[0] = newY;

        return;
    }

    method void grow() {
        if (length < maxLength) {
            let length = length + 1;
        }
        return;
    }

    method boolean isAlive() {
        return alive;
    }

    method void draw() {
        var int i;
        let i = 0;

        while (i < length) {
            do Screen.setColor(true);
            do Screen.drawRectangle(bodyX[i] * 2, bodyY[i] * 2,
                                     (bodyX[i] * 2) + 1, (bodyY[i] * 2) + 1);
            let i = i + 1;
        }

        return;
    }

    method int getHeadX() {
        return bodyX[0];
    }

    method int getHeadY() {
        return bodyY[0];
    }
}
```

File: `Food.jack`
```jack
/** Food for snake */
class Food {
    field int x, y;

    constructor Food new(int ax, int ay) {
        let x = ax;
        let y = ay;
        return this;
    }

    method void dispose() {
        do Memory.deAlloc(this);
        return;
    }

    method int getX() {
        return x;
    }

    method int getY() {
        return y;
    }

    method void draw() {
        do Screen.setColor(true);
        do Screen.drawCircle(x * 2, y * 2, 2);
        return;
    }
}
```

File: `Game.jack`
```jack
/** Snake game controller */
class Game {
    field Snake snake;
    field Food food;
    field int score;
    field boolean exit;

    constructor Game new() {
        let snake = Snake.new();
        let food = Food.new(200, 100);
        let score = 0;
        let exit = false;
        return this;
    }

    method void dispose() {
        do snake.dispose();
        do food.dispose();
        do Memory.deAlloc(this);
        return;
    }

    method void run() {
        var int key;
        var int delay;

        let delay = 100;

        while ((~exit) & snake.isAlive()) {
            // Handle input
            let key = Keyboard.keyPressed();

            if (key = 81) { let exit = true; }                    // Q = quit
            if (key = 131) { do snake.setDirection(0, -1); }      // Up arrow
            if (key = 133) { do snake.setDirection(0, 1); }       // Down arrow
            if (key = 130) { do snake.setDirection(-1, 0); }      // Left arrow
            if (key = 132) { do snake.setDirection(1, 0); }       // Right arrow

            // Move snake
            do snake.move();

            // Check food collision
            if ((snake.getHeadX() = food.getX()) & (snake.getHeadY() = food.getY())) {
                do snake.grow();
                let score = score + 10;

                // Respawn food (simple random position)
                do food.dispose();
                let food = Food.new(100, 50);    // TODO: Real random position
            }

            // Draw
            do Screen.clearScreen();
            do snake.draw();
            do food.draw();

            do Output.moveCursor(0, 0);
            do Output.printString("Score: ");
            do Output.printInt(score);

            // Delay
            do Sys.wait(delay);
        }

        // Game over
        do Screen.clearScreen();
        do Output.moveCursor(10, 25);
        do Output.printString("GAME OVER");
        do Output.moveCursor(12, 22);
        do Output.printString("Final Score: ");
        do Output.printInt(score);

        return;
    }
}
```

File: `Main.jack`
```jack
class Main {
    function void main() {
        var Game game;

        let game = Game.new();
        do game.run();
        do game.dispose();

        return;
    }
}
```

**Game features**:
- Snake moves continuously in current direction
- Arrow keys change direction
- Eating food increases score and length
- Hitting walls or self ends game
- Press Q to quit

**Extension ideas**:
- Add random food placement
- Increase speed as snake grows
- Add obstacles
- Track high scores
- Add sound effects

### Step 6: Understand Jack-to-VM Compilation (3-4 hours)

Study how Jack code compiles to VM code to prepare for Project 10-11.

**Example compilation**:

**Jack code**:
```jack
function int sum(int n) {
    var int i, result;
    let i = 1;
    let result = 0;

    while (i < (n + 1)) {
        let result = result + i;
        let i = i + 1;
    }

    return result;
}
```

**VM code**:
```vm
function Main.sum 2           // 2 local variables: i, result

// let i = 1
push constant 1
pop local 0                   // local 0 = i

// let result = 0
push constant 0
pop local 1                   // local 1 = result

// while loop
label WHILE_EXP0
    push local 0              // i
    push argument 0           // n
    push constant 1
    add                       // n + 1
    lt                        // i < (n + 1)
    not
    if-goto WHILE_END0

    // let result = result + i
    push local 1              // result
    push local 0              // i
    add
    pop local 1               // result = result + i

    // let i = i + 1
    push local 0              // i
    push constant 1
    add
    pop local 0               // i = i + 1

    goto WHILE_EXP0

label WHILE_END0

// return result
push local 1
return
```

**Key observations**:
- Function declares number of local variables
- Variables map to VM segments (local, argument, static, field)
- While loop compiles to labels + if-goto + goto
- Expressions compile to stack operations
- Method calls become VM `call` commands

## Deep Dive: Implementation Insights

### Memory Layout for Objects

When you create an object with `let p = Point.new(10, 20);`, here's what happens:

**Step 1: Constructor allocates memory**
```jack
constructor Point new(int ax, int ay) {
    let x = ax;
    let y = ay;
    return this;
}
```

**Compiles to VM**:
```vm
function Point.new 0          // 0 local variables

push constant 2               // Size = 2 fields (x, y)
call Memory.alloc 1           // Allocate heap memory
pop pointer 0                 // pointer 0 = THIS

push argument 0               // ax
pop this 0                    // this.x = ax

push argument 1               // ay
pop this 1                    // this.y = ay

push pointer 0                // Return THIS
return
```

**Memory allocation**:
```
Heap (RAM 2048-16383):
┌─────────────────┐
│  ...            │
├─────────────────┤
│  this.x (ax)    │  ← Memory.alloc returns this address
├─────────────────┤
│  this.y (ay)    │
├─────────────────┤
│  ...            │
└─────────────────┘
```

**Step 2: Reference stored in variable**
```jack
var Point p;
let p = Point.new(10, 20);
```

**Variable `p` stores the heap address** (pointer to the object).

**Step 3: Method call uses pointer**
```jack
let x = p.getX();
```

**Compiles to VM**:
```vm
push local 0                  // Push object pointer (p)
call Point.getX 1             // Call with object as argument 0
pop local 1                   // x = return value
```

**Inside `Point.getX()`**:
```vm
function Point.getX 0
push argument 0               // argument 0 = THIS pointer (passed by caller)
pop pointer 0                 // Set THIS to object address
push this 0                   // Return this.x
return
```

🎓 **Key insight**: Methods receive `this` as the first argument (implicitly). The caller pushes the object pointer, and the method sets `pointer 0` (THIS) to that address. This is how instance methods access fields!

### Variable Mapping to VM Segments

Jack variables map to VM memory segments based on their kind:

**Example class**:
```jack
class Example {
    static int count;              // Static variable
    field int x, y;                // Field variables (instance)

    method void foo(int a, int b) {  // Parameters
        var int temp, result;       // Local variables

        let temp = a + b;           // temp is local 0
        let result = temp * 2;      // result is local 1
        let x = result;             // x is this 0
        let y = count;              // y is this 1, count is static 0

        return;
    }
}
```

**VM segment mapping**:
```
Parameters:      argument segment
  this (implicit) → argument 0
  a               → argument 1
  b               → argument 2

Local variables: local segment
  temp            → local 0
  result          → local 1

Field variables: this segment (object instance)
  x               → this 0
  y               → this 1

Static variables: static segment (class-level)
  count           → static 0
```

**Compiled VM code**:
```vm
function Example.foo 2        // 2 locals: temp, result

// let temp = a + b
push argument 1               // a
push argument 2               // b
add
pop local 0                   // temp

// let result = temp * 2
push local 0                  // temp
push constant 2
call Math.multiply 2
pop local 1                   // result

// let x = result
push argument 0               // THIS pointer (implicit first argument)
pop pointer 0                 // Set THIS
push local 1                  // result
pop this 0                    // this.x = result

// let y = count
push argument 0
pop pointer 0                 // Set THIS
push static 0                 // count
pop this 1                    // this.y = count

push constant 0
return
```

### Expression Compilation Strategy

Jack expressions compile to **postfix (stack-based) evaluation**:

**Infix expression** (Jack):
```jack
let result = (a + b) * (c - d);
```

**Postfix evaluation** (VM):
```vm
push local 0      // a
push local 1      // b
add               // a + b
push local 2      // c
push local 3      // d
sub               // c - d
call Math.multiply 2    // (a+b) * (c-d)
pop local 4       // result = ...
```

**Evaluation order**:
1. Push left operand
2. Push right operand
3. Apply operator (pops 2, pushes 1)
4. Result is on stack for next operation

**Operator precedence handling**:
- Parser builds expression tree respecting precedence
- Tree traversal (post-order) generates stack code
- Example: `a + b * c` → tree: `+(a, *(b, c))` → VM: `push a, push b, push c, mult, add`

### Control Flow Compilation

**If statement** (Jack):
```jack
if (x > 0) {
    let y = x;
} else {
    let y = -x;
}
```

**VM code**:
```vm
// Evaluate condition
push local 0      // x
push constant 0
gt                // x > 0

// If false, jump to else
not
if-goto IF_FALSE0

// True branch
push local 0      // x
pop local 1       // y = x
goto IF_END0

label IF_FALSE0
// False branch
push local 0      // x
neg
pop local 1       // y = -x

label IF_END0
```

**While statement** (Jack):
```jack
while (i < 10) {
    let sum = sum + i;
    let i = i + 1;
}
```

**VM code**:
```vm
label WHILE_EXP0
    // Evaluate condition
    push local 0      // i
    push constant 10
    lt                // i < 10

    // If false, exit loop
    not
    if-goto WHILE_END0

    // Loop body
    push local 1      // sum
    push local 0      // i
    add
    pop local 1       // sum = sum + i

    push local 0      // i
    push constant 1
    add
    pop local 0       // i = i + 1

    // Repeat
    goto WHILE_EXP0

label WHILE_END0
```

🎓 **Key insight**: Control flow uses **structured jumps**. The compiler generates unique label names (WHILE_EXP0, WHILE_END0) and ensures proper nesting. This is safer than assembly's arbitrary gotos.

## What You Should Understand After This Project

- ✅ **High-level abstraction**: How classes, methods, and OOP hide low-level details
- ✅ **Type system**: How static typing helps catch errors at compile time
- ✅ **Memory management**: Manual allocation/deallocation with constructors/dispose
- ✅ **Expression evaluation**: Infix syntax compiling to stack-based postfix
- ✅ **Object-oriented programming**: Composition, encapsulation, methods vs functions
- ✅ **Program structure**: Classes, methods, fields, local variables, scope
- ✅ **Standard library**: OS functions for I/O, graphics, math, memory

## Common Pitfalls

**1. Forgetting to dispose objects**
```jack
// WRONG (memory leak):
function void test() {
    var Array arr;
    let arr = Array.new(100);
    // ... use array ...
    return;    // Memory leaked!
}

// RIGHT:
function void test() {
    var Array arr;
    let arr = Array.new(100);
    // ... use array ...
    do arr.dispose();    // Free memory
    return;
}
```

**2. Constructor not returning this**
```jack
// WRONG:
constructor Point new(int ax, int ay) {
    let x = ax;
    let y = ay;
    return;    // Returns garbage!
}

// RIGHT:
constructor Point new(int ax, int ay) {
    let x = ax;
    let y = ay;
    return this;    // Must return THIS
}
```

**3. Misunderstanding method vs function**
```jack
// WRONG (method tries to call itself as function):
method void foo() {
    do foo();    // Infinite recursion, wrong signature!
}

// RIGHT (method calls itself as method):
method void foo() {
    do this.foo();    // Explicit 'this' (though rarely useful)
}
```

**4. Array index out of bounds**
```jack
// WRONG:
var Array arr;
let arr = Array.new(5);
let arr[5] = 100;    // Out of bounds! (valid indices: 0-4)

// RIGHT:
var Array arr;
let arr = Array.new(5);
let arr[4] = 100;    // Last valid index
```

**5. Null pointer dereference**
```jack
// WRONG:
var Point p;
let x = p.getX();    // p is null! Crash!

// RIGHT:
var Point p;
let p = Point.new(10, 20);    // Construct object first
let x = p.getX();
```

**6. Comparing objects by reference vs value**
```jack
var Point p1, p2;
let p1 = Point.new(10, 20);
let p2 = Point.new(10, 20);

// Comparison by reference (different objects)
if (p1 = p2) {
    // FALSE - different heap addresses
}

// Must compare fields manually for value equality
if ((p1.getX() = p2.getX()) & (p1.getY() = p2.getY())) {
    // TRUE - same coordinates
}
```

## Extension Ideas

**Level 1: More Programs**
- Calculator with operator precedence
- Text editor with cursor movement
- Conway's Game of Life
- Tic-tac-toe with AI opponent

**Level 2: Advanced Data Structures**
- Binary search tree
- Hash table
- Priority queue (heap)
- Graph with DFS/BFS

**Level 3: Algorithms**
- Sorting algorithms (quicksort, mergesort)
- Pathfinding (A*, Dijkstra)
- String matching (KMP, Boyer-Moore)
- Compression (Huffman coding)

**Level 4: Graphics Applications**
- Paint program with brush tools
- 3D wireframe renderer
- Particle system simulation
- Fractal generator (Mandelbrot set)

**Level 5: Games**
- Breakout/Arkanoid
- Space Invaders
- Tetris
- Maze generator and solver

## Real-World Connection

**Jack is similar to early versions of**:

**Java (circa 1995)**:
- Class-based OOP ✓
- Static typing ✓
- Manual array management ✓
- Difference: Java has garbage collection, interfaces, exceptions

**C++ (subset)**:
- Object-oriented ✓
- Manual memory management (new/delete) ✓
- Methods and constructors ✓
- Difference: C++ has templates, operator overloading, multiple inheritance

**Pascal (Object Pascal)**:
- Structured programming ✓
- Static typing ✓
- Procedures and functions ✓
- Difference: Pascal has more built-in types, pointers, file I/O

**Why simple languages still matter**:
1. **Embedded systems**: Limited resources require simple runtimes
2. **Teaching**: Easier to learn fundamentals without language complexity
3. **Compilation**: Simpler to implement compilers for simple languages
4. **Verification**: Easier to prove correctness with fewer features

## Success Criteria

You've mastered this project when you can:

1. **Write Jack programs**: Create classes with fields, methods, constructors
2. **Understand OOP**: Explain encapsulation, composition, object lifecycle
3. **Trace compilation**: Convert Jack code to VM code mentally
4. **Debug programs**: Identify syntax errors, logic errors, memory leaks
5. **Design abstractions**: Break problems into classes and methods
6. **Use standard library**: Call OS functions for I/O, graphics, math

## Next Steps

**Project 10: Syntax Analyzer (Compiler Frontend)**

Now that you can write Jack programs, you'll build the **parser** that reads Jack source code:
- **Lexical analysis (tokenizer)**: Break source into tokens (keywords, symbols, identifiers)
- **Syntax analysis (parser)**: Build parse tree or XML output
- **Grammar rules**: Implement recursive descent parser
- **Error handling**: Detect and report syntax errors

**Example tokenization**:
```jack
class Point {
    field int x;
}
```

**Tokens**:
```
<keyword> class </keyword>
<identifier> Point </identifier>
<symbol> { </symbol>
<keyword> field </keyword>
<keyword> int </keyword>
<identifier> x </identifier>
<symbol> ; </symbol>
<symbol> } </symbol>
```

**Project 11: Code Generator (Compiler Backend)**

With a parser, you'll implement **code generation** to compile Jack to VM:
- **Symbol tables**: Track variables, types, scopes
- **Expression compilation**: Convert infix to stack operations
- **Control flow**: Generate labels for if/while statements
- **Object management**: Compile constructors, method calls, field access

**Complete the toolchain**:
```
Jack source code (human writes)
    ↓ [Project 10: Parser]
Parse tree / AST
    ↓ [Project 11: Code generator]
VM code (Projects 7-8)
    ↓ [VM translator you built]
Assembly code (Project 6)
    ↓ [Assembler you built]
Machine code
    ↓ [Computer you built in Phase 1]
EXECUTION!
```

**Project 12: Operating System**

Finally, implement the Jack OS in Jack itself:
- **Math**: Multiply, divide, sqrt using bit operations
- **String**: String class implementation
- **Memory**: Heap allocator (malloc/free using first-fit or best-fit)
- **Screen**: Pixel/line/circle drawing algorithms
- **Keyboard**: Keyboard input buffering
- **Sys**: System initialization and halt

---

**Congratulations!** You've learned a complete high-level programming language. You can now write non-trivial applications with OOP, data structures, and graphics. The next step is building the compiler that translates Jack to VM code!

The journey continues:
- ✅ Hardware layer (gates → computer)
- ✅ Assembly language (symbolic programming)
- ✅ Virtual machine (stack-based execution)
- ✅ High-level language (Jack programming)
- 🚧 Compiler (Jack → VM)
- 🚧 Operating system (Jack OS library)

**Next**: Build the compiler that makes this all work! 🚀

---

## Summary: What You Built

**You have learned to write programs in Jack**, a high-level object-oriented language that compiles to VM code:

1. **Designed** classes with fields, methods, constructors
2. **Implemented** data structures (linked lists, arrays, trees)
3. **Created** interactive applications and games
4. **Understood** object-oriented programming concepts
5. **Traced** compilation from Jack to VM to assembly
6. **Used** standard library for I/O, graphics, and math

**Technical accomplishments**:
- ✅ Class-based OOP with encapsulation
- ✅ Static typing with primitives and class types
- ✅ Manual memory management (constructors/dispose)
- ✅ Control flow (if/else, while loops)
- ✅ Expression evaluation with operator precedence
- ✅ Standard library usage (OS functions)

**Why this matters**:
You've climbed the abstraction ladder from **gates to high-level programming**:
- Hardware (Project 1-5): AND gates, registers, CPU
- Assembly (Project 6): Symbolic instructions
- VM (Project 7-8): Stack machine, functions
- **Jack (Project 9): OOP, classes, methods** ← You are here

**The final step**: Build the compiler that translates Jack to VM, completing your journey from NAND gates to applications! 🎉
