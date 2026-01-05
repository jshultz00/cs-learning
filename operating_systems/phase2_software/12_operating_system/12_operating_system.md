# Project 12: Jack Operating System

**Objective**: Implement a complete operating system library providing essential services to Jack programs

## Background Concepts

### What You've Built So Far

**Phase 1: Hardware Layer (Projects 1-5)**
- ✅ Complete computer from NAND gates to Von Neumann architecture
- ✅ 32K RAM, 32K ROM, screen memory-mapped I/O, keyboard input

**Phase 2: Software Stack (Projects 6-11)**
- ✅ **Assembler** (Project 6): Assembly → Machine code
- ✅ **VM Translator** (Projects 7-8): VM code → Assembly
- ✅ **Jack Language** (Project 9): High-level OOP language
- ✅ **Parser** (Project 10): Jack source → Parse tree
- ✅ **Code Generator** (Project 11): Parse tree → VM code

**The Complete Toolchain**:
```
Jack Source (.jack)
      ↓
  [Compiler] ← Projects 10-11
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

### The Problem: No Standard Library

Your Jack compiler works, but programs can only use what you explicitly code:

**Problem 1: No basic arithmetic**
```jack
// Jack compiler supports: +, -, &, |, <, >, =
// But how do you multiply? Divide? Compute square root?
let product = x * y;  // Compiler generates: call Math.multiply 2
// Someone needs to implement Math.multiply!
```

**Problem 2: No I/O**
```jack
// How do you print to screen?
do Output.printString("Hello");  // Needs Output library

// How do you read keyboard?
let key = Keyboard.readChar();  // Needs Keyboard library

// How do you draw graphics?
do Screen.drawCircle(x, y, r);  // Needs Screen library
```

**Problem 3: No memory management**
```jack
// How do you allocate objects?
let arr = Array.new(100);  // Needs Memory.alloc()

// How do you free memory?
do arr.dispose();  // Needs Memory.deAlloc()
```

**Problem 4: No utility functions**
```jack
// How do you work with strings?
let s = String.new(20);  // Needs String library

// How do you handle errors?
do Sys.error(5);  // Needs Sys library
```

### The Solution: Jack Operating System

Project 12 implements the **Jack OS**—a library of 8 classes providing essential services:

| Class      | Purpose                                  | Key Methods                                    |
|------------|------------------------------------------|------------------------------------------------|
| **Math**   | Arithmetic operations                    | multiply, divide, sqrt, min, max, abs          |
| **String** | String manipulation                      | new, appendChar, intValue, setInt              |
| **Array**  | Array allocation                         | new, dispose                                   |
| **Memory** | Heap management                          | alloc, deAlloc                                 |
| **Screen** | Graphics primitives                      | drawPixel, drawLine, drawRectangle, drawCircle |
| **Output** | Text output                              | printChar, printString, printInt, println      |
| **Keyboard** | User input                             | keyPressed, readChar, readLine, readInt        |
| **Sys**    | System services                          | halt, error, wait                              |

**What makes this an "OS"**:
- **Abstraction**: Hides hardware details (screen memory, keyboard register)
- **Resource management**: Manages heap memory (malloc/free)
- **Standard interface**: Common API for all Jack programs
- **System services**: Error handling, timing, initialization

## The Jack OS API

### Math Class

Provides arithmetic operations using only addition and bitwise operations.

**Constructor**: None (all static functions)

**Methods**:
```jack
function int multiply(int x, int y)    // Returns x * y
function int divide(int x, int y)      // Returns x / y (integer division)
function int min(int x, int y)         // Returns minimum
function int max(int x, int y)         // Returns maximum
function int sqrt(int x)               // Returns integer part of sqrt(x)
function int abs(int x)                // Returns absolute value
```

**Implementation challenges**:
- **Multiply**: Use binary addition (shift-and-add algorithm)
- **Divide**: Use repeated subtraction with optimization
- **Sqrt**: Use binary search in range [0, x/2]

**Example**:
```jack
var int product, quotient, root;
let product = Math.multiply(17, 5);  // 85
let quotient = Math.divide(100, 3);  // 33
let root = Math.sqrt(144);           // 12
```

### String Class

Manages character arrays with dynamic length.

**Constructor**:
```jack
constructor String new(int maxLength)  // Creates string with capacity
```

**Methods**:
```jack
method void dispose()                      // Frees memory
method int length()                        // Returns current length
method char charAt(int j)                  // Returns char at index j
method void setCharAt(int j, char c)       // Sets char at index j
method String appendChar(char c)           // Appends character, returns this
method void eraseLastChar()                // Removes last character
method int intValue()                      // Converts string to integer
method void setInt(int n)                  // Sets string to represent n
```

**Implementation details**:
- Store characters in array
- Track current length separately from capacity
- Handle integer parsing (including negative numbers)
- Handle integer-to-string conversion

**Example**:
```jack
var String s;
let s = String.new(20);
do s.appendChar(72);   // 'H'
do s.appendChar(105);  // 'i'
do Output.printString(s);  // Prints "Hi"

