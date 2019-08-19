from Final_Networks.predict35minutes_one_pix_class_CNN import generate_classification
from Data.evaluate_Network_on_realData import eval_trainlogfile
from Final_Networks.predict35minutes_MSE import generate_Data_5_7
from NetworkTypes.extendet_CNN_test import load_last_net
import numpy as np
import matplotlib.pyplot as plt

def eval_validationSet(data, label, net):
    firstdim = data.shape[0]
    prediction = net.predict(data)
    print(data.shape)
    print(prediction.shape)
    print(label.shape)
    get_confusionMatrix(label, prediction)
    correlation_plots(label, prediction)

    return

def get_confusionMatrix(_true, _pred):
    samples, classes = _true.shape

    confusion = np.zeros((classes,classes), dtype=int)
    # c[i][:] = true class
    # c[:][i] = prediction
    # Y-Achse = Kl 0-2 (von oben) X-Achse = Pred 0-2 (von links)

    for i in range(samples):
        x = np.argmax(_pred[i])
        y = np.where(_true[i] == 1)[0][0]   #returns index of first '1' in vector
        confusion[y][x] += 1

    print(confusion)
    return

def correlation_plots(_true, _pred, classnames = ["kein Regen", "Regen", "stark Regen"]):
    samples, classes = _true.shape
    assert classes == 3 # other classifications currently not supported

    prob_values = [[],[],[]]
    reality = [[],[],[]]

    for i in range(samples):
        klasse = np.argmax(_pred[i])
        sicherheit = _pred[i]
        label = np.where(_true[i] == 1)[0][0]  # returns index of first '1' in vector
        if sicherheit[klasse] < 0.1:
           print("Achtung:", sicherheit)
        prob_values[klasse].append(sicherheit[klasse])
        reality[klasse].append(label)

    for i in range(classes):
        plt.figure("predicted class {} | samples: {}".format(classnames[i], len(prob_values[i])))
        plt.plot(prob_values[i], reality[i], "r*")
    return

if __name__ == '__main__':
    #Lernkurve:
    eval_trainlogfile("./trainphase.log", plot=True)

    #DatenSammeln
    data, label = generate_classification(neigbours=True, only_2004=True, print_hist=True, )
    val_data = data[:623]
    val_lbl = label[:623]

    #NetzLaden
    netname = "CNN_classification"
    netname = "CNN_classification_2duplications_neighbours"
    netname = "UNet_classification_2duplications_neighbours"
    #netname = "UNet_classification_2duplications_neighbours_2classes"
    net,offset = load_last_net(netname)
    assert net is not None

    eval_validationSet(val_data, val_lbl, net)
    plt.show()
    #ToDo Validieren
    #confusion Matrix, sieht man eine schöne Einheitsmatrix =P ?
    #2D Plot korrelations plot pro Klasse mit Sicherheit und tatsächlicher Klasse (sieht man bei unsicherem ist es andere Klasse?
