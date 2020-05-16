from dummy_datagenerator import generate_one_sample, plot_6_images, eval_output
import networkBox
import numpy as np
import keras
from keras.models import load_model

N_INPUTS = 5
input_shape = (N_INPUTS, 100, 100) #Channels First!

# ToDo: Netz abspeichern nach Trainieren, damit es auf VM laufen kann
# ToDo: Abgespeichertes Netz laden und auswerten
# ToDo: Gridsearch, sinnvolle Parameter finden, bisher ergebnis super schlecht =C

def generate_Dataset(n_train, n_test, diffToLabel=2, channelsLast=False, n_inputs=N_INPUTS):
    xtrain = []
    ytrain = []
    for i in range(n_train):
        data, label = generate_one_sample((100,100), n_inputs, schrittweite=10, pad=diffToLabel, channelsLast=channelsLast)
        xtrain.append(data)
        ytrain.append(label.flatten())
    xtest = []
    ytest = []
    for i in range(n_test):
        data, label = generate_one_sample((100, 100), N_INPUTS, schrittweite=10, pad=diffToLabel, channelsLast=channelsLast)
        xtest.append(data)
        ytest.append(label.flatten())
    return np.array(xtrain), np.array(ytrain), np.array(xtest), np.array(ytest)


def train_model(model, diffToLabel=2, batch_size=100, epochs = 4, savename=None, n_train=4000, channelsLast=False, n_inputs=N_INPUTS):
    x_train, y_train, x_test, y_test = generate_Dataset(n_train=n_train, n_test=100, diffToLabel=diffToLabel, channelsLast=channelsLast, n_inputs=n_inputs)
    model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, verbose=1, validation_data=(x_test, y_test))

    score = model.evaluate(x_test, y_test, verbose=0)
    print("score:",score)
    #print('Test loss:', score[0])
    #print('Test accuracy:', score[1])
    if savename is not None:
        model.save(savename+'.h5')  # creates a HDF5 file 'my_model.h5'
        #del model  # deletes the existing model
    return model


def eval_model(modelname, diffToLabel, rescale=False):
    """

    :param modelname:   Path to .h5 File were model is stored
    :param diffToLabel: additional Padding
    :param rescale:     Flag, if True Output will be scaled between 0 and 1
    :return:            None
    """
    model = load_model(modelname+'.h5')

    # generates an synthetic sample:
    data, label = generate_one_sample((100, 100), N_INPUTS, schrittweite=10, pad=diffToLabel)
    prediction = model.predict(np.expand_dims(data, axis=0))
    # plot_6_images(data, label)
    eval_output(output=prediction, label=label, name=modelname, rescale=rescale)
    return


def eval_all():
    simple = ('oldNetworks/01_CNN_simple', 2)
    simple2 = ("oldNetworks/03_CNN_simple_5x5_5x5_2epoch", 4)
    simple3 = ("oldNetworks/04_CNN_simple_5x5_5x5_4epoch", 4)
    simple4 = ("oldNetworks/05_CNN_simple_5x5_5x5_2epoch_KLD", 4)
    deeper = ("oldNetworks/02_CNN_deeper_2epoch", 5)  # 0.0229 #Test accuracy: 0.002
    deeper2 = ("oldNetworks/06_CNN_deeper_2epoch_10k", 5)  # 0.0175 #Test accuracy: 0.0
    all = [simple, simple2, simple3, simple4, deeper, deeper2]
    for  net in all:
        try:
            eval_model(net[0],net[1])
        except OSError as e:
            print("Skipping Network", e)
    return


if __name__ == '__main__':
    bool_Train = False
    #eval_model("CNN_deeper_1epoch_25k", 5)
    #Train:
    if bool_Train:
        model = networkBox.get_deeper_net(input_shape=input_shape, loss=keras.losses.mean_squared_error)
        train_model(model, diffToLabel=5, epochs=2, savename="tmp", n_train=100, channelsLast=False)

    else:
        eval_all()


