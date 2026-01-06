# Nand to Tetris: Learning Projects

A comprehensive guide to building a complete computer system from scratch, from logic gates to operating system.

## 🎯 Goal

Learn how operating systems and computers are built by **actually building one**. This project-based approach emphasizes understanding over completion—each project teaches fundamental concepts that power all modern computers.

## 📚 Project Structure

### Phase 1: Hardware Layer (Weeks 1-5)

Build a working computer from logic gates:

1. **[Logic Gate Simulator](phase1_hardware/01_logic_gates/01_logic_gates.md)** - Boolean logic and gate composition
2. **[Binary Arithmetic Calculator](phase1_hardware/02_binary_arithmetic/02_binary_arithmetic.md)** - ALU design and two's complement
3. **[Memory Hierarchy Simulator](phase1_hardware/03_memory_hierarchy/03_memory_hierarchy.md)** - Sequential logic and state
4. **[Assembly Language Emulator](phase1_hardware/04_assembly_emulator/04_assembly_emulator.md)** - Machine code and instruction sets
5. **[Complete Computer Architecture](phase1_hardware/05_computer_architecture/05_computer_architecture.md)** - Von Neumann architecture integration

**What you'll build**: A functioning 16-bit computer that executes programs!

### Phase 2: Software Layer (Weeks 6-14)

Build the software stack on top of your hardware:

6. **[Two-Tier Assembler](phase2_software/06_assembler/06_assembler.md)** - Symbol resolution and code translation
7. **[VM Part 1: Stack Arithmetic](phase2_software/07_vm_part1/07_vm_part1.md)** - Stack machines and memory segments
8. **[VM Part 2: Program Flow](phase2_software/08_vm_part2/08_vm_part2.md)** - Functions and recursion
9. **[High-Level Language Design](phase2_software/09_language_design/09_language_design.md)** - OOP language specification
10. **[Syntax Analyzer](phase2_software/10_parser/10_parser.md)** - Lexical analysis and parsing
11. **[Code Generator](phase2_software/11_code_generator/11_code_generator.md)** - Compilation and code generation
12. **[Operating System Services](phase2_software/12_operating_system/12_operating_system.md)** - System libraries and I/O

**What you'll build**: A complete toolchain from high-level language to machine code!

---

## 📖 Learning Outcomes Summary

This learning path takes you from fundamental logic gates to a complete operating system. Here's what you'll master in each project:

### Phase 1: Hardware Layer

**Project 1: Logic Gate Simulator** — You'll discover that all computation reduces to a single primitive: the NAND gate. By building every Boolean operation (NOT, AND, OR, XOR, MUX, DMUX) from this one building block, you'll understand how complexity emerges from simplicity through composition. This project reveals the fundamental insight that powers all digital computing: any computation imaginable can be expressed through combinations of these elementary gates, and they all trace back to NAND. You'll work with truth tables and Boolean algebra to see how logical operations form the atomic units of information processing, giving you a visceral understanding of why computers think in 1s and 0s.

**Project 2: Binary Arithmetic Calculator** — Building an Arithmetic Logic Unit (ALU) from gates teaches you how computers perform mathematics without "knowing" numbers as we do. You'll construct Half Adders and Full Adders to create a 16-bit Ripple Carry Adder, seeing how binary addition propagates carry bits through hardware. The Two's Complement system for representing negative numbers will reveal why computers use this seemingly strange encoding—it makes subtraction identical to addition with inverted bits. By implementing 18+ operations with control bits that select different computational paths through the same hardware, you'll understand how a single physical circuit can perform multiple operations, a key insight into how CPUs achieve versatility without physical reconfiguration.

**Project 3: Memory Hierarchy Simulator** — This project transforms your understanding of how computers remember. You'll build sequential logic using D Flip-Flops (DFF), which are the quantum leap from combinational logic—circuits that can hold state across time. By constructing registers and RAM hierarchies, you'll see how memory is organized in nested layers, from individual bits to addressable words. Implementing a Program Counter with load, increment, and reset capabilities reveals how computers track their position in executing instructions. You'll confront the fundamental tradeoff in memory design: speed versus capacity, understanding why computers use a hierarchy (registers, cache, RAM, disk) where each level trades access time for storage density. This explains why local variables are fast but limited, while databases are vast but slow.

