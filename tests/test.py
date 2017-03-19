import unittest
import parent_elements as pe

class TestParentElementSearch(unittest.TestCase):
    'Tests Search for parent element'
    feature = {}
    endpoints = [{(1,0):['GUID1'], }
    def test_search(self):
        self.assertIsNone(pe.search_end_points(feature, end_points))

if __name__ == '__main__':
    unittest.main()