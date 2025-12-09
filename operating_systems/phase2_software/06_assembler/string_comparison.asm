// Compare strings at RAM[100] and RAM[200]
// Result: RAM[50] = -1 (str1 < str2), 0 (equal), 1 (str1 > str2)

    @100
    D=A
    @str1
    M=D         // str1 = 100

    @200
    D=A
    @str2
    M=D         // str2 = 200

    @i
    M=0         // i = 0

(LOOP)
    @str1
    D=M
    @i
    A=D+M
    D=M
    @char1
    M=D         // char1 = str1[i]

    @str2
    D=M
    @i
    A=D+M
    D=M
    @char2
    M=D         // char2 = str2[i]

    @char1
    D=M
    @LESS
    D;JEQ       // if char1 == 0, str1 ended first

    @char2
    D=M
    @GREATER
    D;JEQ       // if char2 == 0, str2 ended first

    @char1
    D=M
    @char2
    D=D-M       // D = char1 - char2
    @LESS
    D;JLT       // if char1 < char2
    @GREATER
    D;JGT       // if char1 > char2

    @i
    M=M+1       // i++
    @LOOP
    0;JMP

(LESS)
    @50
    M=-1        // result = -1
    @END
    0;JMP

(GREATER)
    @50
    M=1         // result = 1
    @END
    0;JMP

(EQUAL)
    @50
    M=0         // result = 0

(END)
    @END
    0;JMP