**Project 4: Assembly Language Emulator** — You'll bridge the gap between hardware and software by implementing the fetch-decode-execute cycle—the heartbeat of every processor. Working with A-instructions (address loading) and C-instructions (computation), you'll see how a minimal instruction set can express complex programs through clever combinations. Memory-mapped I/O demystifies how computers interact with the world: the screen and keyboard aren't special cases but simply memory addresses that happen to connect to hardware. Writing assembly programs for graphics and interaction shows you the mental model programmers had before high-level languages—every operation explicit, every memory access manual. This project makes you appreciate both the elegance of machine code's simplicity and the tedium that motivated the invention of compilers.

**Project 5: Complete Computer Architecture** — Integrating the CPU, ALU, RAM, and ROM into a Von Neumann machine crystallizes your understanding of how instruction and data flow through a computer. You'll implement the stored-program concept—that programs are just data in memory—which is why computers can modify their own code and why software can exist. The Von Neumann architecture's single memory space for both instructions and data reveals why buffer overflows are possible and why Harvard architecture (separate instruction and data memory) can be more secure. Building modular components with clean interfaces teaches you that complex systems succeed through isolation and abstraction: each piece has a clear contract, and the whole emerges from their interaction. You now have a working 16-bit computer that can execute real programs.

### Phase 2: Software Layer

**Project 6: Two-Tier Assembler** — Building an assembler reveals why symbols are fundamental to programming: humans think in names, machines think in numbers. The two-pass algorithm shows you how to resolve forward references (using labels before they're defined), a pattern that appears throughout compilation. By implementing symbol tables that map variable names, labels, and special registers to memory addresses, you'll understand that programming languages are built on this translation layer—every identifier ultimately becomes a number. The assembler bridges human cognition and machine execution, teaching you that readable code and efficient code aren't at odds; they're the same code at different abstraction levels. This project demystifies what happens when you "compile" a program, showing that translation is fundamentally about resolving names to locations.

**Project 7: VM Part 1 - Stack Arithmetic** — You'll discover why stack machines dominate modern computing by implementing one yourself. The stack provides a beautifully simple computational model: push operands, execute operation, pop result. This project teaches you that virtual machines aren't just for Java and Python—they're a universal abstraction layer that decouples high-level languages from specific hardware. By implementing eight memory segments (local, argument, this, that, constant, static, temp, pointer), you'll see how logical memory spaces map to physical RAM, understanding that variables don't "live" somewhere—the compiler decides where they live. Stack arithmetic reveals why postfix notation (Reverse Polish Notation) is natural for machines even though infix is natural for humans. You'll internalize that memory isn't a flat array but a carefully organized structure where different regions serve different purposes.

**Project 8: VM Part 2 - Program Flow & Functions** — This project unveils the magic of function calls—how programs remember where to return, how local variables don't collide across function boundaries, and how recursion works without infinite memory. Building stack frames teaches you that each function call creates an isolated memory environment, explaining why local variables vanish when functions return and how recursive calls to the same function don't overwrite each other's data. The calling convention—argument passing, return address storage, frame pointer management—shows you that function calls are expensive because they require carefully preserving and restoring state. You'll understand why tail recursion optimization exists and why deep recursion can crash programs (stack overflow). Bootstrap code initialization reveals that before your program runs, something must set up the memory environment—there's a "program zero" that starts everything.

**Project 9: High-Level Language Design (Jack)** — Writing substantial programs in Jack (an object-oriented language similar to Java) teaches you to think at a higher abstraction level while remembering what's happening underneath. You'll internalize how classes organize state and behavior, how methods receive an implicit `this` pointer, and how constructors must manually allocate memory—revealing that garbage collection isn't automatic in all languages. Building data structures and games shows you that object-oriented programming maps naturally to real-world entities, but manual memory management (allocate/dispose) teaches you why memory leaks happen and why modern languages automate this burden. Working with arrays, strings, and I/O libraries makes you appreciate standard libraries—someone must implement even "basic" operations like printing or drawing. You'll see that high-level languages don't make computers slower; they make programmers faster by handling tedious bookkeeping automatically.

**Project 10: Syntax Analyzer (Compiler Frontend)** — Building a parser demystifies how compilers understand code structure. Tokenization (lexical analysis) teaches you that source code is just text until broken into meaningful units—keywords, identifiers, symbols, constants. Implementing recursive descent parsing reveals why programming language grammar rules must be carefully designed: ambiguous grammars can't be parsed efficiently. LL(1) parsing with one-token lookahead shows you that well-designed languages can be understood with minimal context, which is why some language features (like C++'s template syntax) are notoriously hard to parse. Generating parse trees makes you see code as a hierarchy of nested structures (expressions contain terms, statements contain expressions), not as linear text. This project teaches you that syntax errors aren't arbitrary—they're violations of the grammatical structure the parser expects.

