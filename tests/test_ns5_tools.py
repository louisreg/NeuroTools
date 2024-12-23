import unittest
from neurotools import ns5_tools
import pandas as pd

test_file = './sources/test_ns5_file.ns5'
test_file_header = {'comment': '', 'app_name': '', 'file_type': 'NEURAL', 'timestamp_resolution': 0.0, 'time_span': 12.028, 'time': '00:00:00', 'date': '2000/01/01', 'entity_count': 94}
bad_file_header = {'comment': 'BAD FILE', 'app_name': '', 'file_type': 'NEURAL', 'timestamp_resolution': 0.0, 'time_span': 12.028, 'time': '00:00:00', 'date': '2000/01/01', 'entity_count': 94}
test_file_entities = ['raw 1', 'raw 2', 'raw 3', 'raw 4', 'raw 5', 'raw 6', 'raw 7', 'raw 8', 'raw 9', 'raw 10', 'raw 11', 'raw 12', 'raw 13', 'raw 14', 'raw 15', 'raw 16', 'raw 17', 
                      'raw 18', 'raw 19', 'raw 20', 'raw 21', 'raw 22', 'raw 23', 'raw 24', 'raw 25', 'raw 26', 'raw 27', 'raw 28', 'raw 29', 'raw 30', 'raw 31', 'raw 32', 'raw 129', 
                      'raw 130', 'raw 131', 'raw 132', 'raw 133', 'raw 134', 'raw 135', 'raw 136', 'raw 137', 'raw 138', 'raw 139', 'raw 140', 'raw 141', 'raw 142', 'raw 143', 'raw 144', 
                      'raw 145', 'raw 146', 'raw 147', 'raw 148', 'raw 149', 'raw 150', 'raw 151', 'raw 152', 'raw 153', 'raw 154', 'raw 155', 'raw 156', 'raw 157', 'raw 158', 'raw 159', 
                      'raw 160', 'Tr0 ', 'Tr1 ', 'analog 3', 'analog 4', 'Fx ', 'analog 6', 'Fy ', 'analog 8', 'Fz ', 'analog 10', 'Mx ', 'analog 12', 'My ', 'analog 14', 'Mz ', 'analog 16',
                        'analog 17', 'analog 18', 'analog 19', 'analog 20', 'analog 21', 'analog 22', 'analog 23', 'analog 24', 'analog 25', 'analog 26', 'analog 27', 'analog 28', 'analog 29', 'analog 30']

bad_test_file_entities = ['raw 100', 'raw 2', 'raw 3', 'raw 4', 'raw 5', 'raw 6', 'raw 7', 'raw 8', 'raw 9', 'raw 10', 'raw 11', 'raw 12', 'raw 13', 'raw 14', 'raw 15', 'raw 16', 'raw 17', 
                      'raw 18', 'raw 19', 'raw 20', 'raw 21', 'raw 22', 'raw 23', 'raw 24', 'raw 25', 'raw 26', 'raw 27', 'raw 28', 'raw 29', 'raw 30', 'raw 31', 'raw 32', 'raw 129', 
                      'raw 130', 'raw 131', 'raw 132', 'raw 133', 'raw 134', 'raw 135', 'raw 136', 'raw 137', 'raw 138', 'raw 139', 'raw 140', 'raw 141', 'raw 142', 'raw 143', 'raw 144', 
                      'raw 145', 'raw 146', 'raw 147', 'raw 148', 'raw 149', 'raw 150', 'raw 151', 'raw 152', 'raw 153', 'raw 154', 'raw 155', 'raw 156', 'raw 157', 'raw 158', 'raw 159', 
                      'raw 160', 'Tr0 ', 'Tr1 ', 'analog 3', 'analog 4', 'Fx ', 'analog 6', 'Fy ', 'analog 8', 'Fz ', 'analog 10', 'Mx ', 'analog 12', 'My ', 'analog 14', 'Mz ', 'analog 16',
                        'analog 17', 'analog 18', 'analog 19', 'analog 20', 'analog 21', 'analog 22', 'analog 23', 'analog 24', 'analog 25', 'analog 26', 'analog 27', 'analog 28', 'analog 29', 'analog 30']

sub_list_entities = ['raw 1', 'raw 2', 'raw 3', 'raw 4', 'raw 5', 'raw 6', 'raw 7', 'raw 8', 'Fz ']
save_path = "./output/"
save_file = save_path + "test.hdf5"
test_sampling_rate = 30_000.0
test_n_samples = 360840
class TestOpenning(unittest.TestCase):
    def test_open_OK(self):
        ns5file = ns5_tools.ns5Files(test_file)

    def test_open_NOK(self):
        with self.assertRaises(ns5_tools.InvalidFile): 
            ns5_tools.ns5Files('no_file.ns5')

    def test_open_wrong_extension_NOK(self):
        with self.assertRaises(ns5_tools.InvalidFileExtension): 
            ns5_tools.ns5Files('no_file')

class Test_getInfo_Labels(unittest.TestCase):
    def test_get_file_info_OK(self):
        ns5file = ns5_tools.ns5Files(test_file)
        self.assertEqual(ns5file.get_file_info(), test_file_header)

    def test_get_file_info_NOK(self):
        ns5file = ns5_tools.ns5Files(test_file)
        self.assertNotEqual(ns5file.get_file_info(), bad_file_header)

    def test_get_analog_label_entities_OK(self):
        ns5file = ns5_tools.ns5Files(test_file)
        self.assertEqual(ns5file.get_analog_entitie_labels(), test_file_entities)

    def test_get_analog_label_entities_NOK(self):
        ns5file = ns5_tools.ns5Files(test_file)
        self.assertNotEqual(ns5file.get_analog_entitie_labels(), bad_test_file_entities)
    
    def test_get_sampling_rate(self):
        ns5file = ns5_tools.ns5Files(test_file)
        self.assertEqual(ns5file.get_sampling_rate(), test_sampling_rate)

    def test_get_sampling_rate(self):
        ns5file = ns5_tools.ns5Files(test_file)
        self.assertEqual(ns5file.get_n_samples(), test_n_samples)

    def test_get_time_vector(self):
        ns5file = ns5_tools.ns5Files(test_file)
        ns5file.get_time_vector()

class Test_getAnalogData(unittest.TestCase):
    def test_get_analog_data_OK(self):
        ns5file = ns5_tools.ns5Files(test_file)
        entitites = ns5file.get_analog_entitie_labels()
        ns5file.get_analog_entitie(entitites[0])

    def test_get_analog_data_OK(self):
        ns5file = ns5_tools.ns5Files(test_file)
        with self.assertRaises(ns5_tools.UnknownAnalogLabelException): 
            ns5file.get_analog_entitie('nope')
          
class Test_to_hdf(unittest.TestCase):
    def test_all_labels(self):
        ns5file = ns5_tools.ns5Files(test_file)
        ns5file.to_hdf(save_file)
        df = pd.read_hdf(save_file)
        list_t = ns5file.get_analog_entitie_labels()
        list_t.append("time")
        self.assertEqual(list(df.keys()),list_t)
    
    def test_sublist_labels(self):
        ns5file = ns5_tools.ns5Files(test_file)
        ns5file.to_hdf(save_file,sub_list_entities)
        df = pd.read_hdf(save_file)
        list_t = ns5file.get_analog_entitie_labels()
        list_t.append("time")
        sub_list_entities.append("time")
        self.assertNotEqual(list(df.keys()),list_t)
        self.assertEqual(list(df.keys()),sub_list_entities)


if __name__ == '__main__':
    unittest.main()