# Systems Programming Mastery Path

This course combines:
- **CS:APP** (Computer Systems: A Programmer's Perspective) - Systems programming in C
- **OSTEP** (Operating Systems: Three Easy Pieces) - OS theory and concepts
- **xv6** (MIT 6.S081) - Hands-on OS implementation in C

Together, these resources create a unified learning experience that takes you from C fundamentals to implementing a complete operating system kernel.

---

## 🗺️ Course Structure

### **Module 1: Bits & Data Representation** (Week 1)
*Understand how computers represent and manipulate data*

**Topics:** Binary, integers, floats, two's complement, bit manipulation

**Project:**
- **Data Lab** - Bit manipulation puzzles
  - https://csapp.cs.cmu.edu/3e/labs.html

**Resources:**
- CS:APP Chapters 1-2

**Video Lectures:**
- CMU 15-213: Lectures 1-3 (Course Intro, Bits, Bytes, Integers)
  - https://www.youtube.com/playlist?list=PLbY-cFJNzq7z_tQGq-rxtq_n2QQDf5vnM

---

### **Module 2: Assembly & Machine Code** (Week 2)
*Learn how C compiles to assembly and executes on hardware*

**Topics:** x86-64 assembly, registers, instruction encoding, calling conventions

**Project:**
- **Bomb Lab** - Reverse engineering with GDB
  - https://csapp.cs.cmu.edu/3e/labs.html

**Resources:**
- CS:APP Chapter 3

**Video Lectures:**
- CMU 15-213: Lectures 4-6 (Floating Point, Machine-Level Programming)
  - https://www.youtube.com/playlist?list=PLbY-cFJNzq7z_tQGq-rxtq_n2QQDf5vnM

---

### **Module 3: Stack & Security** (Week 3)
*Understand memory layout and exploit prevention*

**Topics:** Stack frames, buffer overflow, code injection, ROP attacks

**Project:**
- **Attack Lab** - Code injection and return-oriented programming
  - https://csapp.cs.cmu.edu/3e/labs.html

**Resources:**
- CS:APP Chapter 3 (continued)

**Video Lectures:**
- CMU 15-213: Lectures 7-8 (Control Flow, Procedures, Data Structures)
  - https://www.youtube.com/playlist?list=PLbY-cFJNzq7z_tQGq-rxtq_n2QQDf5vnM

---

### **Module 4: Processor Architecture** (Week 4)
*Design and optimize a simple processor*

**Topics:** Y86-64 ISA, sequential processor, pipelining, hazards

**Project:**
- **Architecture Lab** - Y86-64 processor simulator and optimization
  - https://csapp.cs.cmu.edu/3e/labs.html

**Resources:**
- CS:APP Chapter 4

**Video Lectures:**
- CMU 15-213: Lectures 9-11 (Code Optimization, Memory Hierarchy)
  - https://www.youtube.com/playlist?list=PLbY-cFJNzq7z_tQGq-rxtq_n2QQDf5vnM

---

### **Module 5: Memory Linking & Loading** (Week 5)
*Understand program compilation and linking*

**Topics:** Object files, symbols, relocation, static/dynamic linking, libraries

**Resources:**
- CS:APP Chapter 7
- OSTEP Chapters 1-2 (OS Introduction)

**Video Lectures:**
- CMU 15-213: Lecture 13 (Linking)
  - https://www.youtube.com/playlist?list=PLbY-cFJNzq7z_tQGq-rxtq_n2QQDf5vnM
- MIT 6.S081: Lecture 1 (Introduction and Examples)
  - https://pdos.csail.mit.edu/6.828/2023/schedule.html

---

### **Module 6: Process Fundamentals** (Week 6)
*Learn process creation and basic Unix utilities*

**Topics:** Processes, fork, exec, wait, process lifecycle

**Projects:**
- **OSTEP Unix Utilities** - Build grep, zip, unzip
  - https://github.com/remzi-arpacidusseau/ostep-projects/tree/master/initial-utilities
- **xv6 Utilities Lab** - System utilities (sleep, pingpong, find, xargs)
  - https://pdos.csail.mit.edu/6.828/2023/labs/util.html

**Resources:**
- OSTEP Chapters 3-6 (Processes, Process API)
- xv6 Book Chapter 1

**Video Lectures:**
- MIT 6.S081: Lecture 2 (OS Organization)
  - https://pdos.csail.mit.edu/6.828/2023/schedule.html

---

### **Module 7: System Calls & Exceptions** (Week 7)
*Understand kernel/user mode and system call implementation*

**Topics:** Exceptional control flow, system calls, traps, interrupts, signals

**Project:**
- **xv6 System Call Lab** - Add system calls to xv6
  - https://pdos.csail.mit.edu/6.828/2023/labs/syscall.html

**Resources:**
- CS:APP Chapter 8 (Part 1)
- OSTEP Chapter 7-10 (Scheduling)
- xv6 Book Chapter 2

**Video Lectures:**
- CMU 15-213: Lecture 14 (Exceptional Control Flow)
  - https://www.youtube.com/playlist?list=PLbY-cFJNzq7z_tQGq-rxtq_n2QQDf5vnM
- MIT 6.S081: Lectures 3-4 (System Calls, Page Tables)
  - https://pdos.csail.mit.edu/6.828/2023/schedule.html

---

### **Module 8: Trap Handling** (Week 8)
*Deep dive into interrupt and trap mechanisms*

**Topics:** Trap frames, kernel entry/exit, interrupt vectors, timer interrupts

**Project:**
- **xv6 Traps Lab** - Implement trap handling features
  - https://pdos.csail.mit.edu/6.828/2023/labs/traps.html

**Resources:**
- xv6 Book Chapter 5

**Video Lectures:**
- MIT 6.S081: Lecture 5 (Isolation & System Call Entry/Exit)
  - https://pdos.csail.mit.edu/6.828/2023/schedule.html

---

### **Module 9: Shell & Job Control** (Week 9)
*Build a Unix shell with advanced features*

**Topics:** Job control, signals, foreground/background jobs, pipelines

**Projects:**
- **Shell Lab** - Unix shell with job control
  - https://csapp.cs.cmu.edu/3e/labs.html
- **OSTEP Shell Project** - Unix shell implementation
  - https://github.com/remzi-arpacidusseau/ostep-projects/tree/master/processes-shell

**Resources:**
- CS:APP Chapter 8 (Part 2)

**Video Lectures:**
- CMU 15-213: Lecture 14 (continued)
  - https://www.youtube.com/playlist?list=PLbY-cFJNzq7z_tQGq-rxtq_n2QQDf5vnM

---

### **Module 10: Cache Memory** (Week 10)
*Master cache hierarchy and optimization techniques*

**Topics:** Cache organization, locality, cache policies, matrix optimization

**Projects:**
- **Cache Lab** - Cache simulator and transpose optimization
  - https://csapp.cs.cmu.edu/3e/labs.html
- **Performance Lab** - Code optimization for memory hierarchy
  - https://csapp.cs.cmu.edu/3e/labs.html

**Resources:**
- CS:APP Chapter 6

**Video Lectures:**
- CMU 15-213: Lecture 12 (Cache Memories)
  - https://www.youtube.com/playlist?list=PLbY-cFJNzq7z_tQGq-rxtq_n2QQDf5vnM

---

### **Module 11: Virtual Memory Basics** (Week 11)
*Understand address translation and page tables*

**Topics:** Virtual addressing, page tables, TLB, address translation

**Project:**
- **xv6 Page Tables Lab** - Implement page table features
  - https://pdos.csail.mit.edu/6.828/2023/labs/pgtbl.html

**Resources:**
- CS:APP Chapter 9 (Part 1)
- OSTEP Chapters 13-16 (Address Spaces, Address Translation)
- xv6 Book Chapter 3

**Video Lectures:**
- CMU 15-213: Lectures 15-16 (Virtual Memory: Concepts, Systems)
  - https://www.youtube.com/playlist?list=PLbY-cFJNzq7z_tQGq-rxtq_n2QQDf5vnM
- MIT 6.S081: Lecture 6 (Page Tables)
  - https://pdos.csail.mit.edu/6.828/2023/schedule.html

---

### **Module 12: Page Faults & Lazy Allocation** (Week 12)
*Implement demand paging and optimization techniques*

**Topics:** Page faults, demand paging, lazy allocation, swapping

**Project:**
- **xv6 Lazy Allocation Lab** - Implement lazy page allocation
  - https://pdos.csail.mit.edu/6.828/2023/labs/lazy.html

**Resources:**
- OSTEP Chapters 17-20 (Paging, TLB, Advanced Page Tables)

**Video Lectures:**
- MIT 6.S081: Lecture 7 (Page Faults)
  - https://pdos.csail.mit.edu/6.828/2023/schedule.html

---

### **Module 13: Copy-on-Write** (Week 13)
*Optimize fork with copy-on-write semantics*

**Topics:** COW fork, reference counting, memory optimization

**Project:**
- **xv6 Copy-on-Write Lab** - Implement COW fork
  - https://pdos.csail.mit.edu/6.828/2023/labs/cow.html

**Resources:**
- OSTEP Chapters 21-22 (Swapping Mechanisms, Policies)

**Video Lectures:**
- MIT 6.S081: Lecture 8 (Interrupts)
  - https://pdos.csail.mit.edu/6.828/2023/schedule.html

---

### **Module 14: Page Replacement Algorithms** (Week 14)
*Implement and compare paging policies*

**Topics:** FIFO, LRU, Clock algorithm, working sets, thrashing

**Project:**
- **OSTEP VM Paging** - Page replacement simulator
  - https://github.com/remzi-arpacidusseau/ostep-projects/tree/master/vm-paging

**Resources:**
- OSTEP Chapters 23-24 (Complete Virtual Memory)

**Video Lectures:**
- CMU 15-213: Lecture 17 (Virtual Memory: Systems)
  - https://www.youtube.com/playlist?list=PLbY-cFJNzq7z_tQGq-rxtq_n2QQDf5vnM

---

### **Module 15: Dynamic Memory Allocation** (Week 15-16)
*Build a production-quality malloc*

**Topics:** Free lists, coalescing, splitting, allocator design patterns

**Project:**
- **Malloc Lab** - Dynamic memory allocator
  - https://csapp.cs.cmu.edu/3e/labs.html

**Resources:**
- CS:APP Chapter 9 (Part 2)

**Video Lectures:**
- CMU 15-213: Lecture 18 (Dynamic Memory Allocation)
  - https://www.youtube.com/playlist?list=PLbY-cFJNzq7z_tQGq-rxtq_n2QQDf5vnM

---

### **Module 16: Thread Fundamentals** (Week 17)
*Introduction to multithreading and parallelism*

**Topics:** Thread creation, context switching, user-level threads

**Project:**
- **xv6 Multithreading Lab** - Implement user-level threads
  - https://pdos.csail.mit.edu/6.828/2023/labs/thread.html

**Resources:**
- OSTEP Chapters 26-27 (Concurrency, Thread API)
- xv6 Book Chapter 7

**Video Lectures:**
- MIT 6.S081: Lectures 9-10 (Multiprocessors, Locks)
  - https://pdos.csail.mit.edu/6.828/2023/schedule.html

---

### **Module 17: Locks & Synchronization** (Week 18)
*Master synchronization primitives*

**Topics:** Locks, spinlocks, mutexes, deadlock prevention

**Project:**
- **xv6 Locks Lab** - Implement and optimize locks
  - https://pdos.csail.mit.edu/6.828/2023/labs/lock.html

**Resources:**
- OSTEP Chapters 28-32 (Locks, Condition Variables, Semaphores, Deadlock)

**Video Lectures:**
- MIT 6.S081: Lectures 11-12 (Thread Switching, Sleep & Wakeup)
  - https://pdos.csail.mit.edu/6.828/2023/schedule.html

---

### **Module 18: Concurrent Programming Patterns** (Week 19)
*Apply parallelism to real-world problems*

**Topics:** Producer-consumer, thread pools, parallel algorithms

**Projects:**
- **OSTEP Parallel Zip** - Parallel compression
  - https://github.com/remzi-arpacidusseau/ostep-projects/tree/master/concurrency-pzip
- **OSTEP MapReduce** - Parallel MapReduce framework
  - https://github.com/remzi-arpacidusseau/ostep-projects/tree/master/concurrency-mapreduce

**Resources:**
- OSTEP Chapters 33-34 (Event-based Concurrency, Summary)

**Video Lectures:**
- CMU 15-213: Lectures 19-20 (System-Level I/O, Network Programming)
  - https://www.youtube.com/playlist?list=PLbY-cFJNzq7z_tQGq-rxtq_n2QQDf5vnM

---

### **Module 19: Network Servers** (Week 20)
*Build concurrent network applications*

**Topics:** Sockets, network I/O, concurrent servers, HTTP

**Projects:**
- **Proxy Lab** - Concurrent web proxy with caching
  - https://csapp.cs.cmu.edu/3e/labs.html
- **OSTEP Web Server** - Concurrent HTTP server
  - https://github.com/remzi-arpacidusseau/ostep-projects/tree/master/concurrency-webserver

**Resources:**
- CS:APP Chapter 11-12 (Network Programming, Concurrent Programming)

**Video Lectures:**
- CMU 15-213: Lectures 21-22 (Concurrent Programming, Parallelism)
  - https://www.youtube.com/playlist?list=PLbY-cFJNzq7z_tQGq-rxtq_n2QQDf5vnM

---

### **Module 20: File System Basics** (Week 21)
*Understand file system design and implementation*

**Topics:** Inodes, directories, file operations, disk layout

**Project:**
- **xv6 File System Lab** - Implement large files
  - https://pdos.csail.mit.edu/6.828/2023/labs/fs.html

**Resources:**
- OSTEP Chapters 35-39 (File System Implementation)
- xv6 Book Chapter 6

**Video Lectures:**
- MIT 6.S081: Lectures 13-14 (File Systems, Crash Recovery)
  - https://pdos.csail.mit.edu/6.828/2023/schedule.html

---

### **Module 21: Crash Consistency** (Week 22)
*Ensure file system reliability*

**Topics:** Crash recovery, journaling, fsck, consistency protocols

**Project:**
- **OSTEP File System Checker** - Build fsck utility
  - https://github.com/remzi-arpacidusseau/ostep-projects/tree/master/filesystems-checker

**Resources:**
- OSTEP Chapters 40-42 (Crash Consistency, Journaling, Log-Structured FS)

**Video Lectures:**
- MIT 6.S081: Lectures 15-16 (Crash Recovery, Logging)
  - https://pdos.csail.mit.edu/6.828/2023/schedule.html

---

### **Module 22: Advanced File Systems** (Week 23)
*Modern file system features*

**Topics:** Memory-mapped files, symbolic links, file system optimizations

**Project:**
- **xv6 mmap Lab** - Implement memory-mapped files
  - https://pdos.csail.mit.edu/6.828/2023/labs/mmap.html

**Resources:**
- OSTEP Chapters 43-44 (Data Integrity, Distributed Systems)
- xv6 Book Chapter 8

**Video Lectures:**
- MIT 6.S081: Lecture 17 (Virtual Machines)
  - https://pdos.csail.mit.edu/6.828/2023/schedule.html

---

### **Module 23: Networking Stack** (Week 24)
*Build a network stack from scratch*

**Topics:** TCP/IP, sockets, packet processing, network drivers

**Project:**
- **xv6 Network Lab** - Implement network driver and sockets
  - https://pdos.csail.mit.edu/6.828/2023/labs/net.html

**Resources:**
- OSTEP Chapters 45-48 (Distributed Systems)

**Video Lectures:**
- MIT 6.S081: Lecture 18 (OS Organization)
  - https://pdos.csail.mit.edu/6.828/2023/schedule.html

---

### **Module 24: Advanced Topics** (Weeks 25-26)
*Explore cutting-edge OS concepts*

**Topics:** Virtual machines, security, RCU, multi-core optimization

**Project:**
- **Capstone Project** - Design and implement your own OS extension
  - Options: Device driver, scheduler policy, file system feature, security mechanism

**Resources:**
- OSTEP Chapters 49-52 (Security, Advanced Topics)
- Linux kernel documentation

**Video Lectures:**
- MIT 6.S081: Lectures 19-23 (Kernels & HLL, RCU, Networking, Meltdown, Final Lecture)
  - https://pdos.csail.mit.edu/6.828/2023/schedule.html
- CMU 15-213: Lectures 23-24 (Thread-Level Parallelism)
  - https://www.youtube.com/playlist?list=PLbY-cFJNzq7z_tQGq-rxtq_n2QQDf5vnM

---

## 📖 Required Resources

### **Books & Textbooks**
- **CS:APP** - "Computer Systems: A Programmer's Perspective" (3rd Edition)
  - Purchase or university library
  - Labs: https://csapp.cs.cmu.edu/3e/labs.html

- **OSTEP** - "Operating Systems: Three Easy Pieces"
  - **FREE online:** https://pages.cs.wisc.edu/~remzi/OSTEP/
  - Projects: https://github.com/remzi-arpacidusseau/ostep-projects

- **xv6 Book** - "xv6: A Simple, Unix-like Teaching Operating System"
  - **FREE online:** https://pdos.csail.mit.edu/6.828/2023/xv6/book-riscv-rev3.pdf
  - Course: https://pdos.csail.mit.edu/6.828/

### **Software Requirements**
- C compiler (GCC or Clang)
- Debugger (GDB)
- Build tools (Make, CMake)
- QEMU emulator (for xv6)
- RISC-V toolchain

---

## 🎓 Learning Objectives

By completing this course, you will:

### **Technical Skills**
- ✅ Master C programming at expert level
- ✅ Understand computer architecture deeply
- ✅ Implement core OS components (scheduler, memory manager, file system)
- ✅ Write thread-safe concurrent programs
- ✅ Debug complex systems issues
- ✅ Optimize code for performance

### **Conceptual Understanding**
- ✅ How programs execute from compilation to hardware
- ✅ Virtual memory and address translation
- ✅ Process isolation and protection
- ✅ Synchronization primitives and concurrency patterns
- ✅ File system design trade-offs
- ✅ System call interface and kernel design

### **Practical Experience**
- ✅ Built Unix shell with job control
- ✅ Implemented production memory allocator
- ✅ Created thread scheduler and synchronization primitives
- ✅ Extended xv6 kernel with new features
- ✅ Designed and implemented file system
- ✅ Built network stack basics

---

## 🚀 Getting Started

**Set up development environment:**
```bash
# Install required tools (macOS example)
brew install gcc gdb make qemu

# Verify installations
gcc --version
gdb --version
make --version
qemu-system-riscv64 --version
```

---

## 🔍 Additional Resources

**Online Courses:**
- MIT 6.S081 video lectures
- CMU 15-213 video lectures (CS:APP)

**Books:**
- "The C Programming Language" (K&R) - reference
- "Linux Kernel Development" - after xv6
- "The Linux Programming Interface" - system programming

---

## 🎓 What's Next?

After completing this course, you'll be ready for:

- **Advanced OS topics:** Distributed systems, real-time OS, embedded systems
- **Kernel development:** Contributing to Linux, FreeBSD, or other kernels
- **Systems programming roles:** Operating systems, databases, compilers, networking
- **Graduate school:** MS/PhD in Computer Systems
- **Research:** Systems research at top universities or labs
