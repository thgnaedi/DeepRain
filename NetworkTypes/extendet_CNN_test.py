import tfModels as tfm
import simple_CNN_test as sCNN
import numpy as np

N_INPUTS = 5
input_shape = (100, 100, N_INPUTS)  # Channels Last!
DIFF_TO_LABEL = 2

model = tfm.network_differentWay(input_shape)
sCNN.train_model(model, diffToLabel=DIFF_TO_LABEL, epochs=1, savename=None, n_train=3000, channelsLast=True)
# eval_model("tmp",0)
data, label = sCNN.generate_one_sample((100, 100), N_INPUTS, schrittweite=10, pad=DIFF_TO_LABEL, channelsLast=True)
prediction = model.predict(np.expand_dims(data, axis=0))
# plot_6_images(data, label)
sCNN.eval_output(output=prediction, label=label, name="JAJA", rescale=False)