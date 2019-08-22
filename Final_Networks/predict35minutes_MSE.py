import Data.sample_bundle as sample_bundle
import NetworkTypes.tfModels as tfM
from NetworkTypes.extendet_CNN_test import train_realdata
import sys
import numpy as np
import matplotlib.pyplot as plt


# ToDo: 2013 ist durchschnittsjahr =)
def generate_Data_5_7(path, sum=7500, invalid_value=80, only_2004=False):
    trainbundles = []
    testbundle = None
    print("generiere Samples von 2004-2017 ...")
    for year in range(2004, 2018):
        sb = sample_bundle.load_Sample_Bundle(path.format(year))
        sys.stdout.write(" clear")
        sys.stdout.flush()
        b = sb.clear_by_sum(sum)  # 2017 hat anderen Grenzwert
        #plt.hist(b,bins=100)
        #plt.show()
        #sb.replace_borders(invalid_value)   #entferne Radarfreie Zonen
        sys.stdout.write(" normalize")
        sys.stdout.flush()
        sb.normalize()  # normalisieren zwischen [0;1]

        sys.stdout.write("\r|{}{}|".format('##' * (year - 2003), '  ' * (13 - (year - 2003))))
        sys.stdout.flush()

        trainbundles.append(sb)
        if only_2004:
            break

    print("\tfinished")
    return trainbundles, testbundle


if __name__ == '__main__':

    ### Einsammeln aller Samples mit anschließendem Normieren:
    #path = "..\\Data\\samplebundles\\{}_5in_7out_64x64_without_border"
    path = "..\\Data\\samplebundles\\{}_5in_7out_64x64_without_border"
    train, test = generate_Data_5_7(path)    #13000 = 4569 18000 = 2904

    # True nur, beim aussuchen einer guten image ID:
    if False:
        index=0
        sb = train[0]
        data,label = sb.get_all_data_label(True)
        for dl in data:
            print(index)
            print(np.sum(dl[:,:,0]))
            if np.max(dl[:,:,0]) > 0.5:
                plt.imshow(dl[:,:,0], cmap="gray", vmax=1)
                plt.show()
            index += 1

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
    train_realdata(model, samplebundle=None, n_epoch=300, savename="10years", channelsLast=True, use_logfile=True,
                   load_last_state=True, n_testsamples=623, prediction_shape=(64, 64, 7), PREDICTION_IMG_ID=413, data=all_data,
                   label=all_label)
