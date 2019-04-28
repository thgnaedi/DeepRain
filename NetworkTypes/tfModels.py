from tensorflow.python.keras.models import Model
from tensorflow.python.keras.layers import (Input, Lambda, Conv2D, MaxPooling2D, Flatten, Dense, Dropout,
                                            Lambda, Activation, BatchNormalization, concatenate, UpSampling2D,
                                            ZeroPadding2D)

def network_differentWay(input_shape, use_b_norm=True):
    inputs = Input(shape=input_shape)

    conv01 = Conv2D(32, kernel_size=(5, 5), input_shape=input_shape)(inputs)
    if use_b_norm:
        conv01 = BatchNormalization()(conv01)
    conv01 = Activation('relu')(conv01)
    conv01_pool = MaxPooling2D((3, 3), strides=(3,3))(conv01)
    #print("conv01_pool)",conv01_pool.shape)

    up01 = UpSampling2D((3, 3))(conv01_pool)
    if use_b_norm:
        up01 = BatchNormalization()(up01)
    up01 = concatenate([conv01, up01], axis=3)

    output = Conv2D(1, (1, 1), activation='relu')(up01)
    output = Flatten()(output)
    model = Model(inputs=inputs, outputs=output)
    model.compile(loss="mean_squared_error", optimizer='adam')
    return model

def sameshape_CNN(input_shape, use_b_norm=True):
    inputs = Input(shape=input_shape)
    #print("0)", inputs.shape)
    conv01 = Conv2D(32, kernel_size=(5, 5), input_shape=input_shape)(inputs)
    #print("1)", conv01.shape)
    if use_b_norm:
        conv01 = BatchNormalization()(conv01)
    conv01 = Activation('relu')(conv01)
    conv01_pool = MaxPooling2D((3, 3), strides=(3,3))(conv01)

    conv02 = Conv2D(64, kernel_size=(3,3), padding="same")(conv01_pool)
    #print("2)", conv02.shape)
    if use_b_norm:
        conv02 = BatchNormalization()(conv02)
    conv02 = Activation('relu')(conv02)
    conv02_pool = MaxPooling2D((2, 2), strides=(2,2))(conv02)
    #print("3)", conv02_pool.shape)

    up02 = UpSampling2D((2, 2))(conv02_pool)
    up02 = concatenate([conv02, up02], axis=3)
    #print("4)", up02.shape)

    up01 = UpSampling2D((3, 3))(up02)
    if use_b_norm:
        up01 = BatchNormalization()(up01)
    up01 = concatenate([conv01, up01], axis=3)
    #print("5)", up01.shape)

    output = Conv2D(1, (1, 1), activation='relu')(up01)
    #print("6)", output.shape)
    output = Flatten()(output)
    model = Model(inputs=inputs, outputs=output)
    model.compile(loss="mean_squared_error", optimizer='adam')
    #possible losses are: https://www.tensorflow.org/api_docs/python/tf/losses
    return model

if __name__ == '__main__':
    print("=)")