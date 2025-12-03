class DFF:
    """D Flip-Flop: 1-bit memory"""
    def __init__(self):
        self.state = 0  # Current stored bit

    def clock_cycle(self, data_in):
        """On rising edge: capture input, emit old state"""
        output = self.state  # Output is PREVIOUS state
        self.state = data_in  # Store for next cycle
        return output

class Bit:
    """1-bit register with load control"""
    def __init__(self):
        self.dff = DFF()

    def clock_cycle(self, data_in, load):
        """
        If load=1: store new data
        If load=0: keep old data (feedback loop!)
        """
        current_state = self.dff.state

        # MUX: select new data or old data
        to_store = data_in if load else current_state

        return self.dff.clock_cycle(to_store)

class Register:
    """16-bit register"""
    def __init__(self):
        self.bits = [Bit() for _ in range(16)]

    def clock_cycle(self, data_in, load):
        """data_in: 16-bit value, load: single control bit"""
        return [
            self.bits[i].clock_cycle(data_in[i], load)
            for i in range(16)
        ]

class RAM8:
    """8 registers, 3-bit address"""
    def __init__(self):
        self.registers = [Register() for _ in range(8)]

    def clock_cycle(self, data_in, address, load):
        """
        address: 3 bits (0-7)
        load: write enable
        Returns: data from addressed register
        """
        # Decode address: only one register gets load=1
        outputs = []
        for i in range(8):
            reg_load = (load == 1 and address == i)
            out = self.registers[i].clock_cycle(data_in, reg_load)
            outputs.append(out)

        # Output from selected register
        return outputs[address]

class RAM64:
    """64 registers using 8x RAM8, 6-bit address"""
    def __init__(self):
        self.banks = [RAM8() for _ in range(8)]

    def clock_cycle(self, data_in, address, load):
        """
        address: 6 bits
        - High 3 bits select which RAM8 bank
        - Low 3 bits select register within bank
        """
        bank_select = address >> 3  # Top 3 bits
        register_select = address & 0b111  # Bottom 3 bits

        outputs = []
        for i in range(8):
            bank_load = (load == 1 and bank_select == i)
            out = self.banks[i].clock_cycle(
                data_in, register_select, bank_load
            )
            outputs.append(out)

        return outputs[bank_select]


class RAM512:
    """512 registers using 64x RAM64, 9-bit address"""
    def __init__(self):
        self.banks = [RAM64() for _ in range(8)]

    def clock_cycle(self, data_in, address, load):
        """
        address: 9 bits
        - High 6 bits select which RAM64 bank
        - Low 3 bits select register within bank
        """
        bank_select = address >> 6  # Top 3 bits
        ram64_address = address & 0b111111  # Bottom 6 bits

        # Route load only to selected bank
        outputs = []
        for i in range(8):
            bank_load = (load == 1 and bank_select == i)
            out = self.banks[i].clock_cycle(
                data_in, ram64_address, bank_load
            )
            outputs.append(out)

        return outputs[bank_select]


class PC:
    """Program Counter: tracks next instruction address"""
    def __init__(self):
        self.register = Register()
        self.current = [0] * 16  # Track current value

    def clock_cycle(self, data_in, load, inc, reset):
        """
        Priority: reset > load > inc > hold

        reset=1: output 0
        load=1:  output data_in
        inc=1:   output current + 1
        else:    output current (hold)
        """
        if reset:
            next_val = [0] * 16
        elif load:
            next_val = data_in
        elif inc:
            one = [1] + [0] * 15
            next_val, _ = add16(self.current, one)
        else:
            next_val = self.current

        self.current = self.register.clock_cycle(next_val, load=1)
        return self.current


