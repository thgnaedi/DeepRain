import NetworkTypes.tfModels as tfM
import sys
sys.path.append("../Data")
sys.path.append("../NetworkTypes")
import Data.sample_bundle as sampleBundle
from NetworkTypes.extendet_CNN_test import train_realdata
import numpy as np
import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"


def categorize_data(data):
    if len(data.shape) == 3:
        return _categorize_data(data)
    else:
        new_data = map(categorize_data, data)
        return np.array(new_data)


def _categorize_data(data):
    new_label_shape = data.shape[:-1] + (3,)
    print(new_label_shape)
    labels = np.zeros(new_label_shape, data.dtype)

    for idx , value in np.ndenumerate(data):
        if value <= 20:
            label = np.array([1, 0, 0])
        elif value <= 40:
            label = np.array([0, 1, 0])
        else:
            label = np.array([0, 0, 1])
        labels[idx] = label
    return labels


def main():
    input_shape = (64, 64, 5)
    model = tfM.UNet64(input_shape)

    sb = sampleBundle.load_Sample_Bundle("../Data/RegenTage2016")

    data, label = sb.get_all_data_label(channels_Last=True, flatten_output=True)
    label = categorize_data(data)
    n_testsamples = 50
    #x_train, y_train = data[n_testsamples:], label[n_testsamples:]
    #x_test, y_test = data[:n_testsamples], label[:n_testsamples]

    train_realdata(model,
                   sb,
                   n_epoch=80,
                   savename="{FEHLERFUNKTIONSNAME}",
                   channelsLast=True,
                   use_logfile=True,
                   load_last_state=True)


if __name__ == "__main__":
    main()
