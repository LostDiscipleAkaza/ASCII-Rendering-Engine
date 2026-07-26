import sys
import math
import time
import numpy as np

# Cross-platform non-blocking keyboard input
try:
    import msvcrt
    def get_key():
        if msvcrt.kbhit():
            try:
                key = msvcrt.getch()
                # Handle arrow keys / special characters
                if key in [b'\x00', b'\xe0']:
                    key = msvcrt.getch()
                return key.decode('utf-8', errors='ignore').lower()
            except:
                return None
        return None
except ImportError:
    import select
    def get_key():
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read(1).lower()
        return None

SHADES = " .,-~:;=!*#$@"

def load_obj(filename):
    vertices, faces = [], []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):
                parts = line.split()
                vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith('f '):
                parts = line.split()
                face_indices = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                for i in range(1, len(face_indices) - 1):
                    faces.append([face_indices[0], face_indices[i], face_indices[i+1]])
    return np.array(vertices), faces

def normalize_mesh(vertices):
    center = np.mean(vertices, axis=0)
    vertices = vertices - center
    max_dist = np.max(np.linalg.norm(vertices, axis=1))
    if max_dist > 0:
        vertices = (vertices / max_dist) * 1.5
    return vertices

class Engine3D:
    def __init__(self, width=110):
        self.width = width
        self.height = int(width * 0.45) 
        self.pixel_aspect = 11.0 / 24.0 
        
        self.screen_char = np.full((self.height, self.width), ' ')
        self.screen_color = np.zeros((self.height, self.width, 3), dtype=int)
        self.z_buffer = np.zeros((self.height, self.width))
        
        self.light_dir = np.array([0, -0.5, -1])
        self.light_dir = self.light_dir / np.linalg.norm(self.light_dir)

    def clear(self):
        self.screen_char.fill(' ')
        self.screen_color.fill(0)
        self.z_buffer.fill(-float('inf'))

    def draw(self):
        sys.stdout.write('\033[H') # Move cursor top-left
        lines = []
        for y in range(self.height):
            line_str = ""
            for x in range(self.width):
                char = self.screen_char[y, x]
                if char == ' ':
                    line_str += ' '
                else:
                    r, g, b = self.screen_color[y, x]
                    line_str += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
            lines.append(line_str)
            
        sys.stdout.write("\n".join(lines) + "\n")
        sys.stdout.flush()

    def render(self, vertices, faces, rx, ry, rz, offset_z, color_theme):
        self.clear()
        
        mx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
        my = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
        mz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
        
        rot_mat = mx @ my @ mz
        rotated_verts = np.dot(vertices, rot_mat.T)
        rotated_verts[:, 2] += offset_z

        for face in faces:
            v0, v1, v2 = rotated_verts[face[0]], rotated_verts[face[1]], rotated_verts[face[2]]
            
            normal = np.cross(v1 - v0, v2 - v0)
            length = np.linalg.norm(normal)
            if length == 0: continue
            normal = normal / length
            
            if np.dot(normal, v0) < 0:
                illumination = max(0, np.dot(normal, self.light_dir))
                self.rasterize(v0, v1, v2, illumination, normal, color_theme)

    def rasterize(self, v0, v1, v2, illumination, normal, color_theme):
        def project(v):
            x = int((v[0] * self.width / 4) * self.pixel_aspect + self.width / 2)
            y = int((v[1] * self.height / 4) + self.height / 2)
            return np.array([x, y, v[2]])

        p0, p1, p2 = project(v0), project(v1), project(v2)
        char = SHADES[int(illumination * (len(SHADES) - 1))]

        # Calculate RGB based on active theme
        if color_theme == 0:    # Cyber Green
            r, g, b = 0, int(255 * illumination), int(128 * illumination)
        elif color_theme == 1:  # Fire Orange
            r, g, b = int(255 * illumination), int(120 * illumination), 20
        elif color_theme == 2:  # Normal Vectors RGB
            r = int(abs(normal[0]) * 255 * illumination)
            g = int(abs(normal[1]) * 255 * illumination)
            b = int(abs(normal[2]) * 255 * illumination)
        elif color_theme == 3:  # Electric Blue
            r, g, b = int(50 * illumination), int(150 * illumination), int(255 * illumination)
        else:                   # Classic Monochrome
            v = int(255 * illumination)
            r, g, b = v, v, v

        min_x = max(0, min(p0[0], p1[0], p2[0]))
        max_x = min(self.width - 1, max(p0[0], p1[0], p2[0]))
        min_y = max(0, min(p0[1], p1[1], p2[1]))
        max_y = min(self.height - 1, max(p0[1], p1[1], p2[1]))

        for y in range(int(min_y), int(max_y) + 1):
            for x in range(int(min_x), int(max_x) + 1):
                w0 = (p2[0]-p1[0])*(y-p1[1]) - (p2[1]-p1[1])*(x-p1[0])
                w1 = (p0[0]-p2[0])*(y-p2[1]) - (p0[1]-p2[1])*(x-p2[0])
                w2 = (p1[0]-p0[0])*(y-p0[1]) - (p1[1]-p0[1])*(x-p0[0])

                if w0 >= 0 and w1 >= 0 and w2 >= 0:
                    area = max(w0 + w1 + w2, 1)
                    z = (w0*p0[2] + w1*p1[2] + w2*p2[2]) / area
                    if z > self.z_buffer[y, x]:
                        self.z_buffer[y, x] = z
                        self.screen_char[y, x] = char
                        self.screen_color[y, x] = [r, g, b]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py model2ascii.py <path_to_obj>")
        sys.exit()

    try:
        vertices, faces = load_obj(sys.argv[1])
        vertices = normalize_mesh(vertices)
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit()

    engine = Engine3D(width=110)
    rx, ry, rz = 0.5, 0.5, 0.0
    offset_z = 4.0
    color_theme = 0
    auto_rotate = False

    print('\033[2J') # Clear terminal
    
    try:
        while True:
            key = get_key()
            if key == 'w': rx -= 0.15
            elif key == 's': rx += 0.15
            elif key == 'a': ry -= 0.15
            elif key == 'd': ry += 0.15
            elif key == 'q': rz -= 0.15
            elif key == 'e': rz += 0.15
            elif key in ['+', '=']: offset_z = max(1.5, offset_z - 0.4) # Zoom in
            elif key in ['-', '_']: offset_z += 0.4                      # Zoom out
            elif key == 'c': color_theme = (color_theme + 1) % 5        # Toggle Color
            elif key == 'r': auto_rotate = not auto_rotate              # Toggle Spin
            elif key in ['x', '\x1b']: break                           # Exit

            if auto_rotate:
                ry += 0.04
                rx += 0.02

            engine.render(vertices, faces, rx, ry, rz, offset_z, color_theme)
            engine.draw()
            
            # Onscreen HUD Controls
            print(f"\033[36m[WASD/QE] Rotate | [+ / -] Zoom ({offset_z:.1f}) | [C] Theme ({color_theme+1}/5) | [R] Auto-Spin | [X] Exit\033[0m")
            
            time.sleep(0.03)
    except KeyboardInterrupt:
        pass
    print("\nExiting 3D Engine...")