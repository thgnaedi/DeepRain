from Final_Networks.predict35minutes_one_pix_class_CNN import generate_classification
from Data.evaluate_Network_on_realData import eval_trainlogfile
from NetworkTypes.extendet_CNN_test import load_last_net
import Data.evaluate_Network_on_realData
import numpy as np
import matplotlib.pyplot as plt


def eval_validationSet(data, label, net):
    firstdim = data.shape[0]
    prediction = net.predict(data)
    print(data.shape)
    print(prediction.shape)
    print(label.shape)
    get_confusion_matrix_2d(label, prediction)
    correlation_plots(label, prediction)
    return


def get_category(value, bit_rainy_border=8):
    if value == 0:
        return np.array([1, 0, 0])
    elif value <= bit_rainy_border:
        return np.array([0, 1, 0])
    else:
        return np.array([0, 0, 1])


# tr/pred | kein Regen | wenig Regen | viel Regen
# ---------|------------|-------------|-----------
# k.Regen |            |             |
# w.Regen |            |             |
# v.Regen |            |             |
def get_confusion_matrix_2d(_true, _pred):
    index, classes = _true.shape
    #num_samples, x_dim, y_dim, classes = _true.shape

    confusion = np.zeros((classes, classes), dtype=int)
    # c[i][:] = true class
    # c[:][i] = prediction

    for sample, x, y, value in np.ndenumerate(_true):
        true_class = get_category(value)
        pred_class_highest_probability = np.argmax(_pred[sample, x, y])
        x = np.where(pred_class_highest_probability)
        y = np.where(value == 0)

        confusion[y][x] += 1

    print(confusion)
    return confusion


def correlation_plots(_true, _pred, classnames = ["kein Regen", "Regen", "stark Regen"]):
    samples, classes = _true.shape
    assert classes == 3 # other classifications currently not supported

    prob_values = [[], [], []]
    reality = [[], [], []]

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
    eval_trainlogfile("..\\Data\\Training\\activationHidden-tanh_activationOutput-softmax\\trainphase.log", plot=True)

    #DatenSammeln
    data, label = generate_classification(False, only_2004=True, print_hist=True)
    val_data = data[:623]
    val_lbl = label[:623]

    #NetzLaden
    #netname = "CNN_classification"
    netname = "categorical_crossentropy_hidden-tanh_output-softmax_above"
    net, offset = load_last_net(netname, _dir="..\\Data\\Training\\activationHidden-tanh_activationOutput-softmax")
    assert net is not None

    eval_validationSet(val_data, val_lbl, net)
    plt.show()
    #ToDo Validieren
    #confusion Matrix, sieht man eine schöne Einheitsmatrix =P ?
    #2D Plot korrelations plot pro Klasse mit Sicherheit und tatsächlicher Klasse (sieht man bei unsicherem ist es andere Klasse?



# Evaluate training of UNet with Activation functions: hidden layers: TanH, output layer: softmax
Data.evaluate_Network_on_realData.eval_trainlogfile("..\\Data\\Training\\activationHidden-tanh_activationOutput-softmax\\trainphase.log", plot=True)

# Evaluate training of UNet with Activation functions: hidden layers: softmax, output layer: softmax
Data.evaluate_Network_on_realData.eval_trainlogfile("..\\Data\\Training\\activationHidden-softmax_activationOutput-softmax\\trainphase.log", plot=True)
