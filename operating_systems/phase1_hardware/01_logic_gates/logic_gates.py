def NAND(a, b):
    """The only 'primitive' gate - all others built from this"""
    result = int(not (a and b))
    return result
    

def NOT(a):
    """Feed same input to both NAND inputs"""
    result = int(NAND(a, a))
    return result

def AND(a, b):
    """AND gate is the inverse of NAND"""
    result = int(NOT(NAND(a, b)))
    return result

def OR(a, b):
    """OR gate is the combination of NOT and NAND"""
    result = int(NAND(NOT(a), NOT(b)))
    return result

def XOR(a, b):
    """XOR gate is the combination of AND, OR, and NOT"""
    result = int(OR(AND(a, NOT(b)), AND(NOT(a), b)))
    return result

def MUX(a, b, sel):
    """
    If sel=0, output=a
    If sel=1, output=b

    Logic: (NOT(sel) AND a) OR (sel AND b)
    - When sel=0: NOT(0)=1, so (1 AND a) OR (0 AND b) = a
    - When sel=1: NOT(1)=0, so (0 AND a) OR (1 AND b) = b
    """
    result = int(OR(AND(NOT(sel), a), AND(sel, b)))
    return result

def DMUX(input, sel):
    """
    If sel=0, output a gets the input, b gets 0
    If sel=1, output b gets the input, a gets 0

    Logic:
    - a = input AND NOT(sel)  # only passes when sel=0
    - b = input AND sel        # only passes when sel=1
    """
    result = int(AND(input, NOT(sel))), int(AND(input, sel))
    return result

def print_truth_table(gate_funcs: list[callable]):
    dash = "-----"

    # Header row
    print(f"| {'A':^5} | {'B':^5} | {' | '.join([f'{g.__name__:^5}' for g in gate_funcs])} |")

    # Separator row
    print(f"| {dash:^5} | {dash:^5} | {' | '.join([f'{dash:^5}' for _ in gate_funcs])} |")

    # Body rows
    for a in [0, 1]:
        for b in [0, 1]:
            print(f"| {a:^5} | {b:^5} | {' | '.join([f'{g(a, b):^5}' for g in gate_funcs])} |")

    print()

def print_mux_truth_table():
    dash = "-----"
    print(f"| {'A':^5} | {'B':^5} | {'SEL':^5} | {'MUX':^5} |")
    print(f"| {dash:^5} | {dash:^5} | {dash:^5} | {dash:^5} |")
    for a in [0, 1]:
        for b in [0, 1]:
            for sel in [0, 1]:
                print(f"| {a:^5} | {b:^5} | {sel:^5} | {MUX(a, b, sel):^5} |")
    print()

def print_dmux_truth_table():
    dash = "-----"
    print(f"| {'IN':^5} | {'SEL':^5} | {'A':^5} | {'B':^5} |")
    print(f"| {dash:^5} | {dash:^5} | {dash:^5} | {dash:^5} |")
    for input in [0, 1]:
        for sel in [0, 1]:
            print(f"| {input:^5} | {sel:^5} | {DMUX(input, sel)[0]:^5} | {DMUX(input, sel)[1]:^5} |")
    print()

if __name__ == "__main__":
    print_truth_table([NAND, AND, OR, XOR])
    print_mux_truth_table()
    print_dmux_truth_table()
