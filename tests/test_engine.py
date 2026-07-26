import unittest
import numpy as np
from PIL import Image
import sys
import os

# Add the parent directory to the system path so Python can find your main scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import image2ascii
import model2ascii

class TestImage2Ascii(unittest.TestCase):
    def setUp(self):
        # Create a simple 100x100 white image in memory for testing
        self.test_img = Image.new('RGB', (100, 100), color='white')

    def test_grayify(self):
        gray_img = image2ascii.grayify(self.test_img)
        self.assertEqual(gray_img.mode, 'L', "Image should be converted to grayscale ('L' mode)")

    def test_pixels_to_ascii_extremes(self):
        # Create a 2x1 image with pure black (0) and pure white (255)
        img = Image.new('L', (2, 1))
        img.putdata([0, 255])
        
        ascii_res = image2ascii.pixels_to_ascii(img)
        
        # Black (0) should map to the darkest character "@"
        # White (255) should map to the lightest character "."
        self.assertEqual(ascii_res, "@.", "Black should map to '@' and white to '.'")

class TestModel2Ascii(unittest.TestCase):
    def setUp(self):
        # Initialize the engine to access its methods
        self.engine = model2ascii.Engine3D(width=80, height=40)

    def test_normalize_mesh_centering(self):
        # Create a large, massively off-center mesh
        vertices = np.array([
            [100, 100, 100],
            [100, 300, 100],
            [300, 100, 100],
            [300, 300, 300]
        ])
        
        normalized = model2ascii.normalize_mesh(vertices)
        
        # Test centering (the mean of all coordinates should be exactly [0, 0, 0])
        center = np.mean(normalized, axis=0)
        np.testing.assert_almost_equal(center, [0, 0, 0], decimal=5, 
                                       err_msg="Mesh was not properly centered to the origin")

    def test_normalize_mesh_scaling(self):
        # Create a massive mesh
        vertices = np.array([
            [-5000, -5000, -5000],
            [5000, 5000, 5000]
        ])
        
        normalized = model2ascii.normalize_mesh(vertices)
        
        # Test scaling (the furthest point from origin should be <= 1.5)
        max_dist = np.max(np.linalg.norm(normalized, axis=1))
        self.assertTrue(max_dist <= 1.5001, "Mesh was not scaled down to fit the terminal screen")

    def test_rotation_matrix_identity(self):
        # A rotation of 0 on all axes should yield an Identity Matrix
        rot_mat = self.engine.get_rotation_matrix(0, 0, 0)
        identity = np.eye(3)
        np.testing.assert_almost_equal(rot_mat, identity, decimal=5,
                                       err_msg="0 rotation did not return an identity matrix")

if __name__ == '__main__':
    unittest.main()
    