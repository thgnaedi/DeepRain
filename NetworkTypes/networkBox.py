import numpy as np
import keras
from keras.models import Sequential
from keras import backend as K
from keras.models import load_model


def get_simple_net(input_shape, kernels=32, kernel_size1=(3,3), kernel_size2=(3,3), loss=keras.losses.mean_squared_error):
    ## Netz erstellen
    model = Sequential()
    model.add(keras.layers.Conv2D(kernels, kernel_size=kernel_size1,
                     activation='relu',
                     input_shape=input_shape, data_format='channels_first'))
    # input("1)"+str(model.output_shape))
    model.add(keras.layers.Dropout(0.05))
    # input("2)"+str(model.output_shape))
    model.add(keras.layers.Conv2D(1, kernel_size2, activation='relu', input_shape=(32, 98, 98), data_format='channels_first'))
    # input("3)"+str(model.output_shape))
    model.add(keras.layers.Flatten(data_format='channels_first'))
    # input("4)"+str(model.output_shape))

    model.compile(loss=loss,
                  optimizer=keras.optimizers.Adadelta(),
                  metrics=['accuracy'])
    return model


def get_deeper_net(input_shape, dropout=False, loss=keras.losses.mean_squared_error):
    ## Netz erstellen
    model = Sequential()
    model.add(keras.layers.Conv2D(16, kernel_size=(5, 5),
                     activation='relu',
                     input_shape=input_shape, data_format='channels_first'))
    model.add(keras.layers.Conv2D(32, kernel_size=(5, 5),
                     activation='relu',
                     input_shape=input_shape, data_format='channels_first'))
    if dropout:
        model.add(keras.layers.Dropout(0.01))
    model.add(keras.layers.Conv2D(1, (3, 3), activation='relu', input_shape=(32, 98, 98), data_format='channels_first'))
    model.add(keras.layers.Flatten(data_format='channels_first'))

    model.compile(loss=loss,
                  optimizer=keras.optimizers.Adadelta(),
                  metrics=['accuracy'])
    return model


def get_CNN_classification(input_shape, loss=keras.losses.categorical_crossentropy):
    model = Sequential()
    model.add(keras.layers.Conv2D(32, kernel_size=(3, 3),
                     activation='relu',
                     input_shape=input_shape))
    model.add(keras.layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))
    model.add(keras.layers.Dropout(0.25))
    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(30, activation='relu'))
    model.add(keras.layers.Dropout(0.2))
    model.add(keras.layers.Dense(3, activation='softmax'))

    model.compile(loss=loss,
                  optimizer=keras.optimizers.Adadelta(),
                  metrics=['accuracy'])
    return model