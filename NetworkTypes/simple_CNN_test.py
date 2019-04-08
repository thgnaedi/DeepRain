from dummy_datagenerator import generate_one_sample, plot_6_images, eval_output
import numpy as np
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K

N_INPUTS = 5
input_shape = (N_INPUTS, 100, 100) #Channels First!

def generate_Dataset(n_train, n_test):
    xtrain = []
    ytrain = []
    for i in range(n_train):
        data, label = generate_one_sample((100,100), N_INPUTS, schrittweite=10, pad=2)
        xtrain.append(data)
        ytrain.append(label.flatten())
    xtest = []
    ytest = []
    for i in range(n_test):
        data, label = generate_one_sample((100, 100), N_INPUTS, schrittweite=10, pad=2)
        xtest.append(data)
        ytest.append(label.flatten())
    return np.array(xtrain), np.array(ytrain), np.array(xtest), np.array(ytest)


## Netz erstellen
model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3),
                 activation='relu',
                 input_shape=input_shape, data_format='channels_first'))
#input("1)"+str(model.output_shape))
model.add(Dropout(0.05))
#input("2)"+str(model.output_shape))
model.add(Conv2D(1, (3, 3), activation='relu', input_shape=(32,98,98), data_format='channels_first'))
#input("3)"+str(model.output_shape))
model.add(Flatten(data_format='channels_first'))
#input("4)"+str(model.output_shape))

model.compile(loss=keras.losses.mean_squared_error,
              optimizer=keras.optimizers.Adadelta(),
              metrics=['accuracy'])

# Trainieren
x_train, y_train, x_test, y_test = generate_Dataset(n_train=1000, n_test=100)
batch_size = 100
epochs = 2
model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, verbose=1, validation_data=(x_test, y_test))

score = model.evaluate(x_test, y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

data, label = generate_one_sample((100,100), N_INPUTS, schrittweite=10, pad=2)
prediction = model.predict(np.expand_dims(data,axis=0))
#plot_6_images(data, label)

eval_output(output=prediction, label=label)