let s = String.new(6);
do s.setInt(-152);
do Output.printString(s);  // Prints "-152"
```

### Array Class

Simple wrapper for memory allocation (delegates to Memory).

**Constructor**:
```jack
constructor Array new(int size)  // Allocates array of size
```

**Methods**:
```jack
method void dispose()  // Frees array memory
```

**Usage**:
```jack
var Array arr;
let arr = Array.new(100);  // Allocate 100 integers
let arr[0] = 10;
let arr[50] = arr[0] + 5;
do arr.dispose();
```

### Memory Class

Heap manager implementing dynamic memory allocation.

**Constructor**: None (all static functions)

**Methods**:
```jack
function int peek(int address)              // Returns value at RAM[address]
function void poke(int address, int value)  // Sets RAM[address] = value
function Array alloc(int size)              // Allocates memory block
function void deAlloc(Array object)         // Frees memory block
```

**Implementation challenges**:
- **Free list**: Maintain linked list of available blocks
- **First-fit algorithm**: Find first block large enough
- **Fragmentation**: Handle block splitting and merging
- **Heap layout**: Heap starts at address 2048, ends at 16383

**Heap structure**:
```
Address 2048: [length: 14334, next: null] (initial free block)
Address 16383: End of heap
```

**Allocated block format**:
```
[size | data data data ...]
 ↑     ↑
 Header User data (returned address)
```

**Free block format**:
```
[size | next | unused unused ...]
 ↑     ↑
 Size  Pointer to next free block
```

**Example**:
```jack
var Array a, b;
let a = Memory.alloc(100);  // Allocate 100 words
let b = Memory.alloc(50);   // Allocate 50 words
do Memory.deAlloc(a);       // Free first block
do Memory.deAlloc(b);       // Free second block
```

### Screen Class

Provides graphics primitives operating on 256x512 pixel monochrome screen.

**Constructor**: None (all static functions)

**Methods**:
```jack
function void clearScreen()                                    // Clears screen (all white)
function void setColor(boolean b)                              // true=black, false=white
function void drawPixel(int x, int y)                          // Draws single pixel
function void drawLine(int x1, int y1, int x2, int y2)         // Draws line
function void drawRectangle(int x1, int y1, int x2, int y2)    // Draws filled rectangle
function void drawCircle(int x, int y, int r)                  // Draws filled circle
```

**Screen memory map**:
- Base address: 16384 (0x4000)
- Size: 8192 words (256 rows × 512 pixels / 16 pixels per word)
- Layout: Row-major, 32 words per row
- Coordinate system: (0,0) is top-left, (511, 255) is bottom-right

**Memory address calculation**:
```
address = 16384 + (y * 32) + (x / 16)
bit_position = x mod 16
```

**Implementation challenges**:
- **Line drawing**: Bresenham's algorithm (integer-only)
- **Circle drawing**: Midpoint circle algorithm
- **Bit manipulation**: Set/clear individual bits in 16-bit words

**Example**:
```jack
do Screen.clearScreen();
do Screen.setColor(true);           // Black
do Screen.drawRectangle(0, 0, 100, 50);
do Screen.drawCircle(256, 128, 50);
do Screen.drawLine(0, 0, 511, 255);
```

### Output Class

Manages text output to screen using 11-row × 64-column character grid.

**Constructor**: None (all static functions)

**Methods**:
```jack
function void moveCursor(int i, int j)    // Move cursor to row i, column j
function void printChar(char c)            // Print character at cursor
function void printString(String s)        // Print string
function void printInt(int n)              // Print integer
function void println()                    // Print newline
function void backSpace()                  // Move cursor back, erase char
```

**Character set**:
- Each character is 11 pixels tall × 8 pixels wide
- Font map stores bitmap for each ASCII character (32-126)
- Characters beyond 126 print as rectangles

**Cursor management**:
- Tracks current row (0-22) and column (0-63)
- Automatically wraps at end of line
- Scrolling not required (cursor wraps to (0,0))

**Implementation details**:
- Use Screen.drawPixel to render character bitmaps
- Handle special characters: newline (128), backspace (129)
- Convert integers to strings for printing

**Example**:
```jack
do Output.moveCursor(5, 10);
do Output.printString("Score: ");
do Output.printInt(score);
do Output.println();
```

### Keyboard Class

Reads character input from memory-mapped keyboard register.

**Constructor**: None (all static functions)

**Methods**:
```jack
function char keyPressed()      // Returns currently pressed key (0 if none)
function char readChar()        // Waits for key press, displays, returns char
function String readLine(String message)  // Displays message, reads line
function int readInt(String message)      // Displays message, reads integer
```

**Keyboard memory map**:
- Address: 24576 (0x6000)
- Value: ASCII code of currently pressed key (0 if none)

**Key codes**:
- Regular keys: ASCII values (32-126)
- Special keys: newline=128, backspace=129, left=130, up=131, right=132, down=133, home=134, end=135, page up=136, page down=137, insert=138, delete=139, esc=140, F1-F12=141-152

**Implementation challenges**:
- **Key detection**: Poll keyboard register until non-zero
- **Key release**: Wait for key to be released (register returns to 0)
- **Line reading**: Handle backspace, echo characters, detect newline
- **Integer parsing**: Convert input string to number

**Example**:
```jack
var char key;
var String name;
var int age;

