#!/usr/bin/env python3
import sys
from pathlib import Path

v = Path(sys.argv[1]).read_bytes()
p = Path(sys.argv[2]).read_bytes()
print(f"vanilla {len(v)} patched {len(p)}")
shared = min(len(v), 913)  # end of vanilla script 6 body
if v[:shared] == p[:shared]:
    print(f"first {shared} bytes match")
else:
    for i in range(shared):
        if v[i] != p[i]:
            print(f"first diff at {i}: v={v[i]:02x} p={p[i]:02x}")
            print("v", v[i : i + 32].hex())
            print("p", p[i : i + 32].hex())
            break
print(f"patched tail ({len(p)-shared} bytes): {p[shared:].hex()[:80]}...")
