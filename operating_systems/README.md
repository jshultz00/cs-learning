# Nand to Tetris: Learning Projects

A comprehensive guide to building a complete computer system from scratch, from logic gates to operating system.

## 🎯 Goal

Learn how operating systems and computers are built by **actually building one**. This project-based approach emphasizes understanding over completion—each project teaches fundamental concepts that power all modern computers.

## 📚 Project Structure

### Phase 1: Hardware Layer (Weeks 1-5)

Build a working computer from logic gates:

1. **[Logic Gate Simulator](phase1-hardware/01-logic-gates.md)** - Boolean logic and gate composition
2. **[Binary Arithmetic Calculator](phase1-hardware/02-binary-arithmetic.md)** - ALU design and two's complement
3. **[Memory Hierarchy Simulator](phase1-hardware/03-memory-hierarchy.md)** - Sequential logic and state
4. **[Assembly Language Emulator](phase1-hardware/04-assembly-emulator.md)** - Machine code and instruction sets
5. **[Complete Computer Architecture](phase1-hardware/05-computer-architecture.md)** - Von Neumann architecture integration

**What you'll build**: A functioning 16-bit computer that executes programs!

### Phase 2: Software Layer (Weeks 6-14)

Build the software stack on top of your hardware:

6. **[Two-Tier Assembler](phase2-software/06-assembler.md)** - Symbol resolution and code translation
7. **[VM Part 1: Stack Arithmetic](phase2-software/07-vm-part1.md)** - Stack machines and memory segments
8. **[VM Part 2: Program Flow](phase2-software/08-vm-part2.md)** - Functions and recursion
9. **[High-Level Language Design](phase2-software/09-language-design.md)** - OOP language specification
10. **[Syntax Analyzer](phase2-software/10-parser.md)** - Lexical analysis and parsing
11. **[Code Generator](phase2-software/11-code-generator.md)** - Compilation and code generation
12. **[Operating System Services](phase2-software/12-operating-system.md)** - System libraries and I/O

**What you'll build**: A complete toolchain from high-level language to machine code!

### Bonus Projects (Week 15+)

13. **[Optimizing Compiler](bonus/13-optimizing-compiler.md)** - Performance optimizations
14. **[Advanced OS Features](bonus/14-advanced-os.md)** - File systems, scheduling, interrupts
15. **[Full-Stack Application](bonus/15-full-stack-app.md)** - Complete game or utility

## 🚀 Getting Started

### Prerequisites

- **Programming experience**: Comfortable with at least one programming language
- **Basic math**: Binary numbers, Boolean algebra (will be taught in projects)
- **Time commitment**: 5-15 hours per week
- **Tools**: Text editor, Python/JavaScript/Rust (your choice)

### Recommended Approach

1. **Read the project overview** - Understand what you're building and why
2. **Study background concepts** - Each project starts with theory
3. **Follow the learning path** - Step-by-step instructions with time estimates
4. **Build incrementally** - Test each component before moving on
5. **Experiment and extend** - Try the extension ideas for deeper learning

### Timeline

**Fast track** (3 months): Core projects only, minimal extensions
**Standard pace** (6 months): All projects with some extensions
**Deep dive** (12 months): All projects + bonus + extensive experimentation

## 📖 How to Use These Projects

Each project file includes:

- **Background Concepts** - Theory and motivation
- **Learning Path** - Numbered steps with time estimates
- **Code Examples** - Working implementations you can follow
- **Learning Moments** (🎓) - Key insights highlighted throughout
- **What You Should Understand** - Clear learning objectives
- **Common Pitfalls** - Mistakes to avoid
- **Extension Ideas** - Ways to go deeper
- **Real-World Connections** - How this relates to actual computers

## 🎓 Educational Philosophy

This curriculum emphasizes:

- **Learning by building**: Writing code that works teaches more than reading theory
- **Bottom-up understanding**: Start with gates, end with applications
- **Incremental complexity**: Each project builds on previous work
- **Practical insight**: See how real computers work under the hood
- **Experimentation**: Extensions encourage going beyond requirements

## 🛠️ Tools and Resources

### Recommended Languages

- **Python**: Fastest for prototyping, great for beginners
- **JavaScript/TypeScript**: Easy visualization in browser
- **Rust**: Learn systems programming alongside computer architecture
- **C++**: Traditional choice for performance-critical code

### Testing Strategy

- Write comprehensive test suites for each component
- Use truth tables for gate verification
- Test edge cases (0, -1, max values, overflow)
- Build test harnesses before implementing features

### Visualization

- Consider GUI components to visualize operation
- Text-based visualizations work great too
- Seeing data flow helps internalize concepts

### Version Control

- Use Git from day one
- Commit after completing each step
- Tag major milestones (e.g., `v1.0-gates-complete`)
- Your commit history tells the story of learning

## 🌟 What Makes This Unique

Unlike traditional courses:

- **Complete system**: Build every layer from gates to OS
- **Working code**: Everything runs and produces real results
- **Deep explanations**: Understand *why* things work this way
- **Your own design**: Freedom to make architectural choices
- **Portfolio piece**: Show employers you understand computers deeply

## 📊 Progress Tracking

Create a learning journal:

```markdown
# My Nand to Tetris Journey

## Week 1: Logic Gates
- Completed: NAND, NOT, AND, OR, XOR
- Learned: Boolean algebra, gate composition
- Challenge: Understanding MUX implementation
- Next: Move to multi-bit gates

## Week 2: ...
```

## 🤝 Getting Help

When stuck:

1. **Re-read the Background Concepts** - Often the answer is there
2. **Study the code examples** - Compare your code to the patterns shown
3. **Check Common Pitfalls** - You might be hitting a known issue
4. **Simplify and test** - Break the problem into smaller pieces
5. **Draw diagrams** - Visualize the data flow

## 🎯 Success Metrics

You've succeeded when you can:

- ✅ Explain how a computer works to a non-technical person
- ✅ Read assembly code and understand what it does
- ✅ Trace a high-level program down to gates
- ✅ Debug problems at any abstraction level
- ✅ Appreciate the elegance of computer architecture
- ✅ Design new instructions or language features

## 📝 Project Status

| Project | Status | Detailed Guide |
|---------|--------|----------------|
| 1. Logic Gates | ✅ Complete | Full learning path |
| 2. Binary Arithmetic | ✅ Complete | Full learning path |
| 3. Memory Hierarchy | ✅ Complete | Full learning path |
| 4. Assembly Emulator | ✅ Complete | Full learning path |
| 5. Computer Architecture | ✅ Complete | Full learning path |
| 6. Assembler | 📝 Overview | Coming soon |
| 7. VM Part 1 | 📝 Overview | Coming soon |
| 8. VM Part 2 | 📝 Overview | Coming soon |
| 9. Language Design | 📝 Overview | Coming soon |
| 10. Parser | 📝 Overview | Coming soon |
| 11. Code Generator | 📝 Overview | Coming soon |
| 12. Operating System | 📝 Overview | Coming soon |
| 13-15. Bonus Projects | 📝 Overview | Coming soon |

**Phase 1 (Hardware) is complete with full detailed guides!** Phase 2 (Software) guides are being developed.

## 🚀 Start Your Journey

Ready to build a computer from scratch? Start with:

**[Project 1: Logic Gate Simulator →](phase1-hardware/01-logic-gates.md)**

Remember: The goal isn't speed—it's understanding. Take your time, experiment, and enjoy discovering how computers really work!

---

*Based on the Nand to Tetris course but expanded with detailed learning paths, extensive code examples, and educational context for self-paced learning.*
