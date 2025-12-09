// Computes sum = 1 + 2 + ... + 10
    @sum
    M=0         // sum = 0
    @i
    M=1         // i = 1
(LOOP)
    @i
    D=M         // D = i
    @10
    D=D-A       // D = i - 10
    @END
    D;JGT       // if (i - 10) > 0 goto END
    @i
    D=M
    @sum
    M=D+M       // sum += i
    @i
    M=M+1       // i++
    @LOOP
    0;JMP       // goto LOOP
(END)
    @END
    0;JMP       // infinite loop