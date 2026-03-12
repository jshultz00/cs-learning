#!/bin/bash

# Author: Justin Shultz
# ID: m8rZr5w8rON0ii9RiwOdQyzmNtB3
# Lab: Crack Passwords With JohnTheRipper

# Description: This script cracks a hash using John the Ripper.

this_dir=$(dirname $0)
md5_file="$this_dir/md5.txt"
sha1_file="$this_dir/sha1.txt"
sha256_file="$this_dir/sha256.txt"
rockyou_file="$this_dir/rockyou.txt"

crack_and_display() {
    local format=$1
    local file=$2
    local label=$3

    john --format=$format --wordlist=$rockyou_file $file > /dev/null 2>&1
    local cracked=$(john --show --format=$format $file 2>/dev/null | head -n 1 | cut -d: -f2)

    echo "┌─────────────────────────────────────┐"
    printf  "│  %-8s  →  %-22s│\n" "$label" "${cracked:-<not found>}"
    echo "└─────────────────────────────────────┘"
}

crack_and_display "raw-md5"    $md5_file    "MD5"
crack_and_display "raw-sha1"   $sha1_file   "SHA-1"
crack_and_display "raw-sha256" $sha256_file "SHA-256"
