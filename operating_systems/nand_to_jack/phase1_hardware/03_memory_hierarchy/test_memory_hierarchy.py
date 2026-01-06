import unittest
from memory_hierarchy import *

# -----------------------------------------------------------
#  DFF
# -----------------------------------------------------------

class TestDFF(unittest.TestCase):
    def test_basic_behavior(self):
        d = DFF()

        # Initial
        self.assertEqual(d.state, 0)
        self.assertEqual(d.clock_cycle(1), 0)

        # State change
        self.assertEqual(d.clock_cycle(0), 1)
        self.assertEqual(d.clock_cycle(1), 0)

    def test_sequence(self):
        d = DFF()
        sequence = [1,1,0,1,0]
        expected = [0,1,1,0,1]
        for inp, exp in zip(sequence, expected):
            self.assertEqual(d.clock_cycle(inp), exp)


# -----------------------------------------------------------
#  Bit (1-bit register)
# -----------------------------------------------------------

class TestBit(unittest.TestCase):
    def setUp(self):
        self.b = Bit()

    def test_load_and_hold(self):
        # Write 1
        self.assertEqual(self.b.clock_cycle(1, load=1), 0)
        # Hold
        self.assertEqual(self.b.clock_cycle(0, load=0), 1)
        # Overwrite with 0
        self.assertEqual(self.b.clock_cycle(0, load=1), 1)
        self.assertEqual(self.b.clock_cycle(0, load=0), 0)

    def test_multiple_writes(self):
        b = self.b
        writes = [1,0,1,1,0]
        expected = [0,1,0,1,1]
        for inp, exp in zip(writes, expected):
            self.assertEqual(b.clock_cycle(inp, load=1), exp)


# -----------------------------------------------------------
#  16-bit Register
# -----------------------------------------------------------

class TestRegister(unittest.TestCase):
    def setUp(self):
        self.reg = Register()

    def test_write_and_read(self):
        value = 0x1234
        bits = int_to_bits(value)

        # First cycle outputs previous content
        out = self.reg.clock_cycle(bits, load=1)
        self.assertEqual(bits_to_int(out), 0)

        # Second cycle returns stored value
        out = self.reg.clock_cycle([0]*16, load=0)
        self.assertEqual(bits_to_int(out), value)

    def test_persistence(self):
        val = int_to_bits(0xABCD)
        self.reg.clock_cycle(val, load=1)
        for _ in range(10):
            out = self.reg.clock_cycle([0]*16, load=0)
            self.assertEqual(out, val)

    def test_overwrite(self):
        v1 = int_to_bits(0x1111)
        v2 = int_to_bits(0x2222)
        self.reg.clock_cycle(v1, load=1)
        self.reg.clock_cycle([0]*16, load=0)
        self.reg.clock_cycle(v2, load=1)
        out = self.reg.clock_cycle([0]*16, load=0)
        self.assertEqual(out, v2)


# -----------------------------------------------------------
#  RAM8
# -----------------------------------------------------------

class TestRAM8(unittest.TestCase):
    def setUp(self):
        self.ram = RAM8()

    def test_write_read(self):
        for addr in range(8):
            value = int_to_bits(addr + 10)
            # Write
            self.ram.clock_cycle(value, addr, load=1)
            # Readback
            out = self.ram.clock_cycle([0]*16, addr, load=0)
            self.assertEqual(out, value)

    def test_isolation(self):
        # Write different values to each address
        values = [int_to_bits(i * 7) for i in range(8)]
        for addr, bits in enumerate(values):
            self.ram.clock_cycle(bits, addr, 1)

        # Read back
        for addr, bits in enumerate(values):
            out = self.ram.clock_cycle([0]*16, addr, 0)
            self.assertEqual(out, bits)


# -----------------------------------------------------------
#  RAM64
# -----------------------------------------------------------

