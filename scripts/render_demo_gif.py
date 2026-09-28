"""Render the deterministic README demo as a small animated GIF.

This is a maintainer utility, not a runtime dependency. Install Pillow only
when regenerating the checked-in asset: ``python -m pip install Pillow``.
"""

from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - maintainer-only helper
    raise SystemExit("Install Pillow to regenerate assets/demo.gif") from exc


WIDTH = 1200
HEIGHT = 675
BACKGROUND = "#0d1117"
PANEL = "#161b22"
BORDER = "#30363d"
TEXT = "#e6edf3"
MUTED = "#8b949e"
GREEN = "#3fb950"
YELLOW = "#d29922"
RED = "#f85149"
BLUE = "#58a6ff"


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = Path("/System/Library/Fonts/SFNSMono.ttf")
    fallback = Path("/System/Library/Fonts/Menlo.ttc")
    selected = path if path.exists() else fallback
    del bold  # Keep one portable face; color and size provide hierarchy.
    return ImageFont.truetype(str(selected), size=size)


def frame(lines: list[tuple[str, str]], *, progress: str) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (40, 38, WIDTH - 40, HEIGHT - 38), 18, fill=PANEL, outline=BORDER, width=2
    )
    draw.ellipse((70, 67, 86, 83), fill=RED)
    draw.ellipse((98, 67, 114, 83), fill=YELLOW)
    draw.ellipse((126, 67, 142, 83), fill=GREEN)
    draw.text(
        (168, 63), "OSS Link Auditor — deterministic demo", font=font(22, bold=True), fill=TEXT
    )

    y = 125
    for content, color in lines:
        draw.text((76, y), content, font=font(22), fill=color)
        y += 45

    draw.text((76, HEIGHT - 84), progress, font=font(18), fill=MUTED)
    return image


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output = root / "assets" / "demo.gif"
    command = [("$ python3 scripts/demo.py", BLUE)]
    stages = [
        command,
        command + [("Scanning demo.md ...", MUTED)],
        command
        + [
            ("Scanning demo.md ...", MUTED),
            ("✓ HEALTHY   demo.md:1   /healthy", GREEN),
        ],
        command
        + [
            ("Scanning demo.md ...", MUTED),
            ("✓ HEALTHY   demo.md:1   /healthy", GREEN),
            ("↪ REDIRECT  demo.md:2   /moved → /healthy", YELLOW),
        ],
        command
        + [
            ("Scanning demo.md ...", MUTED),
            ("✓ HEALTHY   demo.md:1   /healthy", GREEN),
            ("↪ REDIRECT  demo.md:2   /moved → /healthy", YELLOW),
            ("✗ BROKEN    demo.md:3   /missing   HTTP 404", RED),
        ],
        command
        + [
            ("Scanning demo.md ...", MUTED),
            ("✓ HEALTHY   demo.md:1   /healthy", GREEN),
            ("↪ REDIRECT  demo.md:2   /moved → /healthy", YELLOW),
            ("✗ BROKEN    demo.md:3   /missing   HTTP 404", RED),
            ("", TEXT),
            ("3 unique links · 1 healthy · 1 redirect · 1 broken", TEXT),
        ],
    ]
    frames = [
        frame(lines, progress=f"Frame {index + 1}/{len(stages)} · no network required")
        for index, lines in enumerate(stages)
    ]
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=[900, 800, 850, 900, 1100, 2600],
        loop=0,
        optimize=True,
    )
    print(output)


if __name__ == "__main__":
    main()
