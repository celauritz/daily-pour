#!/usr/bin/env python3
"""Generate Daily Pour PWA icons: chalkboard ground + brass pour-droplet glyph.
Pure stdlib (zlib). Supersampled for antialiasing. Opaque RGB PNGs."""
import zlib, struct, math, os

OUT = os.path.dirname(os.path.abspath(__file__))

# palette (matches app CSS)
G_TOP = (0x23, 0x26, 0x1f)
G_BOT = (0x0b, 0x0c, 0x08)
BRASS = (0xc9, 0x9a, 0x3e)
BRASS_DIM = (0x8a, 0x6b, 0x2c)
BRASS_HI = (0xe4, 0xc4, 0x7f)

SS = 3  # supersample factor


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def blend(bg, fg, alpha):
    return tuple(bg[i] + (fg[i] - bg[i]) * alpha for i in range(3))


def render(size):
    W = size * SS
    H = size * SS
    # float buffer
    buf = [[None] * W for _ in range(H)]

    cx = W / 2.0
    # droplet geometry (kept within maskable safe zone)
    circ_cy = 0.575 * H
    circ_r = 0.205 * H
    apex_y = 0.265 * H

    # inner border rect
    inset = 0.105 * W
    bt = 0.020 * W  # border thickness
    bx0, by0 = inset, inset
    bx1, by1 = W - inset, H - inset

    def in_droplet(x, y):
        # union of bottom circle and apex triangle
        if (x - cx) ** 2 + (y - circ_cy) ** 2 <= circ_r ** 2:
            return True
        # triangle (cx,apex_y) - (cx-circ_r,circ_cy) - (cx+circ_r,circ_cy)
        if y < apex_y or y > circ_cy:
            return False
        frac = (y - apex_y) / (circ_cy - apex_y)
        halfw = circ_r * frac
        return abs(x - cx) <= halfw

    for y in range(H):
        t = y / (H - 1)
        base = lerp(G_TOP, G_BOT, t)
        row = buf[y]
        for x in range(W):
            c = base
            # subtle vignette toward corners
            dx = (x - cx) / (W / 2.0)
            dy = (y - H / 2.0) / (H / 2.0)
            v = dx * dx + dy * dy
            if v > 1.0:
                c = blend(c, (0, 0, 0), min(0.25, (v - 1.0) * 0.4))
            # inner border stroke
            on_border = (
                bx0 - bt <= x <= bx1 + bt and by0 - bt <= y <= by1 + bt and
                not (bx0 + bt <= x <= bx1 - bt and by0 + bt <= y <= by1 - bt)
            )
            if on_border:
                c = blend(c, BRASS_DIM, 0.55)
            # droplet
            if in_droplet(x, y):
                c = BRASS
                # highlight lobe upper-left of droplet
                hx, hy = cx - 0.075 * W, circ_cy - 0.11 * H
                if (x - hx) ** 2 + (y - hy) ** 2 <= (0.075 * H) ** 2:
                    c = blend(BRASS, BRASS_HI, 0.7)
            row[x] = c

    # downsample SS x SS -> size
    out = bytearray()
    for oy in range(size):
        out.append(0)  # filter byte: none
        for ox in range(size):
            r = g = b = 0.0
            for sy in range(SS):
                srow = buf[oy * SS + sy]
                for sx in range(SS):
                    px = srow[ox * SS + sx]
                    r += px[0]; g += px[1]; b += px[2]
            n = SS * SS
            out.append(max(0, min(255, round(r / n))))
            out.append(max(0, min(255, round(g / n))))
            out.append(max(0, min(255, round(b / n))))
    return bytes(out)


def write_png(path, size, raw):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)  # 8-bit RGB
    idat = zlib.compress(raw, 9)
    with open(path, "wb") as f:
        f.write(sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b""))
    print("wrote", path, size)


for name, size in [("icon-192.png", 192), ("icon-512.png", 512), ("apple-touch-icon.png", 180)]:
    write_png(os.path.join(OUT, name), size, render(size))
