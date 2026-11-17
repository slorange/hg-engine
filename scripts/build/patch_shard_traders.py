#!/usr/bin/env python3
"""Replace both shard traders' reward and bag-space item operands in place."""

import argparse
import struct
from pathlib import Path

# Red: offense; blue: survival; yellow: execution; green: surprises.
REWARDS = (201, 204, 206, 202, 205, 208, 203, 210, 209, 207, 211, 212)
VANILLA = {
    857: (149, 151, 154, 155, 150, 160, 153, 158, 163, 152, 157, 162),
    807: (156, 164, 169, 165, 170, 175, 168, 173, 178, 167, 172, 182),
}


def item_assignment(item):
    return struct.pack('<HHH', 41, 0x8004, item)


def patch(directory, verify=False):
    for member, old_items in VANILLA.items():
        path = directory / f'2_{member}'
        data = path.read_bytes()
        if not verify:
            for old, new in zip(old_items, REWARDS):
                before, after = item_assignment(old), item_assignment(new)
                # Each reward appears once in the capacity check and once in the grant.
                if data.count(before) != 2:
                    raise ValueError(f'{path}: expected two assignments for berry {old}')
                data = data.replace(before, after)
            path.write_bytes(data)
        for item in REWARDS:
            if data.count(item_assignment(item)) != 2:
                raise ValueError(f'{path}: missing capacity check or reward for {item}')
        for item in old_items:
            if item_assignment(item) in data:
                raise ValueError(f'{path}: old reward {item} remains')
        print(f'{path}: all 12 rare berries verified (capacity checks and grants)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    patch(args.directory, args.verify)
