import sys
sys.path.append("../../")

from neurotools.experiments.log2ns5 import generate_xls_matching,validate_all_timings,match_ns5_template
from neurotools.ns5_tools.ns5_tools import ns5Files
from neurotools.Neurostimulator.TwistLogger import log
from neurotools.utils.files import list_files_in_subdir
from datetime import datetime
i = 1
"""
for i in range (34):
    idx = str(i+1).zfill(4)
    data_path = f'/Users/louisregnacq/Documents/Work/DataArchive/UARK_experiments/20220607/UA013_BLK_ROAS_BGM0_15khz_5ms_{idx}.ns5'
    log_path = '/Users/louisregnacq/Documents/Work/DataArchive/UARK_experiments/20220607/log_Jun_07_2022/Stim_and_Rest_ContinuousRamp_APP_20_34_23.csv'

    ns = ns5Files(data_path)
    log_t = log(log_path)
    print(f"{log_t.steps[i].start_time} - {ns.datetime}")
    log_datetime = datetime.combine(ns.datetime.date(), log_t.steps[i].start_time)
    print(f"delta: {abs(ns.datetime-log_datetime)}")
    #print(validate_timing(log_t.steps[i], data_path))
    #print(data_path)"""

"""template = f'/Users/louisregnacq/Documents/Work/DataArchive/UARK_experiments/20220607/UA013_BLK_ROAS_BGM0_15khz_5ms_'
data_path = '/Users/louisregnacq/Documents/Work/DataArchive/UARK_experiments/20220607/'
log_path = '/Users/louisregnacq/Documents/Work/DataArchive/UARK_experiments/20220607/log_Jun_07_2022/Stim_and_Rest_ContinuousRamp_APP_20_34_23.csv'
log_t = log(log_path)
ns5_files = list_files_in_subdir(data_path,".ns5")
ns5_files = match_ns5_template(template,ns5_files)

print(validate_all_timings(log_t,ns5_files))"""

data_path = '/Users/louisregnacq/Documents/Work/DataArchive/UARK_experiments/20220601/'
generate_xls_matching(data_path, xlx_path="./outputs/")
