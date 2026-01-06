// Test assembly program
@2
D=A
@3
D=D+A
@0
M=D

// Loop example
(LOOP)
@counter
M=M-1
D=M
@LOOP
D;JGT

// End
(END)
@END
0;JMP