let key = Keyboard.readChar();          // Read single char
let name = Keyboard.readLine("Name: "); // Read line
let age = Keyboard.readInt("Age: ");    // Read integer
```

### Sys Class

Provides system-level services.

**Constructor**: None (all static functions)

**Methods**:
```jack
function void halt()           // Halts program execution
function void error(int errorCode)  // Prints error and halts
function void wait(int duration)    // Waits ~duration milliseconds
```

**Additional (internal)**:
```jack
function void init()  // Initializes OS (called before Main.main)
```

**Implementation details**:
- **halt()**: Infinite loop
- **error()**: Print error code and halt
- **wait()**: Busy-wait loop (calibrated to ~1ms per iteration)
- **init()**: Initialize Memory heap, call Main.main(), halt on return

**Example**:
```jack
do Sys.wait(1000);  // Wait 1 second
if (error) {
    do Sys.error(5);  // Print "ERR5" and halt
}
```

## Learning Path

### Step 1: Math Library (2-3 hours)

**Goal**: Implement arithmetic using only addition and bitwise operations

**Multiply Algorithm** (Shift-and-add):
```
multiply(x, y):
    result = 0
    shiftedX = x
    for each bit i in y (from LSB to MSB):
        if bit i of y is 1:
            result = result + shiftedX
        shiftedX = shiftedX + shiftedX  // Left shift (multiply by 2)
    return result
```

**Example**: `multiply(13, 5)` = `13 * 101₂` = `13 * 1 + 13 * 4` = `13 + 52` = `65`

**Divide Algorithm** (Optimized repeated subtraction):
```
divide(x, y):
    if y = 0: error
    if x < y: return 0

    q = divide(x, 2*y)  // Recursive call
    if (x - 2*q*y) < y:
        return 2*q
    else:
        return 2*q + 1
```

**Sqrt Algorithm** (Binary search):
```
sqrt(x):
    low = 0, high = x
    while low <= high:
        mid = (low + high) / 2
        if mid*mid <= x < (mid+1)*(mid+1):
            return mid
        if mid*mid > x:
            high = mid - 1
        else:
            low = mid + 1
```

**Implementation**:

```jack
class Math {
    static Array twoToThe;  // Powers of 2: [1, 2, 4, 8, ..., 16384]

    function void init() {
        var int i, value;
        let twoToThe = Array.new(16);
        let value = 1;
        let i = 0;
        while (i < 16) {
            let twoToThe[i] = value;
            let value = value + value;
            let i = i + 1;
        }
        return;
    }