class DirectMappedCache:
    """Simple direct-mapped cache"""
    def __init__(self, num_lines=256, line_size=64):
        self.num_lines = num_lines
        self.line_size = line_size
        # Each cache line: [valid, tag, data]
        self.lines = [[False, 0, [0]*line_size] for _ in range(num_lines)]
        self.hits = 0
        self.misses = 0

    def access(self, address, main_memory):
        """Access byte at address (returns data, hit/miss)"""
        # Decode address into: [tag | index | offset]
        index = (address // self.line_size) % self.num_lines
        tag = address // (self.line_size * self.num_lines)
        offset = address % self.line_size

        line_valid, line_tag, line_data = self.lines[index]

        # Check for hit
        if line_valid and line_tag == tag:
            self.hits += 1
            return line_data[offset], True  # HIT

        # Cache miss: fetch from main memory
        self.misses += 1
        base_addr = (address // self.line_size) * self.line_size
        new_data = [main_memory[base_addr + i] for i in range(self.line_size)]

        # Replace cache line
        self.lines[index] = [True, tag, new_data]
        return new_data[offset], False  # MISS

    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0


class FullyAssociativeCache:
    """Fully associative cache—any address can go anywhere"""
    def __init__(self, num_lines=256, line_size=64):
        self.num_lines = num_lines
        self.line_size = line_size
        self.lines = [[False, 0, [0]*line_size] for _ in range(num_lines)]
        self.lru_counters = [0] * num_lines  # For LRU replacement
        self.hits = 0
        self.misses = 0
        self.time = 0

    def access(self, address, main_memory):
        """Access with LRU replacement policy"""
        tag = address // self.line_size
        offset = address % self.line_size
        self.time += 1

        # Search all lines for hit (parallel in hardware)
        for i, (valid, line_tag, data) in enumerate(self.lines):
            if valid and line_tag == tag:
                self.hits += 1
                self.lru_counters[i] = self.time  # Update LRU
                return data[offset], True  # HIT

        # Miss: find victim line (LRU policy)
        self.misses += 1
        # Prefer invalid lines first, then use LRU among valid lines
        invalid_lines = [i for i in range(self.num_lines) if not self.lines[i][0]]
        if invalid_lines:
            victim = invalid_lines[0]  # Use first invalid line
        else:
            # All lines valid, use LRU
            victim = min(range(self.num_lines), key=lambda i: self.lru_counters[i])

        # Fetch cache line from memory
        base_addr = (address // self.line_size) * self.line_size
        new_data = [main_memory[base_addr + i] for i in range(self.line_size)]

        # Replace victim
        self.lines[victim] = [True, tag, new_data]
        self.lru_counters[victim] = self.time
        return new_data[offset], False  # MISS

    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0


class CacheVisualizer:
    """Visualize cache operations (supports DirectMapped and FullyAssociative)"""

    def __init__(self, cache, memory):
        self.cache = cache
        self.memory = memory
        self.access_history = []
        self.cache_type = type(cache).__name__

    def visualize_access(self, address):
        """Visualize a single cache access"""
        # Perform access first
        value, hit = self.cache.access(address, self.memory)

        # Decode address based on cache type
        offset = address % self.cache.line_size

        if self.cache_type == "DirectMappedCache":
            index = (address // self.cache.line_size) % self.cache.num_lines
            tag = address // (self.cache.line_size * self.cache.num_lines)

            # Store in history
            self.access_history.append({
                'address': address,
                'index': index,
                'tag': tag,
                'offset': offset,
                'hit': hit,
                'value': value
            })

            # Print visualization
            print(f"\n{'='*70}")
            print(f"Access #{len(self.access_history)}: Address {address} (0x{address:04X})")
            print(f"{'='*70}")

            # Show address breakdown
            print(f"\nAddress Breakdown (Direct-Mapped):")
            print(f"  Address:  {address:6d}  (0x{address:04X})")
            print(f"  Tag:      {tag:6d}  (identifies which memory block)")
            print(f"  Index:    {index:6d}  (which cache line to use)")
            print(f"  Offset:   {offset:6d}  (byte position within cache line)")

            # Show result
            result_type = "HIT ✓" if hit else "MISS ✗"
            print(f"\nResult: {result_type}")
            print(f"  Value:    {value}")

            # Show cache state for this line
            print(f"\nCache Line {index} State:")
            line = self.cache.lines[index]
            valid, stored_tag, data = line
            print(f"  Valid:    {valid}")
            print(f"  Tag:      {stored_tag}")
            print(f"  Data:     [{', '.join(str(data[i]) for i in range(min(8, len(data))))}...]")

        elif self.cache_type == "FullyAssociativeCache":
            tag = address // self.cache.line_size

            # Store in history
            self.access_history.append({
                'address': address,
                'tag': tag,
                'offset': offset,
                'hit': hit,
                'value': value
            })

            # Print visualization
            print(f"\n{'='*70}")
            print(f"Access #{len(self.access_history)}: Address {address} (0x{address:04X})")
            print(f"{'='*70}")

            # Show address breakdown
            print(f"\nAddress Breakdown (Fully Associative):")
            print(f"  Address:  {address:6d}  (0x{address:04X})")
            print(f"  Tag:      {tag:6d}  (identifies cache line)")
            print(f"  Offset:   {offset:6d}  (byte position within cache line)")
            print(f"  Note: No index - can go in ANY cache line!")

            # Show result
            result_type = "HIT ✓" if hit else "MISS ✗"
            print(f"\nResult: {result_type}")
            print(f"  Value:    {value}")

            # Find which line contains this tag (if any)
            matching_line = None
            for i, (valid, line_tag, data) in enumerate(self.cache.lines):
                if valid and line_tag == tag:
                    matching_line = i
                    break

            if matching_line is not None:
                print(f"\nCache Line {matching_line} Contains This Data:")
                line = self.cache.lines[matching_line]
                valid, stored_tag, data = line
                print(f"  Valid:    {valid}")
                print(f"  Tag:      {stored_tag}")
                print(f"  LRU Time: {self.cache.lru_counters[matching_line]}")
                print(f"  Data:     [{', '.join(str(data[i]) for i in range(min(8, len(data))))}...]")

        # Show statistics
        print(f"\nCache Statistics:")
        print(f"  Hits:     {self.cache.hits}")
        print(f"  Misses:   {self.cache.misses}")
        print(f"  Hit Rate: {self.cache.hit_rate():.1%}")

        return value, hit

    def show_cache_state(self, max_lines=8):
        """Display current state of cache"""
        print(f"\n{'='*70}")
        print(f"CACHE STATE (showing first {max_lines} lines)")
        print(f"{'='*70}")
        print(f"{'Line':>5} | {'Valid':>5} | {'Tag':>6} | {'Data Sample':>20}")
        print(f"{'-'*5}-+-{'-'*5}-+-{'-'*6}-+-{'-'*20}")

        for i in range(min(max_lines, self.cache.num_lines)):
            valid, tag, data = self.cache.lines[i]
            data_sample = f"[{data[0]}, {data[1]}, {data[2]}, ...]" if valid else "[empty]"
            valid_str = "✓" if valid else "✗"
            print(f"{i:5d} | {valid_str:>5} | {tag:6d} | {data_sample:>20}")

        if self.cache.num_lines > max_lines:
            print(f"... ({self.cache.num_lines - max_lines} more lines)")

    def show_access_pattern(self):
        """Show pattern of recent accesses"""
        if not self.access_history:
            print("No accesses yet")
            return

        print(f"\n{'='*70}")
        print(f"ACCESS PATTERN (last {len(self.access_history)} accesses)")
        print(f"{'='*70}")

        if self.cache_type == "DirectMappedCache":
            print(f"{'#':>3} | {'Address':>7} | {'Index':>5} | {'Tag':>6} | {'Result':>6}")
            print(f"{'-'*3}-+-{'-'*7}-+-{'-'*5}-+-{'-'*6}-+-{'-'*6}")

            for i, access in enumerate(self.access_history, 1):
                result = "HIT ✓" if access['hit'] else "MISS ✗"
                print(f"{i:3d} | {access['address']:7d} | {access['index']:5d} | "
                      f"{access['tag']:6d} | {result:>6}")

        elif self.cache_type == "FullyAssociativeCache":
            print(f"{'#':>3} | {'Address':>7} | {'Tag':>6} | {'Result':>6}")
            print(f"{'-'*3}-+-{'-'*7}-+-{'-'*6}-+-{'-'*6}")

            for i, access in enumerate(self.access_history, 1):
                result = "HIT ✓" if access['hit'] else "MISS ✗"
                print(f"{i:3d} | {access['address']:7d} | "
                      f"{access['tag']:6d} | {result:>6}")


def demo_spatial_locality():
    """Demonstrate spatial locality with visualization"""
    print("\n" + "="*70)
    print("DEMO: Spatial Locality")
    print("="*70)
    print("\nCache: 8 lines, 16 bytes per line")
    print("Memory: 256 bytes (values = address)")

    cache = DirectMappedCache(num_lines=8, line_size=16)
    memory = [i for i in range(256)]
    viz = CacheVisualizer(cache, memory)

    print("\n\nAccessing address 0 (loads cache line with addresses 0-15)...")
    viz.visualize_access(0)

    print("\n\nAccessing address 5 (same cache line - should HIT)...")
    viz.visualize_access(5)

    print("\n\nAccessing address 15 (same cache line - should HIT)...")
    viz.visualize_access(15)

    print("\n\nAccessing address 16 (next cache line - should MISS)...")
    viz.visualize_access(16)

    viz.show_access_pattern()
    viz.show_cache_state()


def demo_conflict_miss():
    """Demonstrate conflict misses with visualization"""
    print("\n" + "="*70)
    print("DEMO: Conflict Misses")
    print("="*70)
    print("\nCache: 8 lines, 16 bytes per line")
    print("Memory: 256 bytes")
    print("\nAddresses 0 and 128 both map to cache line 0")

    cache = DirectMappedCache(num_lines=8, line_size=16)
    memory = [i for i in range(256)]
    viz = CacheVisualizer(cache, memory)

    print("\n\nAccessing address 0 (first time - MISS)...")
    viz.visualize_access(0)

    print("\n\nAccessing address 0 again (should HIT)...")
    viz.visualize_access(0)

    print("\n\nAccessing address 128 (maps to same line - evicts address 0)...")
    viz.visualize_access(128)

    print("\n\nAccessing address 0 again (was evicted - MISS)...")
    viz.visualize_access(0)

    viz.show_access_pattern()
    viz.show_cache_state()


def demo_sequential_access():
    """Demonstrate sequential access pattern"""
    print("\n" + "="*70)
    print("DEMO: Sequential Access Pattern")
    print("="*70)
    print("\nCache: 8 lines, 16 bytes per line")
    print("Accessing 32 sequential addresses (0-31)")

    cache = DirectMappedCache(num_lines=8, line_size=16)
    memory = [i for i in range(256)]
    viz = CacheVisualizer(cache, memory)

    print("\nAccessing addresses 0-31...")
    for addr in range(32):
        value, hit = viz.visualize_access(addr)
        if addr < 3 or addr in [15, 16, 31]:  # Show key accesses
            pass  # Already shown by visualize_access
        elif addr == 3:
            print("\n... (skipping to key addresses) ...")

    viz.show_access_pattern()
    print(f"\nPerformance Summary:")
    print(f"  Total Accesses: 32")
    print(f"  Cache Misses:   2  (one per cache line)")
    print(f"  Cache Hits:     30 (spatial locality!)")
    print(f"  Hit Rate:       {viz.cache.hit_rate():.1%}")


def demo_fully_associative_no_conflicts():
    """Demonstrate fully associative cache avoiding conflict misses"""
    print("\n" + "="*70)
    print("DEMO: Fully Associative Cache - No Conflict Misses")
    print("="*70)
    print("\nCache: 8 lines, 16 bytes per line (Fully Associative)")
    print("Memory: 256 bytes")
    print("\nAddresses 0 and 128 that would conflict in direct-mapped")

    cache = FullyAssociativeCache(num_lines=8, line_size=16)
    memory = [i for i in range(256)]
    viz = CacheVisualizer(cache, memory)

    print("\n\nAccessing address 0 (first time - MISS)...")
    viz.visualize_access(0)

    print("\n\nAccessing address 0 again (should HIT)...")
    viz.visualize_access(0)

    print("\n\nAccessing address 128 (would conflict in direct-mapped, but NOT here!)...")
    viz.visualize_access(128)

    print("\n\nAccessing address 0 again (still in cache - HIT!)...")
    viz.visualize_access(0)

    print("\n\nAccessing address 128 again (also still in cache - HIT!)...")
    viz.visualize_access(128)

    viz.show_access_pattern()
    viz.show_cache_state()

    print(f"\nKey Insight:")
    print(f"  In direct-mapped cache: addresses 0 and 128 conflict")
    print(f"  In fully associative: both can coexist in different lines")
    print(f"  Result: 3 misses, 2 hits vs 5 misses in direct-mapped")


def demo_lru_replacement():
    """Demonstrate LRU replacement policy in fully associative cache"""
    print("\n" + "="*70)
    print("DEMO: LRU Replacement Policy")
    print("="*70)
    print("\nCache: 4 lines, 16 bytes per line (Fully Associative)")
    print("Accessing 5 different cache lines - will evict LRU")

    cache = FullyAssociativeCache(num_lines=4, line_size=16)
    memory = [i for i in range(256)]
    viz = CacheVisualizer(cache, memory)

    addresses = [0, 16, 32, 48, 0, 64]  # 5 unique lines, 4 cache capacity

    print("\n\nFilling cache with 4 lines (0, 16, 32, 48)...")
    for addr in addresses[:4]:
        viz.visualize_access(addr)
        if addr == 16:
            print("\n... (continuing) ...")

    print("\n\nAccessing 0 again (makes it most recently used)...")
    viz.visualize_access(0)

    print("\n\nAccessing NEW line 64 (must evict something)...")
    print("LRU is line 16 (accessed first and never revisited)")
    viz.visualize_access(64)

    viz.show_access_pattern()
    viz.show_cache_state()

    print(f"\nLRU Policy Summary:")
    print(f"  Line 16 was evicted (least recently used)")
    print(f"  Lines 0, 32, 48, 64 remain in cache")
    print(f"  This policy works well for temporal locality")


def demo_comparison():
    """Compare direct-mapped vs fully associative on same workload"""
    print("\n" + "="*70)
    print("DEMO: Direct-Mapped vs Fully Associative Comparison")
    print("="*70)
    print("\nWorkload: Alternating access to addresses 0 and 128")
    print("Both have: 8 lines, 16 bytes per line")

    # Direct-mapped test
    print("\n\n--- DIRECT-MAPPED CACHE ---")
    dm_cache = DirectMappedCache(num_lines=8, line_size=16)
    memory = [i for i in range(256)]
    dm_viz = CacheVisualizer(dm_cache, memory)

    pattern = [0, 128, 0, 128, 0, 128]
    for addr in pattern:
        dm_viz.visualize_access(addr)
        if addr == 128 and dm_viz.cache.misses == 2:
            print("\n... (showing conflict misses) ...")

    # Fully associative test
    print("\n\n--- FULLY ASSOCIATIVE CACHE ---")
    fa_cache = FullyAssociativeCache(num_lines=8, line_size=16)
    fa_viz = CacheVisualizer(fa_cache, memory)

    for addr in pattern:
        fa_viz.visualize_access(addr)
        if addr == 128 and fa_viz.cache.misses == 2:
            print("\n... (no conflict misses!) ...")

    # Comparison summary
    print("\n\n" + "="*70)
    print("PERFORMANCE COMPARISON")
    print("="*70)
    print(f"\nDirect-Mapped:")
    print(f"  Hits:     {dm_cache.hits}")
    print(f"  Misses:   {dm_cache.misses}")
    print(f"  Hit Rate: {dm_cache.hit_rate():.1%}")
    print(f"  Problem:  Every access is a conflict miss!")

    print(f"\nFully Associative:")
    print(f"  Hits:     {fa_cache.hits}")
    print(f"  Misses:   {fa_cache.misses}")
    print(f"  Hit Rate: {fa_cache.hit_rate():.1%}")
    print(f"  Benefit:  No conflict misses - both lines coexist")

    print(f"\nTradeoff:")
    print(f"  Direct-Mapped:     Fast, simple hardware, conflict misses")
    print(f"  Fully Associative: Complex hardware (parallel search), no conflicts")


# Helper functions for testing
def int_to_bits(value, width=16):
    """Convert integer to list of bits (LSB first)

    Args:
        value: Integer to convert (0 to 2^width - 1)
        width: Number of bits (default 16)

    Returns:
        List of bits [b0, b1, ..., b15] where b0 is LSB

    Example:
        int_to_bits(5, 16) -> [1, 0, 1, 0, 0, 0, ..., 0]  # 0b0101
    """
    if value < 0 or value >= (1 << width):
        raise ValueError(f"Value {value} out of range for {width}-bit register")

    bits = []
    for i in range(width):
        bits.append((value >> i) & 1)
    return bits

def bits_to_int(bits):
    """Convert list of bits to integer (LSB first)

    Args:
        bits: List of bits [b0, b1, ..., b15] where b0 is LSB

    Returns:
        Integer value

    Example:
        bits_to_int([1, 0, 1, 0, 0, ...]) -> 5  # 0b0101
    """
    result = 0
    for i, bit in enumerate(bits):
        if bit:
            result |= (1 << i)
    return result

