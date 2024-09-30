import unittest
from neurotools import ns5_tools

test_file = './sources/test_ns5_file.ns5'
test_file_header = {'comment': '', 'app_name': '', 'file_type': 'NEURAL', 'timestamp_resolution': 0.0, 'time_span': 4.062, 'time': '00:00:00', 'date': '2000/01/01', 'entity_count': 62}
bad_file_header = {'comment': '', 'app_name': '', 'file_type': 'NEURAL', 'timestamp_resolution': 1.0, 'time_span': 4.062, 'time': '00:00:00', 'date': '2000/01/01', 'entity_count': 62}
test_file_entities = ['raw 1', 'raw 2', 'raw 3', 'raw 4', 'raw 5', 'raw 6', 'raw 7', 'raw 8', 'raw 9', 'raw 10', 'raw 11', 'raw 12', 'raw 13', 'raw 14', 'raw 15', 'raw 16', 'raw 17', 
                      'raw 18', 'raw 19', 'raw 20', 'raw 21', 'raw 22', 'raw 23', 'raw 24', 'raw 25', 'raw 26', 'raw 27', 'raw 28', 'raw 29', 'raw 30', 'raw 31', 'raw 32', 'Tr0 ', 
                      'Tr1 ', 'analog 3', 'analog 4', 'Fx ', 'analog 6', 'Fy ', 'analog 8', 'Fz ', 'analog 10', 'Mx ', 'analog 12', 'My ', 'analog 14', 'Mz ', 'analog 16', 'analog 17', 
                      'analog 18', 'analog 19', 'analog 20', 'analog 21', 'analog 22', 'analog 23', 'analog 24', 'analog 25', 'analog 26', 'analog 27', 'analog 28', 'analog 29', 'analog 30']

bad_test_file_entities = ['raw 100', 'raw 2', 'raw 3', 'raw 4', 'raw 5', 'raw 6', 'raw 7', 'raw 8', 'raw 9', 'raw 10', 'raw 11', 'raw 12', 'raw 13', 'raw 14', 'raw 15', 'raw 16', 'raw 17', 
                      'raw 18', 'raw 19', 'raw 20', 'raw 21', 'raw 22', 'raw 23', 'raw 24', 'raw 25', 'raw 26', 'raw 27', 'raw 28', 'raw 29', 'raw 30', 'raw 31', 'raw 32', 'Tr0 ', 
                      'Tr1 ', 'analog 3', 'analog 4', 'Fx ', 'analog 6', 'Fy ', 'analog 8', 'Fz ', 'analog 10', 'Mx ', 'analog 12', 'My ', 'analog 14', 'Mz ', 'analog 16', 'analog 17', 
                      'analog 18', 'analog 19', 'analog 20', 'analog 21', 'analog 22', 'analog 23', 'analog 24', 'analog 25', 'analog 26', 'analog 27', 'analog 28', 'analog 29', 'analog 30']


class TestOpenning(unittest.TestCase):

    def test_open_OK(self):
        self.assertEqual(ns5_tools.call_ns5_py2(test_file), '')

    def test_open_NOK(self):
        with self.assertRaises(Exception) as context:
            ns5_tools.call_ns5_py2('no_file')
        self.assertTrue('could not find any .nev or .nsx files matching ' in str(context.exception))

    def test_get_file_info_OK(self):
        self.assertEqual(ns5_tools.get_file_info(test_file), test_file_header)

    def test_get_file_info_NOK(self):
        self.assertNotEqual(ns5_tools.get_file_info(test_file), bad_file_header)

    def test_get_analog_label_entities_OK(self):
        self.assertEqual(ns5_tools.get_analog_label_entities(test_file), test_file_entities)

    def test_get_analog_label_entities_NOK(self):
        self.assertNotEqual(ns5_tools.get_analog_label_entities(test_file), bad_test_file_entities)

class Test_getInfos(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()