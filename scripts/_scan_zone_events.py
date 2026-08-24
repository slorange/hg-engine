#!/usr/bin/env python3
import struct
import sys
import ndspy.narc


def parse_zone(data: bytes) -> dict:
    off = 0
    bg = struct.unpack_from("<I", data, off)[0]
    off += 4 + bg * 20
    ob = struct.unpack_from("<I", data, off)[0]
    off += 4 + ob * 32
    wa = struct.unpack_from("<I", data, off)[0]
    off += 4
    warps = []
    for _ in range(wa):
        x, z, hdr, anc = struct.unpack_from("<HHHH", data, off)
        y = struct.unpack_from("<I", data, off + 8)[0]
        warps.append((x, z, hdr, anc, y))
        off += 12
    co = struct.unpack_from("<I", data, off)[0]
    off += 4
    coords = []
    for _ in range(co):
        vals = struct.unpack_from("<8H", data, off)
        coords.append(vals)
        off += 16
    return {"len": len(data), "objs": ob, "warps": warps, "coords": coords}


def main(argv: list[str]) -> int:
    path = argv[1]
    narc = ndspy.narc.NARC.fromFile(path)
    targets = [(5, 12, 33), (5, 2, 48)]
    for idx, data in enumerate(narc.files):
        info = parse_zone(data)
        for warp in info["warps"]:
            if (warp[0], warp[1], warp[2]) in [(5, 12, 33), (5, 2, 48)]:
                print(
                    f"idx={idx} len={info['len']} warps={info['warps']} "
                    f"coords={info['coords']}"
                )
                break
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
