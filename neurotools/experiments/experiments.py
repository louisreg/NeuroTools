from abc import ABC

class experiment(ABC):
    def something(self):
        pass

class Activation_exp(experiment):
    def something(self):
        pass

class MonopolarActivation_exp(Activation_exp):
    pass

class BipolarActivation_exp(Activation_exp):
    pass

def create_experiment(template: str, save_path: str) -> experiment:
    #get_exp_tag()
    #get_electrodes()
    #get_impedance_files()
    #get_SD_curves()
    #create_folder()
    #create_summary_csv()
    

    pass

-> create from xls 
    -> 
exp : 
    - folder 
    - ns5 file list
    - elect name + impedance file 
    - log file 
    - SD curve


folder name: ns5 template 