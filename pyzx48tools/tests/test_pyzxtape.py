
import unittest
from pyzx48tools import pyzxtape

class TestZX(unittest.TestCase):
    def test1(self):
        zx = zxtape()
        self.assertEqual(1, 2)

if __name__ == "__main__":
    unittest.main()
