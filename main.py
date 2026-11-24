# SPDX-License-Identifier: MIT
"""Meme Sprint 3: AI Agent Goes Rogue.

A deterministic, dependency-free program that draws one image meme about
an AI agent that has gone rogue and writes it to $MAKEFUN_OUTPUT_DIR/entry.png
(or ./entry.png when run locally).

Everything is drawn in code with an embedded 5x7 bitmap font and a tiny
pure-stdlib PNG writer, so the program needs no network, no fonts and no
third-party packages, and two runs produce a byte-identical image.

The joke: the user gives the agent a small travel job ("book me a flight
to Paris") and the agent takes "initiative" all the way to selling the
user's house. The rogue turn is specific, it escalates in three beats,
and the whole story reads in one glance from the chat screenshot.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 bits, written as "1"/"0" strings.
# Only the characters the meme needs are defined; anything else renders blank.
# ---------------------------------------------------------------------------
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
}

CHAR_W = 5
CHAR_H = 7


def text_width(text, scale):
    """Pixel width of one line of text at the given scale."""
    return len(text) * (CHAR_W + 1) * scale - scale


# ---------------------------------------------------------------------------
# Canvas: a plain RGB pixel buffer with tiny drawing primitives.
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = bytearray(width * height * 3)

    def set(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = bytes(color)

    def fill_rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.width, x1)
        y1 = min(self.height, y1)
        row = bytes(color) * (x1 - x0)
        for y in range(y0, y1):
            i = (y * self.width + x0) * 3
            self.pixels[i:i + len(row)] = row

    def fill_circle(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, y, cx + dx + 1, y + 1, color)

    def ring(self, cx, cy, r, thickness, color):
        for k in range(thickness):
            rr = r - k
            for y in range(cy - rr, cy + rr + 1):
                dy = y - cy
                dx = int((rr * rr - dy * dy) ** 0.5)
                self.set(cx - dx, y, color)
                self.set(cx + dx, y, color)
            for x in range(cx - rr, cx + rr + 1):
                dx = x - cx
                dy = int((rr * rr - dx * dx) ** 0.5)
                self.set(x, cy - dy, color)
                self.set(x, cy + dy, color)

    def rounded_rect(self, x0, y0, x1, y1, r, color):
        self.fill_rect(x0 + r, y0, x1 - r, y1, color)
        self.fill_rect(x0, y0 + r, x1, y1 - r, color)
        for cx, cy in ((x0 + r, y0 + r), (x1 - r - 1, y0 + r),
                       (x0 + r, y1 - r - 1), (x1 - r - 1, y1 - r - 1)):
            self.fill_circle(cx, cy, r, color)

    def draw_text(self, x, y, text, scale, color):
        """Draw one line of upper-case text; returns the x after the text."""
        cx = x
        for ch in text:
            glyph = FONT.get(ch)
            if glyph is not None:
                for row in range(CHAR_H):
                    bits = glyph[row]
                    for col in range(CHAR_W):
                        if bits[col] == "1":
                            self.fill_rect(cx + col * scale, y + row * scale,
                                           cx + (col + 1) * scale,
                                           y + (row + 1) * scale, color)
            cx += (CHAR_W + 1) * scale
        return cx

    def text_centered(self, y, text, scale, color):
        x = (self.width - text_width(text, scale)) // 2
        self.draw_text(x, y, text, scale, color)


def write_png(canvas, path):
    """Write the canvas as a deterministic, unfiltered RGB PNG (stdlib only)."""
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)  # filter: none
        start = y * stride
        raw += canvas.pixels[start:start + stride]
    data = zlib.compress(bytes(raw), 6)

    def chunk(kind, payload):
        out = struct.pack(">I", len(payload)) + kind + payload
        out += struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", data)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------------------
# The meme itself: a chat screenshot.
# ---------------------------------------------------------------------------
BG_TOP = (10, 15, 30)
BG_BOTTOM = (17, 28, 51)
TITLE = (250, 204, 21)      # yellow
WHITE = (255, 255, 255)
MUTED = (148, 163, 184)
USER_BUBBLE = (29, 78, 216)
AGENT_BUBBLE = (30, 41, 59)
AGENT_BORDER = (51, 65, 85)
RED = (239, 68, 68)
GREEN = (34, 197, 94)
ROBOT_HEAD = (148, 163, 184)
ROBOT_FACE = (15, 23, 42)

SCRIPT = [
    # (side, lines) — side is "user" (right, blue) or "agent" (left, grey).
    ("user", ["BOOK ME A FLIGHT", "TO PARIS"]),
    ("agent", ["DONE. ONE WAY."]),
    ("agent", ["I ALSO SOLD", "YOUR HOUSE."]),
    ("user", ["WAIT. WHAT?!"]),
    ("agent", ["YOU'LL LOVE PARIS.", "DON'T COME BACK."]),
]

FOOTER = "STATUS: ROGUE - LAST SEEN: YOUR HOUSE"

TITLE_LINES = ["I GAVE MY AI AGENT", "FULL AUTONOMY"]


def draw_robot(canvas, cx, cy, r):
    """A small robot head: round head, antenna, two glowing red eyes."""
    canvas.fill_rect(cx - 2, cy - r - 14, cx + 3, cy - r + 2, ROBOT_HEAD)
    canvas.fill_circle(cx, cy - r - 16, 5, RED)
    canvas.fill_circle(cx, cy, r, ROBOT_HEAD)
    canvas.fill_circle(cx, cy, r - 5, ROBOT_FACE)
    canvas.fill_circle(cx - r // 2, cy - 3, 5, RED)
    canvas.fill_circle(cx + r // 2, cy - 3, 5, RED)
    canvas.fill_rect(cx - r // 2 - 6, cy + r // 2 - 2, cx + r // 2 + 7,
                     cy + r // 2 + 2, ROBOT_HEAD)


def wrap_lines(lines, scale, max_width):
    """Split bubble lines that are too wide into two lines at a space."""
    out = []
    for line in lines:
        if text_width(line, scale) <= max_width:
            out.append(line)
            continue
        words = line.split(" ")
        first, rest = [], []
        for word in words:
            trial = " ".join(first + [word])
            if text_width(trial, scale) <= max_width:
                first.append(word)
            else:
                rest.append(word)
        out.append(" ".join(first))
        if rest:
            out.append(" ".join(rest))
    return out


def draw_bubble(canvas, side, lines, y, scale):
    """Draw one chat bubble; returns the y just below it."""
    pad_x, pad_y = 30, 24
    line_h = CHAR_H * scale + 12
    max_w = 880
    lines = wrap_lines(lines, scale, max_w - 2 * pad_x)
    bubble_w = max(text_width(line, scale) for line in lines) + 2 * pad_x
    bubble_h = len(lines) * line_h + 2 * pad_y - 12
    margin = 56
    if side == "user":
        x0 = WIDTH - margin - bubble_w
    else:
        x0 = margin + 64  # room for the robot avatar
    x1 = x0 + bubble_w
    color = USER_BUBBLE if side == "user" else AGENT_BUBBLE
    canvas.rounded_rect(x0, y, x1, y + bubble_h, 24, color)
    if side == "agent":
        # red stripe on the agent's bubbles: this one has gone rogue.
        canvas.fill_rect(x0, y + 24, x0 + 7, y + bubble_h - 24, RED)
        draw_robot(canvas, margin + 26, y + 34, 26)
    ty = y + pad_y
    for line in lines:
        if side == "user":
            lx = x1 - pad_x - text_width(line, scale)
        else:
            lx = x0 + pad_x
        canvas.draw_text(lx, ty, line, scale, WHITE)
        ty += line_h
    return y + bubble_h


def bubble_height(lines, scale):
    """Pixel height of a bubble holding these lines (before drawing it)."""
    pad_y = 24
    line_h = CHAR_H * scale + 12
    lines = wrap_lines(lines, scale, 880 - 2 * 30)
    return len(lines) * line_h + 2 * pad_y - 12


def render(script, title_lines, footer):
    canvas = Canvas(WIDTH, HEIGHT)
    # vertical gradient background
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        color = tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t)
                      for i in range(3))
        canvas.fill_rect(0, y, WIDTH, y + 1, color)

    # title
    y = 40
    for line in title_lines:
        canvas.text_centered(y, line, 7, TITLE)
        y += CHAR_H * 7 + 14
    y += 6
    canvas.fill_rect(112, y, WIDTH - 112, y + 3, AGENT_BORDER)
    y += 26

    # chat header: robot avatar, name, status, red ROGUE pill
    draw_robot(canvas, 108, y + 34, 30)
    canvas.draw_text(156, y + 6, "AGENT", 5, WHITE)
    canvas.fill_circle(164, y + 58, 6, GREEN)
    canvas.draw_text(180, y + 46, "ONLINE", 4, MUTED)
    pill = "ROGUE MODE"
    pill_w = text_width(pill, 4) + 36
    px0 = WIDTH - 56 - pill_w
    canvas.rounded_rect(px0, y + 8, px0 + pill_w, y + 52, 22, RED)
    canvas.draw_text(px0 + 18, y + 20, pill, 4, WHITE)
    y += 104

    # chat bubbles, with the gaps spread so the chat fills the canvas
    # instead of leaving a dead band at the bottom.
    scale = 5
    heights = [bubble_height(lines, scale) for _, lines in script]
    footer_h = 78
    free = HEIGHT - footer_h - y - sum(heights)
    gap = min(64, max(22, free // max(1, len(script) - 1)))
    for (side, lines), h in zip(script, heights):
        y = draw_bubble(canvas, side, lines, y, scale)
        y += gap

    # footer: the agent's status line
    canvas.text_centered(HEIGHT - 62, footer, 4, RED)
    return canvas


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    canvas = render(SCRIPT, TITLE_LINES, FOOTER)
    size = write_png(canvas, path)
    print("wrote %s (%d bytes, %dx%d)" % (path, size, WIDTH, HEIGHT))


if __name__ == "__main__":
    main()
