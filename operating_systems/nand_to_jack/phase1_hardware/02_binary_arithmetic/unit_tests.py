import unittest
from binary_arithmetic import *

class TestBinaryArithmetic(unittest.TestCase):

    def test_half_adder(self):
        # Test all 4 possible input combinations for half adder
        # (a, b, expected_sum, expected_carry)
        # 0 + 0 = 0, carry 0
        # 0 + 1 = 1, carry 0
        # 1 + 0 = 1, carry 0
        # 1 + 1 = 0, carry 1 (overflow to carry)
        cases = [(0,0,0,0), (0,1,1,0), (1,0,1,0), (1,1,0,1)]
        for a, b, expected_sum, expected_carry in cases:
            self.assertEqual(
                half_adder(a, b),
                (expected_sum, expected_carry),
                msg=f"half_adder({a}, {b}) expected ({expected_sum}, {expected_carry})"
            )

    def test_full_adder(self):
        # Test key cases for full adder (adds 3 bits: a, b, carry_in)
        # (a, b, carry_in, expected_sum, expected_carry)
        # 0 + 0 + 0 = 0, carry 0
        # 0 + 1 + 1 = 0, carry 1 (two 1s overflow)
        # 1 + 0 + 1 = 0, carry 1 (two 1s overflow)
        # 1 + 1 + 0 = 0, carry 1 (two 1s overflow)
        # 1 + 1 + 1 = 1, carry 1 (three 1s = 11 in binary)
        cases = [(0,0,0,0,0), (0,1,1,0,1), (1,0,1,0,1), (1,1,0,0,1), (1,1,1,1,1)]
        for a, b, carry_in, expected_sum, expected_carry in cases:
            self.assertEqual(
                full_adder(a, b, carry_in),
                (expected_sum, expected_carry),
                msg=f"full_adder({a}, {b}, {carry_in}) expected ({expected_sum}, {expected_carry})"
            )

    def test_add16(self):
        # Test case 1: 43690 + 43690 = 87380 (overflows 16-bit)
        # 43690 in binary: 1010101010101010
        # 43690 in binary: 1010101010101010
        # Result wraps to: 0101010101010100 with overflow flag 1
        self.assertEqual(
            add16([1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0], [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]),
            ([0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,0], 1),
            msg=f"add16([1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0], [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]) expected ([0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,0], 1)"
        )

        # Test case 2: 1 + 65535 = 65536 (overflows to 0)
        # 1 in binary:     0000000000000001
        # 65535 in binary: 1111111111111111 (all 1s)
        # Result:          0000000000000000 with overflow flag 1
        self.assertEqual(
            add16([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1], [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]),
            ([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 1),
            msg=f"add16([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1], [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]) expected ([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 1)"
        )

    def test_negate16(self):
        # Test case 1: Negate 43690 (two's complement)
        # Original: 1010101010101010 (43690)
        # Step 1 - Invert bits: 0101010101010101
        # Step 2 - Add 1:       0101010101010110 (21846)
        # In two's complement, this represents -43690
        self.assertEqual(
            negate16([1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]),
            ([0,1,0,1,0,1,0,1,0,1,0,1,0,1,1,0]),
            msg=f"negate16([1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]) expected ([0,1,0,1,0,1,0,1,0,1,0,1,0,1,1,0])"
        )

        # Test case 2: Negate 5 (two's complement)
        # Original: 0000000000000101 (5)
        # Step 1 - Invert bits: 1111111111111010
        # Step 2 - Add 1:       1111111111111011 (-5 in two's complement)
        self.assertEqual(
            negate16([0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]),
            ([1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1]),
            msg=f"negate16([0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]) expected ([1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1])"
        )

    def test_sub16(self):
        # Test case 1: 5 - 3 = 2
        # 5 in binary:     0000000000000101
        # -3 in binary:    1111111111111101 (two's complement)
        # 5 + (-3) = 2:    0000000000000010 (carry flag 1 in two's complement subtraction)
        self.assertEqual(
            sub16([0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]),
            ([0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0], 1),
            msg=f"sub16(5, 3) expected 2"
        )

        # Test case 2: 10 - 5 = 5
        # 10 in binary:    0000000000001010
        # -5 in binary:    1111111111111011 (two's complement)
        # 10 + (-5) = 5:   0000000000000101 (carry flag 1 in two's complement subtraction)
        self.assertEqual(
            sub16([0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]),
            ([0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1], 1),
            msg=f"sub16(10, 5) expected 5"
        )

        # Test case 3: 0 - 1 = -1 (all 1s in two's complement)
        # 0 in binary:     0000000000000000
        # -1 in binary:    1111111111111111 (two's complement)
        # 0 + (-1) = -1:   1111111111111111 (no carry in this case)
        self.assertEqual(
            sub16([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]),
            ([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], 0),
            msg=f"sub16(0, 1) expected -1 (all 1s)"
        )

    def test_alu_constant_zero(self):
        # Test ALU computing 0
        # Control bits: zx=1, nx=0, zy=1, ny=0, f=1, no=0
        # Zero both inputs, add them -> 0
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        out, zr, ng = alu(x, y, zx=1, nx=0, zy=1, ny=0, f=1, no=0)
        self.assertEqual(out, [0]*16, msg="ALU should output 0")
        self.assertTrue(zr, msg="Zero flag should be set")
        self.assertFalse(ng, msg="Negative flag should not be set")

    def test_alu_constant_one(self):
        # Test ALU computing 1
        # Control bits: zx=1, nx=1, zy=1, ny=1, f=1, no=1
        # Zero both, invert both (get -1), add (get -2), invert -> 1
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        out, zr, ng = alu(x, y, zx=1, nx=1, zy=1, ny=1, f=1, no=1)
        self.assertEqual(out, [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1], msg="ALU should output 1")
        self.assertFalse(zr, msg="Zero flag should not be set")
        self.assertFalse(ng, msg="Negative flag should not be set")

    def test_alu_constant_negative_one(self):
        # Test ALU computing -1 (all 1s)
        # Control bits: zx=1, nx=1, zy=1, ny=0, f=1, no=0
        # Zero both, invert x (get -1), add with 0 -> -1
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        out, zr, ng = alu(x, y, zx=1, nx=1, zy=1, ny=0, f=1, no=0)
        self.assertEqual(out, [1]*16, msg="ALU should output -1 (all 1s)")
        self.assertFalse(zr, msg="Zero flag should not be set")
        self.assertTrue(ng, msg="Negative flag should be set")

    def test_alu_output_x(self):
        # Test ALU outputting x
        # Control bits: zx=0, nx=0, zy=1, ny=1, f=0, no=0
        # Keep x, zero y then invert (get -1), AND x with -1 -> x
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        out, zr, ng = alu(x, y, zx=0, nx=0, zy=1, ny=1, f=0, no=0)
        self.assertEqual(out, x, msg="ALU should output x")
        self.assertFalse(zr, msg="Zero flag should not be set for 5")
        self.assertFalse(ng, msg="Negative flag should not be set for positive number")

    def test_alu_output_y(self):
        # Test ALU outputting y
        # Control bits: zx=1, nx=1, zy=0, ny=0, f=0, no=0
        # Zero x then invert (get -1), keep y, AND -1 with y -> y
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        out, zr, ng = alu(x, y, zx=1, nx=1, zy=0, ny=0, f=0, no=0)
        self.assertEqual(out, y, msg="ALU should output y")
        self.assertFalse(zr, msg="Zero flag should not be set for 3")
        self.assertFalse(ng, msg="Negative flag should not be set for positive number")

    def test_alu_not_x(self):
        # Test ALU computing !x (bitwise NOT)
        # Control bits: zx=0, nx=0, zy=1, ny=1, f=0, no=1
        # Keep x, zero y then invert (get -1), AND -> x, then NOT x
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        out, zr, ng = alu(x, y, zx=0, nx=0, zy=1, ny=1, f=0, no=1)
        expected = [1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0]  # NOT 5
        self.assertEqual(out, expected, msg="ALU should output NOT x")
        self.assertFalse(zr, msg="Zero flag should not be set")
        self.assertTrue(ng, msg="Negative flag should be set (MSB is 1)")

    def test_alu_not_y(self):
        # Test ALU computing !y (bitwise NOT)
        # Control bits: zx=1, nx=1, zy=0, ny=0, f=0, no=1
        # Zero x then invert (get -1), keep y, AND -> y, then NOT y
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        out, zr, ng = alu(x, y, zx=1, nx=1, zy=0, ny=0, f=0, no=1)
        expected = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0]  # NOT 3
        self.assertEqual(out, expected, msg="ALU should output NOT y")
        self.assertFalse(zr, msg="Zero flag should not be set")
        self.assertTrue(ng, msg="Negative flag should be set (MSB is 1)")

    def test_alu_negate_x(self):
        # Test ALU computing -x (two's complement negation)
        # Control bits: zx=0, nx=0, zy=1, ny=1, f=1, no=1
        # Keep x, zero y then invert (get -1), add x + (-1) = x-1, then NOT -> -x
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        out, zr, ng = alu(x, y, zx=0, nx=0, zy=1, ny=1, f=1, no=1)
        expected = [1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1]  # -5 in two's complement
        self.assertEqual(out, expected, msg="ALU should output -x")
        self.assertFalse(zr, msg="Zero flag should not be set")
        self.assertTrue(ng, msg="Negative flag should be set")

    def test_alu_negate_y(self):
        # Test ALU computing -y (two's complement negation)
        # Control bits: zx=1, nx=1, zy=0, ny=0, f=1, no=1
        # Zero x then invert (get -1), keep y, add (-1) + y = y-1, then NOT -> -y
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        out, zr, ng = alu(x, y, zx=1, nx=1, zy=0, ny=0, f=1, no=1)
        expected = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1]  # -3 in two's complement
        self.assertEqual(out, expected, msg="ALU should output -y")
        self.assertFalse(zr, msg="Zero flag should not be set")
        self.assertTrue(ng, msg="Negative flag should be set")

    def test_alu_x_plus_1(self):
        # Test ALU computing x + 1
        # Control bits: zx=0, nx=1, zy=1, ny=1, f=1, no=1
        # Invert x (get !x), zero y then invert (get -1), add !x + (-1) = !x - 1, NOT -> x + 1
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        out, zr, ng = alu(x, y, zx=0, nx=1, zy=1, ny=1, f=1, no=1)
        expected = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0]  # 6
        self.assertEqual(out, expected, msg="ALU should output x + 1")
        self.assertFalse(zr, msg="Zero flag should not be set")
        self.assertFalse(ng, msg="Negative flag should not be set")

    def test_alu_y_plus_1(self):
        # Test ALU computing y + 1
        # Control bits: zx=1, nx=1, zy=0, ny=1, f=1, no=1
        # Zero x then invert (get -1), invert y (get !y), add (-1) + !y = !y - 1, NOT -> y + 1
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        out, zr, ng = alu(x, y, zx=1, nx=1, zy=0, ny=1, f=1, no=1)
        expected = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0]  # 4
        self.assertEqual(out, expected, msg="ALU should output y + 1")
        self.assertFalse(zr, msg="Zero flag should not be set")
        self.assertFalse(ng, msg="Negative flag should not be set")

    def test_alu_x_minus_1(self):
        # Test ALU computing x - 1
        # Control bits: zx=0, nx=0, zy=1, ny=1, f=1, no=0
        # Keep x, zero y then invert (get -1), add x + (-1) -> x - 1
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        out, zr, ng = alu(x, y, zx=0, nx=0, zy=1, ny=1, f=1, no=0)
        expected = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0]  # 4
        self.assertEqual(out, expected, msg="ALU should output x - 1")
        self.assertFalse(zr, msg="Zero flag should not be set")
        self.assertFalse(ng, msg="Negative flag should not be set")

    def test_alu_y_minus_1(self):
        # Test ALU computing y - 1
        # Control bits: zx=1, nx=1, zy=0, ny=0, f=1, no=0
        # Zero x then invert (get -1), keep y, add (-1) + y -> y - 1
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        out, zr, ng = alu(x, y, zx=1, nx=1, zy=0, ny=0, f=1, no=0)
        expected = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0]  # 2
        self.assertEqual(out, expected, msg="ALU should output y - 1")
        self.assertFalse(zr, msg="Zero flag should not be set")
        self.assertFalse(ng, msg="Negative flag should not be set")

    def test_alu_x_plus_y(self):
        # Test ALU computing x + y
        # Control bits: zx=0, nx=0, zy=0, ny=0, f=1, no=0
        # Keep both x and y, add them
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        out, zr, ng = alu(x, y, zx=0, nx=0, zy=0, ny=0, f=1, no=0)
        expected = [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0]  # 8
        self.assertEqual(out, expected, msg="ALU should output x + y")
        self.assertFalse(zr, msg="Zero flag should not be set")
        self.assertFalse(ng, msg="Negative flag should not be set")

    def test_alu_x_minus_y(self):
        # Test ALU computing x - y
        # Control bits: zx=0, nx=1, zy=0, ny=0, f=1, no=1
        # Invert x (get !x), keep y, add !x + y, invert result
        # This gives x - y via two's complement
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        out, zr, ng = alu(x, y, zx=0, nx=1, zy=0, ny=0, f=1, no=1)
        expected = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0]  # 2
        self.assertEqual(out, expected, msg="ALU should output x - y")
        self.assertFalse(zr, msg="Zero flag should not be set")
        self.assertFalse(ng, msg="Negative flag should not be set")

    def test_alu_y_minus_x(self):
        # Test ALU computing y - x
        # Control bits: zx=0, nx=0, zy=0, ny=1, f=1, no=1
        # Keep x, invert y (get !y), add x + !y, invert result
        # This gives y - x via two's complement
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        out, zr, ng = alu(x, y, zx=0, nx=0, zy=0, ny=1, f=1, no=1)
        expected = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0]  # -2 in two's complement
        self.assertEqual(out, expected, msg="ALU should output y - x")
        self.assertFalse(zr, msg="Zero flag should not be set")
        self.assertTrue(ng, msg="Negative flag should be set")

    def test_alu_x_and_y(self):
        # Test ALU computing x & y (bitwise AND)
        # Control bits: zx=0, nx=0, zy=0, ny=0, f=0, no=0
        # Keep both x and y, AND them
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5 (binary: 0101)
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3 (binary: 0011)
        out, zr, ng = alu(x, y, zx=0, nx=0, zy=0, ny=0, f=0, no=0)
        expected = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]  # 1 (binary: 0001)
        self.assertEqual(out, expected, msg="ALU should output x & y")
        self.assertFalse(zr, msg="Zero flag should not be set")
        self.assertFalse(ng, msg="Negative flag should not be set")

    def test_alu_x_or_y(self):
        # Test ALU computing x | y (bitwise OR)
        # Control bits: zx=0, nx=1, zy=0, ny=1, f=0, no=1
        # Invert x, invert y, AND them (get !x & !y), invert result -> x | y (De Morgan's law)
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5 (binary: 0101)
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3 (binary: 0011)
        out, zr, ng = alu(x, y, zx=0, nx=1, zy=0, ny=1, f=0, no=1)
        expected = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1]  # 7 (binary: 0111)
        self.assertEqual(out, expected, msg="ALU should output x | y")
        self.assertFalse(zr, msg="Zero flag should not be set")
        self.assertFalse(ng, msg="Negative flag should not be set")

    def test_alu_zero_flag_set(self):
        # Test that zero flag is correctly set when output is 0
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        # Compute x - x = 0
        out, zr, ng = alu(x, y, zx=0, nx=1, zy=0, ny=0, f=1, no=1)
        self.assertEqual(out, [0]*16, msg="Output should be 0")
        self.assertTrue(zr, msg="Zero flag should be set when output is 0")
        self.assertFalse(ng, msg="Negative flag should not be set for 0")

    def test_alu_negative_flag_set(self):
        # Test that negative flag is set when MSB is 1
        x = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]  # 3
        y = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1]  # 5
        # Compute x - y = 3 - 5 = -2 (which has MSB = 1 in two's complement)
        out, zr, ng = alu(x, y, zx=0, nx=1, zy=0, ny=0, f=1, no=1)
        self.assertFalse(zr, msg="Zero flag should not be set")
        self.assertTrue(ng, msg="Negative flag should be set when MSB is 1")
        self.assertEqual(out[0], 1, msg="MSB (index 0) should be 1 for negative number")


if __name__ == "__main__":
    unittest.main()