    function boolean bit(int x, int i) {
        // Returns true if i-th bit of x is 1
        return ~((x & twoToThe[i]) = 0);
    }

    function int multiply(int x, int y) {
        var int sum, shiftedX, i;
        let sum = 0;
        let shiftedX = x;
        let i = 0;

        while (i < 16) {
            if (Math.bit(y, i)) {
                let sum = sum + shiftedX;
            }
            let shiftedX = shiftedX + shiftedX;
            let i = i + 1;
        }
        return sum;
    }

    function int divide(int x, int y) {
        var int result, sign;

        // Handle negative numbers
        if (y = 0) {
            do Sys.error(3);  // Division by zero
        }

        let sign = 1;
        if (x < 0) {
            let x = -x;
            let sign = -sign;
        }
        if (y < 0) {
            let y = -y;
            let sign = -sign;
        }

        let result = Math.divideHelper(x, y);

        if (sign < 0) {
            return -result;
        }
        return result;
    }

    function int divideHelper(int x, int y) {
        var int q;

        if (y > x) {
            return 0;
        }
        if (y < 0) {  // Overflow check (y doubled too much)
            return 0;
        }

        let q = Math.divideHelper(x, y + y);

        if ((x - (2 * q * y)) < y) {
            return q + q;
        } else {
            return q + q + 1;
        }
    }

    function int sqrt(int x) {
        var int low, high, mid, midSquared, midPlus1Squared;

        if (x < 0) {
            do Sys.error(4);  // Square root of negative
        }

        let low = 0;
        let high = x;

        while (low < (high - 1)) {
            let mid = (low + high) / 2;
            let midSquared = mid * mid;

            if (midSquared > x) {
                let high = mid;
            } else {
                let low = mid;
            }
        }

        return low;
    }

    function int min(int x, int y) {
        if (x < y) {
            return x;
        }
        return y;
    }

    function int max(int x, int y) {
        if (x > y) {
            return x;
        }
        return y;
    }

    function int abs(int x) {
        if (x < 0) {
            return -x;
        }
        return x;
    }
}
```

**🎓 Learning Moment**: Hardware multipliers are complex circuits. Software multiplication using shift-and-add mirrors how hardware ALUs work—accumulate partial products.

### Step 2: String Library (2-3 hours)

**Goal**: Manage character arrays and convert between strings and integers

**Key challenges**:
- Integer to string conversion with negative numbers
- String to integer parsing
- Dynamic appending without reallocation

**Implementation**:

```jack
class String {
    field Array chars;
    field int currentLength;
    field int maximumLength;

    constructor String new(int maxLength) {
        if (maxLength < 1) {
            let maxLength = 1;
        }
        let maximumLength = maxLength;
        let currentLength = 0;
        let chars = Array.new(maxLength);
        return this;
    }

    method void dispose() {
        do chars.dispose();
        return;
    }

    method int length() {
        return currentLength;
    }

    method char charAt(int j) {
        return chars[j];
    }

    method void setCharAt(int j, char c) {
        let chars[j] = c;
        return;
    }

    method String appendChar(char c) {
        if (currentLength < maximumLength) {
            let chars[currentLength] = c;
            let currentLength = currentLength + 1;
        }
        return this;
    }

    method void eraseLastChar() {
        if (currentLength > 0) {
            let currentLength = currentLength - 1;
        }
        return;
    }

    method int intValue() {
        var int value, i, digit;
        var boolean isNegative;

        let value = 0;
        let i = 0;
        let isNegative = false;

        // Check for negative sign
        if ((currentLength > 0) & (chars[0] = 45)) {  // '-'
            let isNegative = true;
            let i = 1;
        }

        // Convert digits
        while (i < currentLength) {
            let digit = chars[i] - 48;  // '0' = 48
            let value = (value * 10) + digit;
            let i = i + 1;
        }

        if (isNegative) {
            return -value;
        }
        return value;
    }

