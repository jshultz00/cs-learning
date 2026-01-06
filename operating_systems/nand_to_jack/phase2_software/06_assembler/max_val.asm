// Finds max value in array of 10 numbers
// Array starts at RAM[100]
// Result stored in RAM[50]

    @100        // Array base address
    D=A
    @arr
    M=D         // arr = 100

    @10         // Array length
    D=A
    @n
    M=D         // n = 10

    @arr
    A=M
    D=M
    @max
    M=D         // max = arr[0]

    @i
    M=1         // i = 1

(LOOP)
    @i
    D=M
    @n
    D=D-M
    @END
    D;JGE       // if i >= n goto END

    @arr
    D=M
    @i
    A=D+M       // A = arr + i
    D=M         // D = arr[i]

    @max
    D=D-M       // D = arr[i] - max
    @SKIP
    D;JLE       // if arr[i] <= max goto SKIP

    @arr
    D=M
    @i
    A=D+M
    D=M
    @max
    M=D         // max = arr[i]

(SKIP)
    @i
    M=M+1       // i++
    @LOOP
    0;JMP

(END)
    @max
    D=M
    @50
    M=D         // RAM[50] = max

    @END
    0;JMP