from Data.evaluate_Network_on_realData import eval_trainlogfile
from NetworkTypes.extendet_CNN_test import load_last_net
import NetworkTypes.loss_function_test_etienne
import Data.evaluate_Network_on_realData
import numpy as np
import matplotlib.pyplot as plt


def correlation_plots(_true, _pred, classnames = ["kein Regen", "Regen", "stark Regen"]):
    samples, x, y, classes = _true.shape
    print("True shape: {}".format(_true.shape))
    print("Prediction shape: {}".format(_pred.shape))
    assert classes == 3  # other classifications currently not supported

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


def generate_classification():
    all_data, all_label = NetworkTypes.loss_function_test_etienne.load_all_year_data()
    all_label = NetworkTypes.loss_function_test_etienne.categorize_data(all_label)
    return all_data, all_label


def eval_validation_set(data, label, net):
    prediction = net.predict(data)

    target_shape = (623, 64, 64, 3)
    prediction = prediction.reshape(target_shape)
    label = label.reshape(target_shape)
    print("Data shape: {}".format(data.shape))
    print("Prediction shape: {}".format(prediction.shape))
    print("Label shape: {}".format(label.shape))

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
# --------|------------|-------------|-----------
# k.Regen |            |             |
# w.Regen |            |             |
# v.Regen |            |             |
def get_confusion_matrix_2d(_true, _pred):
    print("True-shape: {}".format(_true.shape))
    print("Pred-Shape: {}".format(_pred.shape))
    # samples, classes = _true.shape
    num_samples, x_dim, y_dim, classes = _true.shape

    confusion = np.zeros((classes, classes), dtype=int)
    # c[i][:] = true class
    # c[:][i] = prediction

    for idx, value in np.ndenumerate(_true):
        true_class = get_category(value)
        pred_class_highest_probability = np.argmax(_pred[idx])
        x = np.where(pred_class_highest_probability)
        y = np.where(value == 0)

        confusion[y][x] += 1

    print(confusion)
    return confusion


def main():
    # Lernkurve:
    eval_trainlogfile("..\\Data\\Training\\activationHidden-tanh_activationOutput-softmax\\trainphase.log", plot=True)

    # DatenSammeln
    data, label = generate_classification()
    val_data = data[:623]
    val_lbl = label[:623]

    # NetzLaden
    netname = "categorical_crossentropy_hidden-tanh_output-softmax_above"
    net, offset = load_last_net(netname, _dir="..\\Data\\Training\\activationHidden-tanh_activationOutput-softmax")
    assert net is not None

    eval_validation_set(val_data, val_lbl, net)
    plt.show()
    # ToDo Validieren
    # confusion Matrix, sieht man eine schöne Einheitsmatrix =P ?
    # 2D Plot korrelations plot pro Klasse mit Sicherheit und tatsächlicher Klasse
    # (sieht man bei unsicherem ist es andere Klasse?


if __name__ == '__main__':
    main()

    # Evaluate training of UNet with Activation functions: hidden layers: TanH, output layer: softmax
    Data.evaluate_Network_on_realData.eval_trainlogfile("..\\Data\\Training\\activationHidden-tanh_activationOutput-softmax\\trainphase.log", plot=True)

    # Evaluate training of UNet with Activation functions: hidden layers: softmax, output layer: softmax
    Data.evaluate_Network_on_realData.eval_trainlogfile("..\\Data\\Training\\activationHidden-softmax_activationOutput-softmax\\trainphase.log", plot=True)