    method void setInt(int number) {
        var int temp, digit, i;
        var boolean isNegative;

        let currentLength = 0;
        let isNegative = false;

        if (number < 0) {
            let isNegative = true;
            let number = -number;
        }

        // Build string in reverse
        let temp = number;
        while (true) {
            let digit = temp - ((temp / 10) * 10);  // temp % 10
            let chars[currentLength] = digit + 48;
            let currentLength = currentLength + 1;
            let temp = temp / 10;

            if (temp = 0) {
                let i = currentLength;  // Break point
            }
            if (temp = 0) {
                // Exit loop
                let temp = temp;  // No-op to exit
            }
        }

        // Add negative sign
        if (isNegative) {
            let chars[currentLength] = 45;
            let currentLength = currentLength + 1;
        }

        // Reverse string
        do reverseChars();
        return;
    }

    method void reverseChars() {
        var int i, j;
        var char temp;

        let i = 0;
        let j = currentLength - 1;

        while (i < j) {
            let temp = chars[i];
            let chars[i] = chars[j];
            let chars[j] = temp;
            let i = i + 1;
            let j = j - 1;
        }
        return;
    }
}
```

### Step 3: Memory Library (3-4 hours)

**Goal**: Implement heap allocator with free list

**Heap layout**:
```
Address 2048:    [Initial free block: 14334 words]
Address 16383:   [End of heap]
```

**Free list structure** (singly-linked list):
```
Block: [size | next | unused data...]
       ↑      ↑
       Word 0 Word 1 (pointer to next free block)
```

**Allocation algorithm** (First-fit):
1. Search free list for first block >= requested size
2. If block is much larger, split it
3. Remove allocated portion from free list
4. Return pointer to data (skip size header)

**Implementation**:

```jack
class Memory {
    static Array memory;
    static Array freeList;
    static int heapBase, heapEnd;

    function void init() {
        let heapBase = 2048;
        let heapEnd = 16384;
        let memory = 0;
        let freeList = heapBase;

        // Initialize free list with single large block
        let freeList[0] = heapEnd - heapBase;  // Size
        let freeList[1] = null;                 // Next

        return;
    }

    function int peek(int address) {
        return memory[address];
    }

    function void poke(int address, int value) {
        let memory[address] = value;
        return;
    }

    function Array alloc(int size) {
        var Array block, nextBlock, result;
        var int blockSize;

        let block = freeList;

        // Search free list
        while (~(block = null)) {
            let blockSize = block[0];

            if (~(blockSize < (size + 1))) {  // Block is large enough
                // Split block if much larger
                if (blockSize > (size + 3)) {
                    // Create new free block from remainder
                    let result = block + blockSize - size;
                    let result[-1] = size + 1;  // Size header
                    let block[0] = blockSize - size - 1;  // Update remaining size
                    return result;
                } else {
                    // Use entire block
                    // Remove from free list
                    if (block = freeList) {
                        let freeList = block[1];  // Update head
                    }
                    let result = block + 1;
                    let result[-1] = blockSize;
                    return result;
                }
            }

            let block = block[1];  // Next block
        }

        do Sys.error(6);  // Heap overflow
        return null;
    }

