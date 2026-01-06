// ===== Bootstrap: Initialize VM State =====
@256
D=A
@SP
M=D           // SP = 256

// Call Sys.init
@Sys.init$ret.bootstrap
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
A=M
M=0
@SP
M=M+1
@SP
A=M
M=0
@SP
M=M+1
@SP
A=M
M=0
@SP
M=M+1
@SP
A=M
M=0
@SP
M=M+1
@SP
D=M
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Sys.init
0;JMP
(Sys.init$ret.bootstrap)

// ===== File: Main.vm =====
// function Main.main 1
(Main.main)
@SP
A=M
M=0
@SP
M=M+1
// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop local 0
@LCL
D=M
@0
D=D+A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
// label LOOP_START
(Main.main$LOOP_START)
// push local 0
@LCL
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
// push constant 5
@5
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@TRUE_0
D;JEQ
@SP
A=M
M=0
@END_0
0;JMP
(TRUE_0)
@SP
A=M
M=-1
(END_0)
@SP
M=M+1
// if-goto LOOP_END
@SP
M=M-1
A=M
D=M
@Main.main$LOOP_END
D;JNE
// push local 0
@LCL
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
// push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=D+M
@SP
M=M+1
// pop local 0
@LCL
D=M
@0
D=D+A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
// goto LOOP_START
@Main.main$LOOP_START
0;JMP
// label LOOP_END
(Main.main$LOOP_END)
// push local 0
@LCL
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
// return
@LCL
D=M
@R13
M=D          // R13 = FRAME
@5
A=D-A        // A = FRAME - 5
D=M          // D = *(FRAME - 5)
@R14
M=D          // R14 = RET (return address)
@SP
M=M-1
A=M
D=M          // D = return value
@ARG
A=M
M=D          // *ARG = return value
@ARG
D=M+1
@SP
M=D
@R13
D=M
@1
A=D-A
D=M
@THAT
M=D
@R13
D=M
@2
A=D-A
D=M
@THIS
M=D
@R13
D=M
@3
A=D-A
D=M
@ARG
M=D
@R13
D=M
@4
A=D-A
D=M
@LCL
M=D
@R14
A=M
0;JMP

// ===== File: Sys.vm =====
// function Sys.init 0
(Sys.init)
// call Main.main 0
@Main.main$ret.0
D=A
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
D=M
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.main
0;JMP
(Main.main$ret.0)
// label SYS_HALT
(Sys.init$SYS_HALT)
// goto SYS_HALT
@Sys.init$SYS_HALT
0;JMP
