import unittest

import common_types


class TestCommonTypes(unittest.TestCase):
    def test_distance(self):
        a = common_types.Coordinates(3, 4)
        b = common_types.Coordinates(7, 8)
        self.assertEqual(common_types.distance(a, b), 8)


if __name__ == '__main__':
    unittest.main()