**Project 11: Code Generator (Compiler Backend)** — Completing the compiler reveals how high-level abstractions map to low-level operations. Symbol tables with two-level scoping (class and subroutine) teach you why name resolution can be tricky and why shadowing (local variables hiding class fields) is possible. Converting infix expressions to postfix stack operations shows you that the recursive structure of the parser naturally produces the evaluation order machines need. Compiling object-oriented features—constructors that allocate memory, methods that receive `this` as a hidden parameter, field access through pointer arithmetic—demystifies how objects are just structured memory regions with functions that receive their address. You'll understand why method calls are more expensive than function calls and why array access requires address computation. This project closes the loop: you can now write Jack code, compile it to VM code, translate it to assembly, assemble it to machine code, and run it on the computer you built.

**Project 12: Jack Operating System** — Implementing the OS library teaches you that operating systems aren't mysterious kernel code—they're collections of services programs need. Building Math.multiply using only addition (shift-and-add algorithm) and Math.sqrt using binary search reveals that complex operations decompose into simpler ones, and that clever algorithms can do more with less. The heap allocator (Memory.alloc/deAlloc) with its free list and first-fit strategy teaches you how dynamic memory works: allocation is searching for free space, and deallocation is returning space to a pool. Screen graphics primitives using Bresenham's line algorithm and midpoint circle algorithm show you that drawing isn't magic—it's mathematical computation of which pixels to light. Text rendering with character bitmaps reveals that fonts are just data. The keyboard polling loop teaches you that input is checking a memory location until it changes. This final project makes you appreciate that every library function—from print to malloc to sqrt—is code someone wrote, and now you understand how they work at every level from algorithms to gate patterns.

---

## 🎓 Key Learning Themes

**Abstraction Layers**: Each project builds on the previous, showing how complex systems emerge from simple components. You'll see firsthand how high-level code (Jack) compiles through multiple stages to gate-level hardware.

**Two-Pass Algorithms**: Used in both the assembler (symbol resolution) and memory allocation (heap management), this fundamental pattern appears throughout systems programming.

**Stack-Based Computation**: The VM's stack architecture mirrors real systems like JVM and CPython, showing why stack machines are ubiquitous in modern computing.

**Memory Management**: From hardware registers to heap allocation, you'll understand how computers manage data at every level—critical knowledge for systems programming.

**Compilation Pipeline**: Building a complete compiler demystifies how programming languages work, showing the translation from human-readable code to executable instructions.

**Object-Oriented Design**: Jack's OOP features (classes, methods, inheritance) demonstrate how high-level abstractions map to low-level operations.

**Real-World Connections**: Every project relates to production systems—your ALU works like x86 CPUs, your VM resembles JVM/Python bytecode, your compiler follows gcc/clang patterns.

---

## 🚀 What You'll Achieve

By completing all 12 projects, you will:

1. **Understand computers completely**: From transistors to applications, no layer is a black box
2. **Build a working toolchain**: Compiler, VM translator, assembler, and computer that runs real programs
3. **Master systems programming**: Memory management, stack frames, calling conventions, and more
4. **Write a compiler**: Full frontend (lexing, parsing) and backend (code generation, optimization)
5. **Implement an OS**: Standard library with I/O, graphics, memory allocation, and system services
6. **Gain practical skills**: Assembly, C-like languages, virtual machines, and low-level programming
7. **Develop problem-solving abilities**: Each project requires breaking complex problems into manageable pieces

**Time Investment**: 100-150 hours total (15-25 hours per phase)  
**Prerequisites**: Basic programming knowledge (any language)  
**Outcome**: Deep understanding of computing from first principles

---

*Based on the Nand to Tetris course but expanded with detailed learning paths, extensive code examples, and educational context for self-paced learning.*
