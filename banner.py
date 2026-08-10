"""
banner.py - Generate ASCII art banners from text or images.

Usage:
    py banner.py text "HELLO WORLD" [--font slant] [--color red] [--border]
    py banner.py image assets/tiger.jpg [--width 100] [--nocolor] [--border]

Run `py banner.py text --list-fonts` to see available FIGlet fonts.
"""

import argparse
import sys

import pyfiglet

from image2ascii import convert_image_to_ascii, get_default_width

# ANSI truecolor-ish palette for simple named colors (used for text banners,
# which have no inherent color the way an image does).
ANSI_COLORS = {
    "red": "\033[38;2;255;60;60m",
    "green": "\033[38;2;60;220;120m",
    "blue": "\033[38;2;80;140;255m",
    "yellow": "\033[38;2;255;220;60m",
    "magenta": "\033[38;2;255;80;220m",
    "cyan": "\033[38;2;60;220;220m",
    "white": "\033[38;2;255;255;255m",
}
ANSI_RESET = "\033[0m"


def generate_text_banner(text, font="standard"):
    """Render text as a big block-letter ASCII banner using pyfiglet.

    Trailing blank lines that pyfiglet sometimes emits are stripped, and
    the result is right-padded so every row is exactly the same width
    (helpful for downstream centering/bordering).
    """
    try:
        rendered = pyfiglet.figlet_format(text, font=font)
    except pyfiglet.FontNotFound:
        available = ", ".join(sorted(pyfiglet.FigletFont.getFonts()))
        raise ValueError(
            f"Unknown font '{font}'. Available fonts: {available}"
        )

    lines = rendered.rstrip("\n").split("\n")
    width = max((len(line) for line in lines), default=0)
    lines = [line.ljust(width) for line in lines]
    return "\n".join(lines)


def generate_image_banner(image_path, width=None, use_color=True):
    """Render an image as ASCII art, reusing the core image2ascii pipeline."""
    if width is None:
        width = get_default_width()
    result = convert_image_to_ascii(image_path, new_width=width, use_color=use_color)
    if result is None:
        raise ValueError(f"Could not open image: {image_path}")
    return result


def _visible_length(line):
    """Length of a line ignoring ANSI escape codes (for alignment/border math)."""
    out = []
    in_escape = False
    for ch in line:
        if ch == "\033":
            in_escape = True
            continue
        if in_escape:
            if ch == "m":
                in_escape = False
            continue
        out.append(ch)
    return len(out)


def wrap_in_border(art, padding=1):
    """Wrap ASCII art in a box-drawing border, sized to the widest line.

    ANSI color codes are ignored when measuring width so colored banners
    still line up correctly.
    """
    lines = art.split("\n")
    content_width = max((_visible_length(line) for line in lines), default=0)
    pad = " " * padding

    top = "┌" + "─" * (content_width + padding * 2) + "┐"
    bottom = "└" + "─" * (content_width + padding * 2) + "┘"

    boxed_lines = [top]
    for line in lines:
        extra = content_width - _visible_length(line)
        boxed_lines.append(f"│{pad}{line}{' ' * extra}{pad}│")
    boxed_lines.append(bottom)

    return "\n".join(boxed_lines)


def _build_arg_parser():
    parser = argparse.ArgumentParser(
        description="Generate ASCII art banners from text or images."
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    text_parser = subparsers.add_parser("text", help="Generate a banner from text")
    text_parser.add_argument("text", nargs="?", help="Text to render as a banner")
    text_parser.add_argument(
        "--font", default="standard", help="pyfiglet font name (default: standard)"
    )
    text_parser.add_argument(
        "--color", choices=sorted(ANSI_COLORS), help="Solid ANSI color for the text"
    )
    text_parser.add_argument(
        "--border", action="store_true", help="Wrap the banner in a border"
    )
    text_parser.add_argument(
        "--list-fonts", action="store_true", help="List available fonts and exit"
    )

    image_parser = subparsers.add_parser("image", help="Generate a banner from an image")
    image_parser.add_argument("path", help="Path to the image file")
    image_parser.add_argument("--width", type=int, default=None, help="Output width in characters")
    image_parser.add_argument("--nocolor", action="store_true", help="Render in monochrome")
    image_parser.add_argument(
        "--border", action="store_true", help="Wrap the banner in a border"
    )

    return parser


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    if args.mode == "text":
        if args.list_fonts:
            for font in sorted(pyfiglet.FigletFont.getFonts()):
                print(font)
            return

        if not args.text:
            parser.error("the 'text' argument is required unless --list-fonts is given")

        try:
            art = generate_text_banner(args.text, font=args.font)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

        if args.color:
            color_code = ANSI_COLORS[args.color]
            art = "\n".join(f"{color_code}{line}{ANSI_RESET}" for line in art.split("\n"))

        if args.border:
            art = wrap_in_border(art)

        print(art)

    elif args.mode == "image":
        try:
            art = generate_image_banner(
                args.path, width=args.width, use_color=not args.nocolor
            )
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

        if args.border:
            art = wrap_in_border(art)

        print(art)


if __name__ == "__main__":
    main()