class TestRAM64(unittest.TestCase):
    def setUp(self):
        self.ram = RAM64()

    def test_write_read(self):
        # Write 8 values spread across different banks+registers
        for addr in [0, 7, 8, 15, 32, 45, 63]:
            bits = int_to_bits(addr + 100)
            self.ram.clock_cycle(bits, addr, load=1)
            out = self.ram.clock_cycle([0]*16, addr, load=0)
            self.assertEqual(out, bits)

    def test_address_decoding(self):
        # Write to one address only
        target_addr = 37
        value = int_to_bits(0xBEEF)
        self.ram.clock_cycle(value, target_addr, load=1)

        # Make sure nothing else changed
        for addr in range(64):
            out = self.ram.clock_cycle([0]*16, addr, load=0)
            if addr == target_addr:
                self.assertEqual(out, value)
            else:
                self.assertEqual(out, [0]*16)

    def test_overwrite(self):
        addr = 23
        first = int_to_bits(0xAAAA)
        second = int_to_bits(0x1234)

        self.ram.clock_cycle(first, addr, 1)
        self.ram.clock_cycle([0]*16, addr, 0)
        self.ram.clock_cycle(second, addr, 1)
        out = self.ram.clock_cycle([0]*16, addr, 0)
        self.assertEqual(out, second)


# -----------------------------------------------------------
#  RAM512
# -----------------------------------------------------------

class TestRAM512(unittest.TestCase):
    def setUp(self):
        self.ram = RAM512()

    def test_write_read(self):
        """Write/read across widely spaced addresses to test all banks."""
        test_addrs = [
            0,        # bank 0, reg 0
            7,        # bank 0, reg 7
            8,        # bank 1, reg 0
            63,       # bank 1, reg 55
            64,       # bank 2, reg 0
            129,      # bank 4, reg 1
            255,      # bank 3, reg 63
            511       # bank 7, reg 63
        ]

        for addr in test_addrs:
            bits = int_to_bits(addr + 1000)  # unique pattern
            self.ram.clock_cycle(bits, addr, load=1)
            out = self.ram.clock_cycle([0]*16, addr, load=0)
            self.assertEqual(out, bits)

    def test_address_decoding(self):
        """Verify that writing to one address affects no others."""
        target_addr = 347  # random address inside RAM512
        value = int_to_bits(0xBEEF)

        # Write once
        self.ram.clock_cycle(value, target_addr, load=1)

        # Verify only that address holds the data
        for addr in range(512):
            out = self.ram.clock_cycle([0]*16, addr, load=0)
            if addr == target_addr:
                self.assertEqual(out, value)
            else:
                self.assertEqual(out, [0]*16)

    def test_overwrite(self):
        """Verify writing twice overwrites previous value at same address."""
        addr = 123
        first = int_to_bits(0xAAAA)
        second = int_to_bits(0x1234)

        # First write
        self.ram.clock_cycle(first, addr, load=1)
        self.ram.clock_cycle([0]*16, addr, load=0)

        # Overwrite
        self.ram.clock_cycle(second, addr, load=1)
        out = self.ram.clock_cycle([0]*16, addr, load=0)

        self.assertEqual(out, second)


# -----------------------------------------------------------
#  DirectMappedCache
# -----------------------------------------------------------

class TestDirectMappedCache(unittest.TestCase):
    def setUp(self):
        """Create a small cache and memory for testing"""
        # Small cache: 8 lines, 16 bytes per line
        self.cache = DirectMappedCache(num_lines=8, line_size=16)
        # Simple memory: 1024 bytes filled with values = address % 256
        self.memory = [i % 256 for i in range(1024)]

    def test_cache_hit_and_miss(self):
        """Test basic cache hit and miss behavior"""
        # First access - cold miss
        value, hit = self.cache.access(0, self.memory)
        self.assertFalse(hit)
        self.assertEqual(value, 0)

        # Second access to same address - hit
        value, hit = self.cache.access(0, self.memory)
        self.assertTrue(hit)
        self.assertEqual(value, 0)

    def test_spatial_locality(self):
        """Cache line loads 16 bytes at once, exploiting spatial locality"""
        # Access address 0 - loads cache line with addresses 0-15
        self.cache.access(0, self.memory)

        # Access nearby addresses (same cache line) - should hit
        value, hit = self.cache.access(5, self.memory)
        self.assertTrue(hit)
        self.assertEqual(value, 5)

        value, hit = self.cache.access(15, self.memory)
        self.assertTrue(hit)

        # Access address 16 (next cache line) - should miss
        value, hit = self.cache.access(16, self.memory)
        self.assertFalse(hit)

    def test_conflict_miss(self):
        """Addresses mapping to same cache line cause conflict evictions"""
        # Address 0 and 128 both map to cache line 0
        self.cache.access(0, self.memory)
        self.cache.access(0, self.memory)  # hit

        # Load address 128 - evicts address 0's cache line
        self.cache.access(128, self.memory)

        # Access 0 again - miss (was evicted)
        value, hit = self.cache.access(0, self.memory)
        self.assertFalse(hit)

    def test_sequential_access_pattern(self):
        """Sequential access benefits from spatial locality"""
        # Access 32 sequential bytes (2 cache lines)
        hits = 0
        misses = 0

        for addr in range(32):
            value, hit = self.cache.access(addr, self.memory)
            if hit:
                hits += 1
            else:
                misses += 1

        # Only 2 misses (one per cache line), rest are hits
        self.assertEqual(misses, 2)
        self.assertEqual(hits, 30)


