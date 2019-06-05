import tfModels as tfM
import tfLosses as tfL
import simple_CNN_test as sCNN
import numpy as np
import os
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
import keras

N_INPUTS = 5
input_shape = (100, 100, N_INPUTS)  # Channels Last!
DIFF_TO_LABEL = 2


def compare_multiple_nets(netlist, eval_seed, diffToLabel=DIFF_TO_LABEL, channelsLast=True, show_GroundTruth=True):
    np.random.seed(eval_seed)
    data, label = sCNN.generate_one_sample((100, 100), N_INPUTS, schrittweite=10, pad=diffToLabel,
                                           channelsLast=channelsLast)
    predictions = []
    for current_model in netlist:
        assert isinstance(current_model, str)
        current_model = load_model(current_model)
        pred = current_model.predict(np.expand_dims(data, axis=0))
        predictions.append(pred.reshape(label.shape))

    if show_GroundTruth:
        netlist.append("Label")
        predictions.append(label)
    f, axes = plt.subplots(2, int((len(predictions) + 1) / 2.0))
    multiarray = int((len(predictions) + 1) / 2.0)
    for i in range(len(predictions)):
        if multiarray == 1:
            axes[i].imshow(predictions[i], vmin=0, vmax=1, interpolation="none")
            axes[i].set_title(netlist[i])
        else:
            axes[i % multiarray][int(i / multiarray)].imshow(predictions[i], vmin=0, vmax=1, interpolation="none")
            axes[i % multiarray][int(i / multiarray)].set_title(netlist[i])
    f.suptitle("vergleich seed = {}".format(eval_seed))
    # plt.show()
    return


def load_last_net(nameoffset, _dir=os.getcwd()):
    assert nameoffset is not None
    last_version = -1
    print("load last state")
    print(_dir)
    for e in os.listdir(_dir):
        if nameoffset in e and ".h5" in e:
            e = e.replace(".h5", "")
            e = e.replace(nameoffset + "_", "")
            n = int(e)
            if n > last_version:
                last_version = n

    netname = nameoffset + "_" + str(last_version) + ".h5"
    if last_version == -1:
        print("no network found in this Path:", _dir)
        return None, 0
    print(netname)
    model = load_model(netname)
    return model, last_version


def eval_trainingsphase(model, n_epoch, diffToLabel, n_train, savename=None, channelsLast=True, n_inputs=N_INPUTS,
                        use_logfile=True, load_last_state=False):
    offset = 0
    if load_last_state:
        model, offset = load_last_net(savename)
        if model is None:
            return
    info = "Starte Trainingsphase für {} Epochen".format(n_epoch)
    if offset > 0:
        info += ", beginne bei Epoche {}, geladenes Netz = {}".format(offset, savename + "_" + str(offset) + ".h5")
    if savename is not None:
        info += " Zwischenschritte werden gespeichert!"
    print(info)

    tmp = np.random.randint(0, 100000)
    np.random.seed(13370)
    data, label = sCNN.generate_one_sample((100, 100), N_INPUTS, schrittweite=10, pad=diffToLabel, channelsLast=True)
    np.random.seed(tmp)
    log = open("trainphase.log", "w+")
    for i in range(offset, n_epoch):
        current_name = None
        if savename is not None:
            current_name = savename + "_" + str(i + 1)
        sCNN.train_model(model, diffToLabel=diffToLabel, epochs=1, savename=current_name, n_train=n_train,
                         channelsLast=channelsLast, n_inputs=n_inputs)
        prediction = model.predict(np.expand_dims(data, axis=0))
        sCNN.eval_output(output=prediction, label=label, name=savename + "_" + str(i + 1), rescale=False,
                         save_img_name=savename + "_" + str(i + 1))
        if use_logfile:
            info = "Epoch: " + str(i) + "\tmax: " + str(np.max(prediction)) + "\tmin: " + str(
                np.min(prediction)) + "\tsaved as: " + savename + "_" + str(i + 1) + "\n"
            print(info)
            log.write(info)
            log.flush()
    log.close()


