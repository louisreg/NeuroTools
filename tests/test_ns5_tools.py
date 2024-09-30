import unittest
from neurotools import ns5_tools

test_file = './sources/test_ns5_file.ns5'

class TestOpenning(unittest.TestCase):

    def test_open_OK(self):
        self.assertEqual(ns5_tools.call_ns5_py2(test_file), '')

    def test_open_NOK(self):
        with self.assertRaises(Exception) as context:
            ns5_tools.call_ns5_py2('no_file')
        self.assertTrue('could not find any .nev or .nsx files matching ' in str(context.exception))

class Test_getInfos(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()