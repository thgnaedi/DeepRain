import sample_bundle
import tfModels as tfM
from extendet_CNN_test import train_realdata
import sys
import numpy as np


# ToDo: 2013 ist durchschnittsjahr =)
def generate_Data_5_7(sum=76100):
    trainbundles = []
    testbundle = None
    print("generiere Samples von 2008-2017 ...")
    for year in range(2008, 2018):
        sb = sample_bundle.load_Sample_Bundle("..\\Data\\samplebundles\\{}_5in_7out_64x64".format(year))
        if year == 2017:
            sb.clear_by_sum(30100)  # 2017 hat anderen Grenzwert
        else:
            sb.clear_by_sum(sum)  # bereinigen von zu geringen niederschlagsmengen
        sb.normalize()  # normalisieren zwischen [0;1]

        sys.stdout.write("\r|{}{}|".format('##' * (year - 2007), '  ' * (10 - (year - 2007))))
        sys.stdout.flush()

        if year == 2013:
            testbundle = sb
        else:
            trainbundles.append(sb)
    print("\tfinished")
    return trainbundles, testbundle


if __name__ == '__main__':

    ### Einsammeln aller Samples mit anschließendem Normieren:
    train, test = generate_Data_5_7()

    ### Netz erstellen:
    model = tfM.UNet64(input_shape=(64, 64, 5), n_predictions=7, lossfunction="mean_squared_error")

    ### Training vorbereiten:
    all_data = None
    all_label = None
    for bundle in train:
        data, label = bundle.get_all_data_label(channels_Last=True, flatten_output=True)
        if all_data is None:
            all_data = data
            all_label = label
        else:
            all_data = np.concatenate((all_data,data), axis=0)
            all_label = np.concatenate((all_label, label), axis=0)
    print("collected {} samples for training, 2013 excluded!".format(len(all_data)))

    ## Training starten:
    train_realdata(model, samplebundle=None, n_epoch=10, savename="10years", channelsLast=True, use_logfile=True,
                   load_last_state=True, n_testsamples=365, prediction_shape=(64, 64, 7), PREDICTION_IMG_ID=1245, data=all_data,
                   label=all_label)
