import tfModels as tfm
import simple_CNN_test as sCNN
import numpy as np
import os
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt


N_INPUTS = 5
input_shape = (100, 100, N_INPUTS)  # Channels Last!
DIFF_TO_LABEL = 2

def compare_multiple_nets(netlist, seed, diffToLabel=DIFF_TO_LABEL, channelsLast=True, show_GroundTruth=True):
    np.random.seed(seed)
    data, label = sCNN.generate_one_sample((100, 100), N_INPUTS, schrittweite=10, pad=diffToLabel, channelsLast=channelsLast)
    predictions = []
    for model in netlist:
        assert isinstance(model, str)
        model = load_model(model)
        pred = model.predict(np.expand_dims(data, axis=0))
        predictions.append(pred.reshape(label.shape))

    if show_GroundTruth:
        netlist.append("Label")
        predictions.append(label)
    f, axes = plt.subplots(2, int((len(predictions)+1)/2.0))
    multiarray = int((len(predictions)+1)/2.0)
    for i in range(len(predictions)):
        if multiarray == 1:
            axes[i].imshow(predictions[i], vmin=0, vmax=1, interpolation="none")
            axes[i].set_title(netlist[i])
        else:
            axes[i%multiarray][int(i/multiarray)].imshow(predictions[i], vmin=0, vmax=1, interpolation="none")
            axes[i % multiarray][int(i / multiarray)].set_title(netlist[i])
    f.suptitle("vergleich seed = {}".format(seed))
    #plt.show()
    return

def load_last_net(nameoffset, _dir=os.getcwd()):
    assert nameoffset is not None
    last_version=-1
    print("load last state")
    print(_dir)
    for e in os.listdir(_dir):
        if nameoffset in e and ".h5" in e:
            e = e.replace(".h5", "")
            e = e.replace(nameoffset+"_","")
            n = int(e)
            if n > last_version:
                last_version = n

    netname = nameoffset+"_"+str(last_version)+".h5"
    if last_version == -1:
        print("no network found in this Path:", _dir)
        return None, 0
    print(netname)
    model = load_model(netname)
    return model, last_version

def eval_trainingsphase(model, n_epoch, diffToLabel, n_train, savename=None, channelsLast=True, n_inputs=N_INPUTS, use_logfile=True, load_last_state=False):
    offset = 0
    if load_last_state:
        model, offset = load_last_net(savename)
        if model is None:
            return
    info = "Starte Trainingsphase für {} Epochen".format(n_epoch)
    if offset > 0:
        info += ", beginne bei Epoche {}, geladenes Netz = {}".format(offset, savename+"_"+str(offset)+".h5")
    if savename is not None:
        info += " Zwischenschritte werden gespeichert!"
    print(info)

    tmp = np.random.randint(0,100000)
    np.random.seed(13370)
    data, label = sCNN.generate_one_sample((100, 100), N_INPUTS, schrittweite=10, pad=diffToLabel, channelsLast=True)
    np.random.seed(tmp)
    log = open("trainphase.log", "w+")
    for i in range(offset, n_epoch):
        current_name = None
        if savename is not None:
            current_name = savename+"_"+str(i+1)
        sCNN.train_model(model, diffToLabel=diffToLabel, epochs=1, savename=current_name, n_train=n_train, channelsLast=channelsLast, n_inputs=n_inputs)
        prediction = model.predict(np.expand_dims(data, axis=0))
        sCNN.eval_output(output=prediction, label=label, name=savename+"_"+str(i+1), rescale=False, save_img_name=savename+"_"+str(i+1))
        if use_logfile:
            info = "Epoch: "+str(i)+"\tmax: "+str(np.max(prediction))+"\tmin: "+str(np.min(prediction))+"\tsaved as: "+savename+"_"+str(i+1)+"\n"
            print(info)
            log.write(info)
            log.flush()
    log.close()


#model = tfm.network_differentWay(input_shape)
#eval_trainingsphase(model, n_epoch=100, diffToLabel=DIFF_TO_LABEL, n_train=1000, savename="Test_UPsampling", channelsLast=True, n_inputs=N_INPUTS, use_logfile=True, load_last_state=False)

model = tfm.sameshape_CNN(input_shape)
#eval_trainingsphase(model, n_epoch=100, diffToLabel=DIFF_TO_LABEL, n_train=1000,
#                    savename="twoUPSamplings", channelsLast=True, n_inputs=N_INPUTS, use_logfile=True, load_last_state=True)

for seed in [13370, 100, 12345]:
    compare_multiple_nets(["Net_tinyUNet/twoUpSamplings_100.h5", "Net_with_BNorm/Test_UPsampling_100.h5",
                           "Net_without_BNorm/Test_UPsampling_100.h5"], seed)
plt.show()

# eval_model("tmp",0)
# plot_6_images(data, label)
#sCNN.eval_output(output=prediction, label=label, name="JAJA", rescale=False)
