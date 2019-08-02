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
        continue
    print(confusion)
    return



if __name__ == '__main__':
    #Lernkurve:
    eval_trainlogfile("./trainphase.log", plot=True)

    #DatenSammeln
    data, label = generate_classification(False, only_2004=True, print_hist=True)
    val_data = data[:623]
    val_lbl = label[:623]

    #NetzLaden
    net,offset = load_last_net("CNN_classification")
    assert net is not None

    eval_validationSet(val_data, val_lbl, net)
    #ToDo Validieren
    #confusion Matrix, sieht man eine schöne Einheitsmatrix =P ?
    #2D Plot korrelations plot pro Klasse mit Sicherheit und tatsächlicher Klasse (sieht man bei unsicherem ist es andere Klasse?
