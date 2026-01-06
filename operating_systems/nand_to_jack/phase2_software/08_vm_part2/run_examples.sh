#!/bin/bash
# Run VM translator on all example programs

echo "=== VM Translator Part 2: Running Examples ==="
echo

for dir in examples/*/; do
    dir_name=$(basename "$dir")
    echo "Translating $dir_name..."
    python3 vm_translator.py "$dir"

    if [ $? -eq 0 ]; then
        echo "✓ $dir_name translated successfully"
    else
        echo "✗ $dir_name translation failed"
        exit 1
    fi
    echo
done

echo "=== All examples translated successfully! ==="
echo
echo "Generated files:"
find examples/ -name "*.asm" -o -name "*.hack"