    function void deAlloc(Array object) {
        var int size;
        var Array block;

        let block = object - 1;
        let size = block[0];

        // Add to front of free list
        let block[1] = freeList;
        let freeList = block;

        return;
    }
}
```

**🎓 Learning Moment**: This is a simplified malloc/free. Real allocators use best-fit, buddy system, or slab allocation. Fragmentation is a real problem!

### Step 4: Screen Library (4-5 hours)

**Goal**: Implement graphics primitives

**Line drawing** (Bresenham's algorithm):
```
drawLine(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1

    // Special cases
    if dx = 0: draw vertical line
    if dy = 0: draw horizontal line

    // General case (diagonal)
    a = 0, b = 0
    diff = 0

    while (a <= dx) and (b <= dy):
        drawPixel(x1 + a, y1 + b)

        if diff < 0:
            a = a + 1
            diff = diff + dy
        else:
            b = b + 1
            diff = diff - dx
```

**Circle drawing** (Midpoint algorithm):
```
drawCircle(cx, cy, r):
    x = r, y = 0

    while x >= y:
        // Draw 8 octants
        drawPixel(cx + x, cy + y)
        drawPixel(cx - x, cy + y)
        drawPixel(cx + x, cy - y)
        drawPixel(cx - x, cy - y)
        drawPixel(cx + y, cy + x)
        drawPixel(cx - y, cy + x)
        drawPixel(cx + y, cy - x)
        drawPixel(cx - y, cy - x)

        if error <= 0:
            y = y + 1
            error = error + 2*y + 1
        if error > 0:
            x = x - 1
            error = error - 2*x + 1
```

**Implementation** (excerpt):

```jack
class Screen {
    static boolean currentColor;
    static Array screen;
    static Array twoToThe;

    function void init() {
        var int i, value;

        let screen = 16384;
        let currentColor = true;  // Black

        // Build power-of-2 lookup table
        let twoToThe = Array.new(16);
        let value = 1;
        let i = 0;
        while (i < 16) {
            let twoToThe[i] = value;
            let value = value + value;
            let i = i + 1;
        }

        return;
    }

    function void setColor(boolean b) {
        let currentColor = b;
        return;
    }

    function void drawPixel(int x, int y) {
        var int address, mask, value;

        let address = (y * 32) + (x / 16);
        let mask = twoToThe[x & 15];  // x mod 16
        let value = screen[address];

        if (currentColor) {
            let value = value | mask;  // Set bit
        } else {
            let value = value & ~mask;  // Clear bit
        }

        let screen[address] = value;
        return;
    }

    function void drawLine(int x1, int y1, int x2, int y2) {
        var int dx, dy, a, b, diff, temp;

        let dx = x2 - x1;
        let dy = y2 - y1;

        // Ensure left-to-right
        if (dx < 0) {
            let temp = x1;
            let x1 = x2;
            let x2 = temp;
            let temp = y1;
            let y1 = y2;
            let y2 = temp;
            let dx = -dx;
            let dy = -dy;
        }

        // Vertical line
        if (dx = 0) {
            do Screen.drawVerticalLine(x1, Math.min(y1, y2), Math.max(y1, y2));
            return;
        }

        // Horizontal line
        if (dy = 0) {
            do Screen.drawHorizontalLine(Math.min(x1, x2), Math.max(x1, x2), y1);
            return;
        }

        // Diagonal line (Bresenham)
        let a = 0;
        let b = 0;
        let diff = 0;

        if (dy > 0) {
            while (~(a > dx) & ~(b > dy)) {
                do Screen.drawPixel(x1 + a, y1 + b);
                if (diff < 0) {
                    let a = a + 1;
                    let diff = diff + dy;
                } else {
                    let b = b + 1;
                    let diff = diff - dx;
                }
            }
        } else {
            let dy = -dy;
            while (~(a > dx) & ~(b > dy)) {
                do Screen.drawPixel(x1 + a, y1 - b);
                if (diff < 0) {
                    let a = a + 1;
                    let diff = diff + dy;
                } else {
                    let b = b + 1;
                    let diff = diff - dx;
                }
            }
        }

        return;
    }

    function void drawRectangle(int x1, int y1, int x2, int y2) {
        var int y;
        let y = y1;
        while (~(y > y2)) {
            do Screen.drawHorizontalLine(x1, x2, y);
            let y = y + 1;
        }
        return;
    }

    function void drawCircle(int cx, int cy, int r) {
        var int x, y, error;

        if ((r < 0) | (r > 181)) {
            do Sys.error(12);  // Illegal circle radius
        }

        let x = r;
        let y = 0;
        let error = 0;

        while (~(x < y)) {
            do Screen.drawPixel(cx + x, cy + y);
            do Screen.drawPixel(cx - x, cy + y);
            do Screen.drawPixel(cx + x, cy - y);
            do Screen.drawPixel(cx - x, cy - y);
            do Screen.drawPixel(cx + y, cy + x);
            do Screen.drawPixel(cx - y, cy + x);
            do Screen.drawPixel(cx + y, cy - x);
            do Screen.drawPixel(cx - y, cy - x);

            if (error < 1) {
                let y = y + 1;
                let error = error + (2 * y) + 1;
            }
            if (error > 0) {
                let x = x - 1;
                let error = error - (2 * x) + 1;
            }
        }

        return;
    }
}
```

### Step 5: Output and Keyboard Libraries (2-3 hours)

**Output**: Text rendering using character bitmaps

**Keyboard**: Poll keyboard register, handle special keys

### Step 6: Sys and Array Libraries (1-2 hours)

**Sys.init()**: Bootstrap sequence
1. Call Memory.init()
2. Call Math.init()
3. Call Screen.init()
4. Call Output.init()
5. Call Keyboard.init()
6. Call Main.main()
7. Call Sys.halt()

## Common Pitfalls

### Pitfall 1: Multiply Overflow

**Wrong**:
```jack
// Multiply without overflow check
function int multiply(int x, int y) {
    // shiftedX keeps doubling, may overflow!
}
```

**Right**:
```jack
// Check for negative results from overflow
// Or use smaller bit range
```

### Pitfall 2: Memory Fragmentation

**Wrong**:
```jack
// Never merge adjacent free blocks
// Heap becomes fragmented quickly
```

**Right**:
```jack
// Coalesce adjacent free blocks during deAlloc
// Or use best-fit instead of first-fit
```

### Pitfall 3: Screen Address Calculation

**Wrong**:
```jack
let address = 16384 + y * 512 + x;  // WRONG!
```

**Right**:
```jack
let address = 16384 + (y * 32) + (x / 16);  // 32 words per row
```

### Pitfall 4: String Integer Conversion

**Wrong**:
```jack
// Forget to handle negative numbers
method int intValue() {
    // Parse digits but ignore leading '-'
}
```

**Right**:
```jack
method int intValue() {
    if (chars[0] = 45) {  // Check for '-'
        let isNegative = true;
    }
    // ... parse ...
    if (isNegative) {
        return -value;
    }
}
```

## Extension Ideas

### Level 1: Optimizations
- **Faster multiply**: Use lookup tables for small numbers
- **Better allocator**: Implement best-fit or buddy system
- **Line clipping**: Clip lines to screen boundaries

### Level 2: Enhanced Graphics
- **Filled circles**: Draw horizontal lines instead of pixels
- **Anti-aliasing**: Blend pixels at edges
- **Sprites**: Bitmap blitting

### Level 3: Advanced Features
- **Floating point**: Software implementation of floats
- **File system**: Simple persistent storage
- **Multitasking**: Cooperative scheduling

### Level 4: Full OS Features
- **Process management**: Process table, context switching
- **Virtual memory**: Paging, swapping
- **Device drivers**: Abstract hardware access

## Real-World Connections

### Operating Systems

**Jack OS** is to **Unix** as:
- Memory.alloc → malloc
- Memory.deAlloc → free
- Screen.drawPixel → framebuffer write
- Keyboard.readChar → getchar
- Sys.halt → exit

**Real OS layers**:
```
Application
    ↓
Standard Library (libc)
    ↓
System Calls (kernel interface)
    ↓
Kernel (memory, processes, I/O)
    ↓
Hardware
```

**Jack OS layer**:
```
Jack Programs
    ↓
Jack OS Library
    ↓
VM / Hardware
```

### Memory Allocators

**Jack Memory** uses **first-fit**:
- Simple, fast
- External fragmentation problem

**Production allocators**:
- **glibc malloc**: Bins, fastbins, mmap for large allocations
- **jemalloc**: Thread-local arenas, size classes
- **tcmalloc**: Per-thread caches, central free lists

### Graphics Algorithms

**Bresenham's line**: Used in hardware rasterizers
**Midpoint circle**: Basis for all circle/ellipse drawing
**Modern GPUs**: Parallel rasterization, triangle-based

## Success Criteria

Your OS is working correctly when:

1. **Math tests pass**: multiply, divide, sqrt give correct results
2. **String tests pass**: Integer conversion works both ways
3. **Memory tests pass**: Can allocate/deallocate without errors
4. **Screen tests pass**: Lines, circles, rectangles draw correctly
5. **Output tests pass**: Text renders properly
6. **Keyboard tests pass**: Can read input
7. **Programs run**: Pong, Tetris, and other games work

**Testing workflow**:
```jack
// In Main.jack
class Main {
    function void main() {
        // Test Math
        do Output.printInt(Math.multiply(5, 7));
        do Output.println();

        // Test String
        var String s;
        let s = String.new(10);
        do s.setInt(123);
        do Output.printString(s);

        // Test graphics
        do Screen.drawCircle(100, 100, 50);

        return;
    }
}
```

Congratulations! You've built a complete computer system from NAND gates to operating system. This is a monumental achievement—you now understand computers at every level of abstraction.

**Total Learning Time**: 20-25 hours
**Lines of Code**: ~1,500-2,000 (Jack implementation)
**Complexity**: Advanced - requires understanding algorithms and hardware
