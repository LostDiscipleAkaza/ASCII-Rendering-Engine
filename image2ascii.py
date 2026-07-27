import sys
import shutil
from PIL import Image

ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]


def grayify(image):
    """Convert a PIL RGB image to grayscale ('L' mode) for brightness mapping."""
    return image.convert("L")


def pixels_to_ascii(image):
    """Map a grayscale ('L' mode) PIL image's pixels to ASCII characters.

    Darkest pixel (0) -> ASCII_CHARS[0] ("@")
    Brightest pixel (255) -> ASCII_CHARS[-1] (".")
    """
    pixels = list(image.getdata())
    return "".join(
        ASCII_CHARS[pixel * (len(ASCII_CHARS) - 1) // 255] for pixel in pixels
    )


def get_default_width(fallback=120):
    """Use the real terminal width when available, capped to a sane range."""
    try:
        columns = shutil.get_terminal_size().columns
    except Exception:
        return fallback
    # Guard against absurdly small/large values (e.g. when piped or in some IDEs)
    return max(40, min(columns, 220)) if columns else fallback


def convert_image_to_ascii(image_path, new_width=None, use_color=True):
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"Error opening image: {e}")
        return None

    if new_width is None:
        new_width = get_default_width()

    # Aspect ratio adjustment for terminal font dimensions (chars are taller than wide)
    width, height = image.size
    ratio = height / width * 0.45
    new_height = max(1, int(new_width * ratio))
    image = image.resize((new_width, new_height))

    if use_color:
        pixels = list(image.getdata())
        rows = []
        row = []
        for i, (r, g, b) in enumerate(pixels):
            brightness = int(0.299 * r + 0.587 * g + 0.114 * b)
            char = ASCII_CHARS[brightness * (len(ASCII_CHARS) - 1) // 255]
            row.append(f"\033[38;2;{r};{g};{b}m{char}\033[0m")
            if (i + 1) % new_width == 0:
                rows.append("".join(row))
                row = []
        ascii_img = "\n".join(rows)
    else:
        gray_image = grayify(image)
        chars = pixels_to_ascii(gray_image)
        rows = [chars[i:i + new_width] for i in range(0, len(chars), new_width)]
        ascii_img = "\n".join(rows)

    return ascii_img


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py image2ascii.py <path_to_image> [nocolor]")
        sys.exit(1)

    image_path = sys.argv[1]
    use_color = "nocolor" not in sys.argv

    result = convert_image_to_ascii(image_path, use_color=use_color)
    if result:
        print(result)