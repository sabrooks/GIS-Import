import unittest
import pickle
import functions.function_factory as ff

with open('tests/examples/example_elements.p', 'rb') as f:
        FEATURES = pickle.load(f)

[ff.make_basic_feature(feature) for _, feature in FEATURES.items()]

class BasicFeature(unittest.TestCase):

    def test_basic_process(self):
        self.assertTrue(EXAMPLES is dict)

if __name__ == '__main__':
    unittest.main()