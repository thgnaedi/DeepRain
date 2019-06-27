import NetworkTypes.tfModels as tfM
import sys
sys.path.append("../Data")
sys.path.append("../NetworkTypes")
import Data.sample_bundle as sampleBundle
from NetworkTypes.extendet_CNN_test import train_realdata


input_shape = (64, 64, 5)
model = tfM.UNet64(input_shape)

sb = sampleBundle.load_Sample_Bundle("../Data/RegenTage2016")

data, label = sb.get_all_data_label(channels_Last=True, flatten_output=True)
n_testsamples = 50
x_train, y_train = data[n_testsamples:], label[n_testsamples:]
x_test, y_test = data[:n_testsamples], label[:n_testsamples]

train_realdata(model, sb, n_epoch=80, savename="{FEHLERFUNKTIONSNAME}", channelsLast=True, use_logfile=True, load_last_state=True)
