
```markdown
# ASCII Rendering Terminal Engine 

A lightweight Python software rendering engine that converts 2D images (`.jpg`, `.png`, `.jpeg`) and 3D Wavefront models (`.obj`) into interactive, colorful ASCII art inside your terminal.

---

## Features

* **2D Image Renderer:** 24-bit ANSI Truecolor output with font aspect-ratio correction and perceptual brightness mapping.
* **3D OBJ Model Viewer:** Custom software rendering pipeline featuring matrix transformations, backface culling, diffuse surface lighting, and Z-buffer depth sorting.
* **ASCII Banners:** Turn text or images into standalone ASCII art banners, with optional color and border framing.
* **Interactive Controls:** Smooth non-blocking WASD controls to rotate, zoom, auto-spin, and cycle color shaders on the fly.

---

## Prerequisites & Installation

```bash
pip install numpy pillow pyfiglet

```

---

## Project Structure

```text
├── assets/
│   ├── your_image.jpg
│   └── your_model.obj
├── image2ascii.py
└── model2ascii.py

```

*Place all your `.obj` files and images inside the `assets/` directory.*

---

## Usage

### 1. 2D Image to ASCII

```cmd
py image2ascii.py assets/your_image.jpg

```

*(Add `nocolor` at the end of the command for monochrome mode).*

### 2. Interactive 3D Model Viewer

```cmd
py model2ascii.py assets/your_model.obj

```

### 3. ASCII Art Banners (Text or Image)

Generate a standalone banner from text using a FIGlet font:

```cmd
py banner.py text "HELLO WORLD" --font slant --color cyan --border

```

Generate a banner from an image:

```cmd
py banner.py image assets/tiger.jpg --width 100 --border

```

*(Add `--nocolor` for monochrome image banners. Run `py banner.py text --list-fonts` to see all available FIGlet fonts. `--border` works for both text and image banners.)*

---

## 3D Controls

| Key | Action |
| --- | --- |
| **`W` / `S**` | Pitch (Rotate Up / Down) |
| **`A` / `D**` | Yaw (Rotate Left / Right) |
| **`Q` / `E**` | Roll (Rotate Counter-Clockwise / Clockwise) |
| **`+` / `-**` | Zoom In / Zoom Out |
| **`C`** | Cycle Color Themes *(Cyber Green, Fire Orange, RGB Normals, Electric Blue, White)* |
| **`R`** | Toggle Auto-Spin |
| **`X`** | Exit |

```

```