# -----------------------------------------------------------
#  FullyAssociativeCache
# -----------------------------------------------------------

class TestFullyAssociativeCache(unittest.TestCase):
    def setUp(self):
        """Create a small cache and memory for testing"""
        # Small cache: 8 lines, 16 bytes per line
        self.cache = FullyAssociativeCache(num_lines=8, line_size=16)
        # Simple memory: 1024 bytes filled with values = address % 256
        self.memory = [i % 256 for i in range(1024)]

    def test_no_conflict_misses(self):
        """Addresses that would conflict in direct-mapped can coexist"""
        # In direct-mapped with 8 lines, addresses 0 and 128 would conflict
        # (both map to line 0). In fully associative, they can both stay.

        # Load address 0
        self.cache.access(0, self.memory)

        # Load address 128
        self.cache.access(128, self.memory)

        # Access 0 again - should HIT (not evicted!)
        value, hit = self.cache.access(0, self.memory)
        self.assertTrue(hit)
        self.assertEqual(value, 0)

        # Access 128 again - should also HIT
        value, hit = self.cache.access(128, self.memory)
        self.assertTrue(hit)
        self.assertEqual(value, 128)

        # Total: 2 misses (initial loads), 2 hits
        self.assertEqual(self.cache.misses, 2)
        self.assertEqual(self.cache.hits, 2)

    def test_lru_replacement(self):
        """LRU replacement evicts least recently used line"""
        # Cache has 4 lines - fill it completely then add a 5th
        cache = FullyAssociativeCache(num_lines=4, line_size=16)

        # Load 4 different cache lines (fill cache)
        cache.access(0, self.memory)    # Time 1
        cache.access(16, self.memory)   # Time 2
        cache.access(32, self.memory)   # Time 3
        cache.access(48, self.memory)   # Time 4

        # Access line 0 again (makes it most recently used)
        value, hit = cache.access(0, self.memory)
        self.assertTrue(hit)  # Time 5

        # Now load a new line (64) - should evict line 16 (LRU = time 2)
        cache.access(64, self.memory)   # Time 6, evicts 16

        # Verify line 0 is still in cache (was refreshed to time 5)
        value, hit = cache.access(0, self.memory)
        self.assertTrue(hit)  # Time 7

        # Verify line 16 was evicted (should MISS)
        value, hit = cache.access(16, self.memory)
        self.assertFalse(hit)  # MISS - was evicted
        # This loads 16 at time 8, evicting 32 (LRU = time 3)

        # Cache now has: 0 (time 7), 48 (time 4), 64 (time 6), 16 (time 8)
        # Line 32 was evicted when we reloaded 16

        # Verify line 48 is still in cache
        value, hit = cache.access(48, self.memory)
        self.assertTrue(hit)

        # Verify line 64 is still in cache
        value, hit = cache.access(64, self.memory)
        self.assertTrue(hit)


# -----------------------------------------------------------
#  Helper Functions
# -----------------------------------------------------------

class TestHelpers(unittest.TestCase):
    def test_roundtrip(self):
        for value in [0, 1, 5, 255, 4096, 65535]:
            bits = int_to_bits(value)
            self.assertEqual(bits_to_int(bits), value)

    def test_out_of_range(self):
        with self.assertRaises(ValueError):
            int_to_bits(-1)
        with self.assertRaises(ValueError):
            int_to_bits(1 << 16)


if __name__ == "__main__":
    unittest.main()