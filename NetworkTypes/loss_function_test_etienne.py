import NetworkTypes.tfModels as tfM
import Data.sample_bundle as sampleBundle
import sys
import os
from NetworkTypes.extendet_CNN_test import train_realdata

sys.path.append("../Data")

input_shape = (64, 64, 5)
model = tfM.UNet64(input_shape)

print(os.getcwd())
sb = sampleBundle.load_Sample_Bundle("../Data/RegenTage2016")

data, label = sb.get_all_data_label(channels_Last=True, flatten_output=True)
n_testsamples = 50
x_train, y_train = data[n_testsamples:], label[n_testsamples:]
x_test, y_test = data[:n_testsamples], label[:n_testsamples]

train_realdata(model, sb, n_epoch=80, savename="{FEHLERFUNKTIONSNAME}", channelsLast=True, use_logfile=True, load_last_state=True)
