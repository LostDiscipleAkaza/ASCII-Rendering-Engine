import sys
from PIL import Image

ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

def convert_image_to_ascii(image_path, new_width=120, use_color=True):
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"Error opening image: {e}")
        return None

    # Aspect ratio adjustment for terminal font dimensions
    width, height = image.size
    ratio = height / width * 0.45
    new_height = int(new_width * ratio)
    image = image.resize((new_width, new_height))

    pixels = list(image.getdata())
    ascii_img = ""

    for i, (r, g, b) in enumerate(pixels):
        # Perceptual grayscale brightness formula
        brightness = int(0.299 * r + 0.587 * g + 0.114 * b)
        char = ASCII_CHARS[brightness * (len(ASCII_CHARS) - 1) // 255]

        if use_color:
            # 24-bit ANSI Color: \033[38;2;R;G;Bm
            ascii_img += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
        else:
            ascii_img += char

        if (i + 1) % new_width == 0:
            ascii_img += "\n"

    return ascii_img

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py image2ascii.py <path_to_image> [nocolor]")
        sys.exit(1)

    image_path = sys.argv[1]
    use_color = "nocolor" not in sys.argv

    result = convert_image_to_ascii(image_path, new_width=120, use_color=use_color)
    if result:
        print(result)