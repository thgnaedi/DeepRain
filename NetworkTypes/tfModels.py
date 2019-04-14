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

if __name__ == '__main__':
    print("=)")