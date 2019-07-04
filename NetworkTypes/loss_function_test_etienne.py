import NetworkTypes.tfModels as tfM
import sys
sys.path.append("../Data")
sys.path.append("../NetworkTypes")
import Data.sample_bundle as sampleBundle
from NetworkTypes.extendet_CNN_test import train_realdata
import numpy as np
import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"


def categorize_data(label):
    n_samples = len(label)
    label = label.reshape(n_samples, 64, 64)
    print("Old shape: {}".format(label.shape))
    new_label_shape = label.shape + (3,)
    labels = np.zeros(new_label_shape, label.dtype)

    for idx, value in np.ndenumerate(label):
        if value == 0:
            labels[idx] = np.array([1, 0, 0])
        elif value <= 10:
            labels[idx] = np.array([0, 1, 0])
        else:
            labels[idx] = np.array([0, 0, 1])
    labels = labels.reshape(n_samples, 4096*3)
    print("New shape: {}".format(labels.shape))
    return labels


def main():
    input_shape = (64, 64, 5)
    #https://stackoverflow.com/questions/50395170/multi-label-classification-loss-function
    #https://www.i2tutorials.com/machine-learning-using-tensorflow-tutorial/tensorflow-loss-function/
    model = tfM.UNet64(input_shape,
                       n_predictions=3,
                       lossfunction="categorical_crossentropy",
                       activation_hidden="tanh",
                       activation_output="softmax",
                       metrics=["categorical_accuracy"])

    sb = sampleBundle.load_Sample_Bundle("../Data/RegenTage2016")

    data, label = sb.get_all_data_label(channels_Last=True, flatten_output=True)
    print("Original label shape: {}".format(label.shape))
    label = categorize_data(label)
    n_testsamples = 50
    x_train, y_train = data[n_testsamples:], label[n_testsamples:]
    print("Data shape: {}".format(x_train.shape))
    print("Label shape: {}".format(y_train.shape))
    #x_test, y_test = data[:n_testsamples], label[:n_testsamples]

    train_realdata(model=model,
                   samplebundle=None,
                   n_epoch=80,
                   savename="categorical_crossentropy_0-20_20-40_above",
                   channelsLast=True,
                   use_logfile=True,
                   load_last_state=True,
                   prediction_shape=(64, 64, 3),
                   data=data,
                   label=label,
                   _eval_output=True)


if __name__ == "__main__":
    main()
