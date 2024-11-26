import sys, os
from datetime import datetime
sys.path.append("../../")

from neurotools.Neurostimulator.TwistLogger import log

"""log_path = "./sources/SweepStim_APP_17_13_17_ GM1_NGM3_BA_R12.json"
test_log = log(log_path)

for step in test_log.steps:
    print(step.stimulation_amp)"""


log_path = "./sources/Stim_and_Rest_ContinuousRamp_APP_19_30_58.csv"
test_log = log(log_path)

for step in test_log.steps:
    print(step.start_time)
    print(step.stop_time)
#print(test_log.steps[0].start_time)

