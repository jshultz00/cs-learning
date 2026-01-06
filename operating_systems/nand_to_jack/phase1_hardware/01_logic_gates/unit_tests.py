import unittest
from logic_gates import *
from logic_gates_multibit import *

class TestLogicGates(unittest.TestCase):

    def test_nand(self):
        cases = [(0,0,1), (0,1,1), (1,0,1), (1,1,0)]
        for a, b, expected in cases:
            self.assertEqual(
                NAND(a, b), 
                expected, 
                msg=f"NAND({a}, {b}) expected {expected}"
            )

    def test_not(self):
        cases = [(0,1), (1,0)]
        for a, expected in cases:
            self.assertEqual(
                NOT(a), 
                expected,
                msg=f"NOT({a}) expected {expected}"
            )

    def test_and(self):
        cases = [(0,0,0), (0,1,0), (1,0,0), (1,1,1)]
        for a, b, expected in cases:
            self.assertEqual(
                AND(a, b), 
                expected,
                msg=f"AND({a}, {b}) expected {expected}"
            )

    def test_or(self):
        cases = [(0,0,0), (0,1,1), (1,0,1), (1,1,1)]
        for a, b, expected in cases:
            self.assertEqual(
                OR(a, b), 
                expected,
                msg=f"OR({a}, {b}) expected {expected}"
            )

    def test_xor(self):
        cases = [(0,0,0), (0,1,1), (1,0,1), (1,1,0)]
        for a, b, expected in cases:
            self.assertEqual(
                XOR(a, b), 
                expected,
                msg=f"XOR({a}, {b}) expected {expected}"
            )

    def test_mux(self):
        cases = [(0,0,0,0), (0,0,1,0), (0,1,0,0), (0,1,1,1), (1,0,0,1), (1,0,1,0), (1,1,0,1), (1,1,1,1)]
        for a, b, sel, expected in cases:
            self.assertEqual(
                MUX(a, b, sel), 
                expected,
                msg=f"MUX({a}, {b}, {sel}) expected {expected}"
            )

    def test_dmux(self):
        cases = [(0,0,(0,0)), (0,1,(0,0)), (1,0,(1,0)), (1,1,(0,1))]
        for input, sel, (a, b) in cases:
            self.assertEqual(
                DMUX(input, sel), 
                (a, b),
                msg=f"DMUX({input}, {sel}) expected ({a}, {b})"
            )

    def test_not16(self):
        cases = [(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1), (1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0), (0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1)]
        for a in cases:
            self.assertEqual(
                not16(a), 
                [NOT(bit) for bit in a],
                msg=f"not16({a}) expected {[NOT(bit) for bit in a]}"
            )

    def test_and16(self):
        cases = [(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1), (1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0), (0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1)]
        for a in cases:
            for b in cases:
                self.assertEqual(
                    and16(a, b), 
                    [AND(a[i], b[i]) for i in range(16)],
                    msg=f"and16({a}, {b}) expected {[AND(a[i], b[i]) for i in range(16)]}"
                )

    def test_or16(self):
        cases = [(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1), (1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0), (0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1)]
        for a in cases:
            for b in cases:
                self.assertEqual(
                    or16(a, b), 
                    [OR(a[i], b[i]) for i in range(16)],
                    msg=f"or16({a}, {b}) expected {[OR(a[i], b[i]) for i in range(16)]}"
                )

    def test_xor16(self):
        cases = [(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1), (1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0), (0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1)]
        for a in cases:
            for b in cases:
                self.assertEqual(
                    xor16(a, b), 
                    [XOR(a[i], b[i]) for i in range(16)],
                    msg=f"xor16({a}, {b}) expected {[XOR(a[i], b[i]) for i in range(16)]}"
                )

    def test_mux16(self):
        cases = [(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1), (1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0), (0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1)]
        for a in cases:
            for b in cases:
                for sel in [0, 1]:
                    self.assertEqual(
                        mux16(a, b, sel), 
                        [MUX(a[i], b[i], sel) for i in range(16)],
                        msg=f"mux16({a}, {b}, {sel}) expected {[MUX(a[i], b[i], sel) for i in range(16)]}"
                    )

    def test_dmux16(self):
        cases = [(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1), (1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0), (0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1)]
        for input in cases:
            for sel in [0, 1]:
                self.assertEqual(
                    dmux16(input, sel), 
                    [DMUX(input[i], sel) for i in range(16)],
                    msg=f"dmux16({input}, {sel}) expected {[DMUX(input[i], sel) for i in range(16)]}"
                )

if __name__ == "__main__":
    unittest.main()