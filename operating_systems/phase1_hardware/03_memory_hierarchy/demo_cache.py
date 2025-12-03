#!/usr/bin/env python3
"""
Cache Visualization Demo

This script demonstrates how a direct-mapped cache works through
interactive visualizations.

Usage:
    python3 demo_cache.py
"""

from memory_hierarchy import (
    DirectMappedCache,
    FullyAssociativeCache,
    CacheVisualizer,
    demo_spatial_locality,
    demo_conflict_miss,
    demo_sequential_access,
    demo_fully_associative_no_conflicts,
    demo_lru_replacement,
    demo_comparison
)


def main_menu():
    """Display main menu and run selected demo"""
    while True:
        print("\n" + "="*70)
        print("CACHE VISUALIZATION DEMOS")
        print("="*70)
        print("\n=== Direct-Mapped Cache Demos ===")
        print("1. Spatial Locality - How cache lines exploit nearby accesses")
        print("2. Conflict Misses - When addresses compete for same cache line")
        print("3. Sequential Access - Real-world performance pattern")
        print("\n=== Fully Associative Cache Demos ===")
        print("4. No Conflict Misses - Addresses can coexist in any line")
        print("5. LRU Replacement - How least-recently-used policy works")
        print("6. Direct-Mapped vs Fully Associative - Side-by-side comparison")
        print("\n=== Interactive ===")
        print("7. Interactive Mode (Direct-Mapped) - Try your own addresses")
        print("8. Interactive Mode (Fully Associative) - Try your own addresses")
        print("9. Exit")

        choice = input("\nSelect a demo (1-9): ").strip()

        if choice == "1":
            demo_spatial_locality()
            input("\nPress Enter to continue...")
        elif choice == "2":
            demo_conflict_miss()
            input("\nPress Enter to continue...")
        elif choice == "3":
            demo_sequential_access()
            input("\nPress Enter to continue...")
        elif choice == "4":
            demo_fully_associative_no_conflicts()
            input("\nPress Enter to continue...")
        elif choice == "5":
            demo_lru_replacement()
            input("\nPress Enter to continue...")
        elif choice == "6":
            demo_comparison()
            input("\nPress Enter to continue...")
        elif choice == "7":
            interactive_mode(cache_type="direct")
        elif choice == "8":
            interactive_mode(cache_type="fully_associative")
        elif choice == "9":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please select 1-9.")


def interactive_mode(cache_type="direct"):
    """Let user enter addresses to access"""
    print("\n" + "="*70)
    print("INTERACTIVE MODE")
    print("="*70)

    if cache_type == "direct":
        print("\nCache: Direct-Mapped, 8 lines, 16 bytes per line")
        cache = DirectMappedCache(num_lines=8, line_size=16)
    else:
        print("\nCache: Fully Associative, 8 lines, 16 bytes per line")
        cache = FullyAssociativeCache(num_lines=8, line_size=16)

    print("Memory: 256 bytes (values = address)")
    print("\nEnter addresses to access (0-255), or 'q' to quit")
    print("Commands: 'state' - show cache, 'history' - show access pattern")

    memory = [i for i in range(256)]
    viz = CacheVisualizer(cache, memory)

    while True:
        cmd = input("\nAddress or command: ").strip().lower()

        if cmd == 'q' or cmd == 'quit':
            break
        elif cmd == 'state':
            viz.show_cache_state()
        elif cmd == 'history':
            viz.show_access_pattern()
        elif cmd == 'help':
            print("\nCommands:")
            print("  0-255    - Access an address")
            print("  state    - Show current cache state")
            print("  history  - Show access pattern")
            print("  help     - Show this help")
            print("  q        - Quit interactive mode")
        else:
            try:
                addr = int(cmd)
                if 0 <= addr < 256:
                    viz.visualize_access(addr)
                else:
                    print("Address must be between 0 and 255")
            except ValueError:
                print("Invalid input. Enter a number (0-255) or command.")


if __name__ == "__main__":
    main_menu()
