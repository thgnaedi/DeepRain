from Data.evaluate_Network_on_realData import eval_trainlogfile
from NetworkTypes.extendet_CNN_test import load_last_net
import Final_Networks.eval_1D_classification_anyNet as eval_1d
import Data.evaluate_Network_on_realData
import numpy as np
import matplotlib.pyplot as plt


def generate_classification(neighbors,
                            print_hist=False,
                            threshold=0.05,
                            only_2014=False,
                            offset=623,
                            duplications=0):
    pass


def eval_validationSet(data, label, net):
    prediction = net.predict(data)
    print(data.shape)
    print(prediction.shape)
    print(label.shape)
    get_confusion_matrix_2d(label, prediction)
    eval_1d.correlation_plots(label, prediction)
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
    samples, classes = _true.shape
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
