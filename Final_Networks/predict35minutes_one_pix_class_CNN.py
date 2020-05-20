import numpy as np
from Final_Networks.predict35minutes_MSE import generate_Data_5_7
from extendet_CNN_test import train_realdata
from NetworkTypes.networkBox import get_CNN_classification
from random import shuffle
import NetworkTypes.tfModels as tfM

def generate_classification(neigbours, print_hist=False, threshold=0.05, only_2004=False, offset=623, duplications=0, two_class=False):
    path = "..\\Data\\samplebundles\\{}_5in_7out_64x64_without_border"
    train, test = generate_Data_5_7(path, only_2004=only_2004)  # 13000 = 4569 18000 = 2904

    all_data = None
    all_label = None
    for bundle in train:
        data, label = bundle.get_all_data_label(channels_Last=True, flatten_output=True)
        if all_data is None:
            all_data = data
            all_label = label
        else:
            all_data = np.concatenate((all_data, data), axis=0)
            all_label = np.concatenate((all_label, label), axis=0)
    print("collected {} samples".format(len(all_data)), "dtype=", type(all_data), all_data.shape)

    posX, posY = 31, 40  # location kn in image
    flattened_pos = 14174  # flattened id for [31][40][6] #6*64*64+posX*64+posY
    new_label = []
    new_data = []
    if two_class:
        countarray = np.zeros(2)
        countarray2 = np.zeros(2)
    else:
        countarray = np.zeros(3)
        countarray2 = np.zeros(3)


    for i in range(len(all_data)):
        if neigbours:
            value = max(all_label[i][13726], all_label[i][14167], all_label[i][14174], all_label[i][14181], all_label[i][14622])
        else:
            value = all_label[i][flattened_pos]
        n_duplications=1
        if i == 623:
            if two_class:
                countarray2 = np.zeros(2)
            else:
                countarray2 = np.zeros(3)
        if two_class:
            tmp = np.zeros(2)
        else:
            tmp = np.zeros(3)

        if value == 0:
            tmp[0] = 1
            countarray[0] += 1
            countarray2[0] += 1
        elif value < threshold:
            if (i >= offset):
                n_duplications +=duplications
            tmp[1] = 1
            countarray[1] += n_duplications
            countarray2[1] += n_duplications
        else:
            if two_class:
                if (i >= offset):
                    n_duplications += duplications
                tmp[1] = 1
                countarray[1] += n_duplications
                countarray2[1] += n_duplications
            else:
                if (i >= offset):
                    n_duplications +=duplications
                tmp[2] = 1
                countarray[2] += n_duplications
                countarray2[2] += n_duplications


        for j in range(n_duplications):
            new_label.append(tmp)
            new_data.append(all_data[i])

    new_label = np.array(new_label)
    new_data = np.array(new_data)

    if print_hist:
        print("Klassen Verteilung aller Daten:", countarray)
        print("Klassen Verteilung der trainings Daten:", countarray2)
        tmp = countarray-countarray2
        print("trivial solution would be at {}% accuracy".format(tmp[0]*100 / np.sum(tmp)))

    return new_data, new_label


if __name__ == '__main__':

    #ToDo: Daten sammeln bzw. Umwandeln mit Nachbarschaftspixeln statt nur dem Konstanz pixel und kn = max (alle in range)

    ### Netz erstellen:
    #model = get_CNN_classification(input_shape=(64, 64, 5))
    model2 = tfM.UNet64(input_shape=(64, 64, 5), simpleclassification=2, lossfunction="categorical_crossentropy", metrics=['accuracy'])

    ### Training vorbereiten:
    data, label = generate_classification(neigbours=True, print_hist=True, duplications=2, two_class=True)
    print("sollte sein (8123,3):",label.shape)

    ## Training starten:
    train_realdata(model2, samplebundle=None, n_epoch=150, savename="UNet_classification_2duplications_neighbours_2classes", channelsLast=True, use_logfile=True,
                   load_last_state=True, n_testsamples=623, data=data, label=label, _eval_output=False)