def train_realdata(model, samplebundle, n_epoch=100, savename="UNet64_2016", channelsLast=True,
                   use_logfile=True, load_last_state=True, n_testsamples=50, prediction_shape = (64, 64), PREDICTION_IMG_ID=14):
    """
    Method to train Network on real Data (depending on the given samplebundle)
    :param model:           NN to train
    :param samplebundle:    sample bundle object, containing Data&Label as list.
    :param n_epoch:         number epochs to train
    :param savename:        name to store network (adding epoch number and .h5 at the end)
    :param channelsLast:    if true, channels are in the last axis
    :param use_logfile:     if true, logdetails will be stored in a file.
    :param load_last_state: if true, last stored network with same name will be loaded
    :param n_testsamples:   number of testsamples, data = [0:n_testsamples]+[n_testsamples:len(data)]
    :param PREDICTION_IMG_ID    id of evaluating image
    :return:                None
    """
    offset = 0
    if load_last_state:
        _model, offset = load_last_net(savename)
        if _model is None and model is None:
            print("No model to train!")
            return
        if _model is not None:
            model = _model

    samplebundle.normalize()
    info = "Starte Trainingsphase für {} Epochen".format(n_epoch)
    if offset > 0:
        info += ", beginne bei Epoche {}, geladenes Netz = {}".format(offset, savename + "_" + str(offset) + ".h5")
    if savename is not None:
        info += " Zwischenschritte werden gespeichert!"
    print(info)

    data, label = samplebundle.get_all_data_label(channels_Last=channelsLast, flatten_output=True)

    x_train, y_train = data[n_testsamples:], label[n_testsamples:]
    x_test, y_test = data[:n_testsamples], label[:n_testsamples]

    log = open("trainphase.log", "a+")
    for i in range(offset, n_epoch):
        current_name = None
        if savename is not None:
            current_name = savename + "_" + str(i + 1)

        history = model.fit(x_train, y_train, batch_size=200, epochs=1, verbose=1, validation_data=(x_test, y_test))
        trainloss = np.mean(np.array(history.history["loss"]))
        valloss = np.mean(np.array(history.history["val_loss"]))
        if current_name is not None:
            model.save(current_name + '.h5')  # creates a HDF5 file 'my_model.h5'

        prediction = model.predict(np.expand_dims(data[PREDICTION_IMG_ID], axis=0))
        sCNN.eval_output(output=prediction, label=label[PREDICTION_IMG_ID].reshape(prediction_shape),
                         name=savename + "_" + str(i + 1), rescale=False,
                         save_img_name=savename + "_" + str(i + 1))
        if use_logfile:
            info = "Epoch: " + str(i) + "\tmax: " + str(np.max(prediction)) +"/{}".format(np.max(label[PREDICTION_IMG_ID]))+ "\tmin: " + str(np.min(prediction)) +"\tloss: " + str(valloss) + "\ttrain_loss: " + str(trainloss) + "\tsaved as: " + savename + "_" + str(i + 1) + "\n"
            print(info)
            log.write(info)
            log.flush()
    log.close()
    return


# model = tfM.network_differentWay(input_shape)
# eval_trainingsphase(model, n_epoch=100, diffToLabel=DIFF_TO_LABEL, n_train=1000, savename="Test_UPsampling", channelsLast=True, n_inputs=N_INPUTS, use_logfile=True, load_last_state=False)
if __name__ == '__main__':

    # model = tfM.sameshape_CNN(input_shape)
    print("erstelle Netz:")
    input_shape = (64, 64, 5)  # Channels Last!
    #model = tfM.UNet64(input_shape) #erster Test auf reale Daten

    import sample_bundle

## UNet to predict 1 timestep (5min)
    #model = tfM.UNet64_sigmoid_tanh(input_shape)
    #sb = sample_bundle.load_Sample_Bundle("C:/Users/TopSecret!/Documents/aMSI1/Teamprojekt/DeepRain/Data/RegenTage2016")
    #print(sb.info())
    #train_realdata(model, sb, n_epoch=80, savename="UNet64_sigmoid_tanh_2016", channelsLast=True, use_logfile=True,
    #               load_last_state=True)
## UNet to predict 2 timesteps (10min)


    # zwei Zeitschritte:
    #model = tfM.UNet64x2(input_shape)
    #sb = sample_bundle.load_Sample_Bundle("C:/Users/TopSecret!/Documents/aMSI1/Teamprojekt/DeepRain/Data/RegenTage2016_5_2")
    #ein Zeitschritt
    model = tfM.UNet64(input_shape=(64, 64, 5), lossfunction=tfL.mean_squared_error_kopie)
    sb = sample_bundle.load_Sample_Bundle("C:/Users/TopSecret!/Documents/aMSI1/Teamprojekt/DeepRain/Data/RegenTage2016")

    print(sb.info())
    train_realdata(model, sb, n_epoch=10, savename="UNet64", channelsLast=True, use_logfile=True,
                   load_last_state=True, n_testsamples=50, prediction_shape = (64, 64), PREDICTION_IMG_ID=6)
    # eval_trainingsphase(model, n_epoch=100, diffToLabel=DIFF_TO_LABEL, n_train=1000,
    #                    savename="twoUPSamplings", channelsLast=True, n_inputs=N_INPUTS, use_logfile=True, load_last_state=True)
## compare nets on different Seeds:
    #for seed in [13370, 100, 12345]:
    #    compare_multiple_nets(["Net_tinyUNet/twoUpSamplings_100.h5", "Net_with_BNorm/Test_UPsampling_100.h5",
    #                           "Net_without_BNorm/Test_UPsampling_100.h5"], seed)
    #plt.show()

    # eval_model("tmp",0)
    # plot_6_images(data, label)
    # sCNN.eval_output(output=prediction, label=label, name="JAJA", rescale=False)
