import tfModels as tfm
import simple_CNN_test as sCNN
import numpy as np

N_INPUTS = 5
input_shape = (100, 100, N_INPUTS)  # Channels Last!
DIFF_TO_LABEL = 2

def eval_trainingsphase(model, n_epoch, diffToLabel, n_train, savename=None, channelsLast=True, n_inputs=N_INPUTS):
    print("Starte Trainingsphase für",n_epoch,"epochen, zwischen schritte werden gespeichert:", savename is not None)
    data, label = sCNN.generate_one_sample((100, 100), N_INPUTS, schrittweite=10, pad=diffToLabel, channelsLast=True)
    for i in range(n_epoch):
        sCNN.train_model(model, diffToLabel=diffToLabel, epochs=1, savename=savename+"_"+str(i+1), n_train=n_train, channelsLast=channelsLast, n_inputs=n_inputs)
        prediction = model.predict(np.expand_dims(data, axis=0))
        sCNN.eval_output(output=prediction, label=label, name=savename+"_"+str(i+1), rescale=False, save_img_name=savename+"_"+str(i+1))
        print("Epoch:",i,"max,min value:",np.max(prediction), np.min(prediction))


model = tfm.network_differentWay(input_shape)
eval_trainingsphase(model, n_epoch=100, diffToLabel=DIFF_TO_LABEL, n_train=2000, savename="Test_UPsampling", channelsLast=True, n_inputs=N_INPUTS)

# eval_model("tmp",0)
# plot_6_images(data, label)
#sCNN.eval_output(output=prediction, label=label, name="JAJA", rescale=False)
