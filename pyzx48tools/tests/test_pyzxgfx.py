
import unittest
from pyzx48tools import zxgfx

class TestZX(unittest.TestCase):
    def test1(self):
        zx = zxgfx()
        self.assertEqual(1, 2)

if __name__ == "__main__":
    unittest.main()
