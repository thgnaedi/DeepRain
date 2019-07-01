from tensorflow.python.keras.models import Model
from tensorflow.python.keras.layers import (Input, Lambda, Conv2D, MaxPooling2D, Flatten, Dense, Dropout,
                                            Lambda, Activation, BatchNormalization, concatenate, UpSampling2D,
                                            ZeroPadding2D)

def UNet64(input_shape, n_predictions=1, lossfunction="mean_squared_error", simpleclassification=None):
    inputs = Input(shape=input_shape)

    conv01 = Conv2D(10, kernel_size=(3,3), padding="same")(inputs)  #10 x 64x64
    conv01 = Activation('relu')(conv01)
    conv01_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv01)      #10 x 32x32
    print("0)", conv01_pool.shape, "10 x 32x32")

    conv02 = Conv2D(20, kernel_size=(3,3), padding="same")(conv01_pool) #20 x 32x32
    conv02 = Activation('relu')(conv02)
    conv02_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv02)          #20 x 16x16
    print("1)", conv02_pool.shape, "20 x 16x16")

    conv03 = Conv2D(20, kernel_size=(3, 3), padding="same")(conv02_pool)#20 x 16x16
    conv03 = Activation('relu')(conv03)
    conv03_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv03)          #20 x 8x8
    print("2)", conv03_pool.shape, "20 x 8x8")

    conv04 = Conv2D(20, kernel_size=(3, 3), padding="same")(conv03_pool)#20 x 8x8
    conv04 = Activation('relu')(conv04)
    conv04_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv04)          #20 x 4x4
    print("3)", conv04_pool.shape, "20 x 4x4")

### UPSAMPLING:
    up04 = UpSampling2D((2, 2))(conv04_pool)                            #20 x 8x8
    up04 = concatenate([conv04, up04], axis=3)                          #20+20 x 8x8
    print("4)", up04.shape, "40 x 8x8")

    up03 = UpSampling2D((2, 2))(up04)                                   #40 x 16x16
    up03 = concatenate([conv03, up03], axis=3)                          #20+40 x 16x16
    print("5)", up03.shape, "60 x 16x16")

    up02 = UpSampling2D((2, 2))(up03)                                   #60 x 32x32
    up02 = concatenate([conv02, up02], axis=3)                          #20+60 x 32x32
    print("6)", up02.shape, "80 x 32x32")

    up01 = UpSampling2D((2, 2))(up02)                                   #80 x 64x64
    up01 = concatenate([conv01, up01], axis=3)                          #10+80 x 64x64
    print("7)", up01.shape, "90 x 64x64")

    output = Conv2D(n_predictions, (1, 1), activation='relu')(up01)                 #1 x 64x64
    print("8)", output.shape, "{} x 64x64".format(n_predictions))
    output = Flatten()(output)
    if simpleclassification is not None:
        output = Dense(simpleclassification, activation='softmax')
        print("9)", output.shape, "zur Klassifikation von {} Klassen (mit softmax)".format(simpleclassification))

    model = Model(inputs=inputs, outputs=output)
    model.compile(loss=lossfunction, optimizer='adam')
    return model


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

def UNet64_output_expansed(input_shape):
    """gleich wie UNet64, nur am output ist ein 3x3 Kernel eingesetzt."""
    inputs = Input(shape=input_shape)

    conv01 = Conv2D(10, kernel_size=(3,3), padding="same")(inputs)  #10 x 64x64
    conv01 = Activation('relu')(conv01)
    conv01_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv01)      #10 x 32x32
    print("0)", conv01_pool.shape, "10 x 32x32")

    conv02 = Conv2D(20, kernel_size=(3,3), padding="same")(conv01_pool) #20 x 32x32
    conv02 = Activation('relu')(conv02)
    conv02_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv02)          #20 x 16x16
    print("1)", conv02_pool.shape, "20 x 16x16")

    conv03 = Conv2D(20, kernel_size=(3, 3), padding="same")(conv02_pool)#20 x 16x16
    conv03 = Activation('relu')(conv03)
    conv03_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv03)          #20 x 8x8
    print("2)", conv03_pool.shape, "20 x 8x8")

    conv04 = Conv2D(20, kernel_size=(3, 3), padding="same")(conv03_pool)#20 x 8x8
    conv04 = Activation('relu')(conv04)
    conv04_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv04)          #20 x 4x4
    print("3)", conv04_pool.shape, "20 x 4x4")

### UPSAMPLING:
    up04 = UpSampling2D((2, 2))(conv04_pool)                            #20 x 8x8
    up04 = concatenate([conv04, up04], axis=3)                          #20+20 x 8x8
    print("4)", up04.shape, "40 x 8x8")

    up03 = UpSampling2D((2, 2))(up04)                                   #40 x 16x16
    up03 = concatenate([conv03, up03], axis=3)                          #20+40 x 16x16
    print("5)", up03.shape, "60 x 16x16")

    up02 = UpSampling2D((2, 2))(up03)                                   #60 x 32x32
    up02 = concatenate([conv02, up02], axis=3)                          #20+60 x 32x32
    print("6)", up02.shape, "80 x 32x32")

    up01 = UpSampling2D((2, 2))(up02)                                   #80 x 64x64
    up01 = concatenate([conv01, up01], axis=3)                          #10+80 x 64x64
    print("7)", up01.shape, "90 x 64x64")

    output = Conv2D(1, (3, 3), activation='relu', padding="same")(up01)#1 x 64x64
    print("8)", output.shape, "1 x 64x64")
    output = Flatten()(output)
    model = Model(inputs=inputs, outputs=output)
    model.compile(loss="mean_squared_error", optimizer='adam')
    return model

def UNet64_2x2core(input_shape):
    """wie UNet64_out_expansed, aber downsampling bis 2x2"""
    inputs = Input(shape=input_shape)

    conv01 = Conv2D(10, kernel_size=(3,3), padding="same")(inputs)  #10 x 64x64
    conv01 = Activation('relu')(conv01)
    conv01_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv01)      #10 x 32x32
    print("0)", conv01_pool.shape, "10 x 32x32")

    conv02 = Conv2D(20, kernel_size=(3,3), padding="same")(conv01_pool) #20 x 32x32
    conv02 = Activation('relu')(conv02)
    conv02_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv02)          #20 x 16x16
    print("1)", conv02_pool.shape, "20 x 16x16")

    conv03 = Conv2D(20, kernel_size=(3, 3), padding="same")(conv02_pool)#20 x 16x16
    conv03 = Activation('relu')(conv03)
    conv03_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv03)          #20 x 8x8
    print("2)", conv03_pool.shape, "20 x 8x8")

    conv04 = Conv2D(20, kernel_size=(3, 3), padding="same")(conv03_pool)#20 x 8x8
    conv04 = Activation('relu')(conv04)
    conv04_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv04)          #20 x 4x4
    print("3)", conv04_pool.shape, "20 x 4x4")

    conv05 = Conv2D(5, kernel_size=(3, 3), padding="same")(conv04_pool)#5 x 4x4
    conv05 = Activation('relu')(conv05)
    conv05_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv05)          #5 x 2x2
    print("4)", conv05_pool.shape, "5 x 2x2")

### UPSAMPLING:
    up05 = UpSampling2D((2, 2))(conv05_pool)                            #5 x 4x4
    up05 = concatenate([conv05, up05], axis=3)                          #10 x 4x4
    print("4)", up05.shape, "10 x 4x4")

    up04 = UpSampling2D((2, 2))(up05)                                   #10 x 8x8
    up04 = concatenate([conv04, up04], axis=3)                          #20+10 x 8x8
    print("4)", up04.shape, "20 x 8x8")

    up03 = UpSampling2D((2, 2))(up04)                                   #30 x 16x16
    up03 = concatenate([conv03, up03], axis=3)                          #20+30 x 16x16
    print("5)", up03.shape, "50 x 16x16")

    up02 = UpSampling2D((2, 2))(up03)                                   #50 x 32x32
    up02 = concatenate([conv02, up02], axis=3)                          #20+50 x 32x32
    print("6)", up02.shape, "70 x 32x32")

    up01 = UpSampling2D((2, 2))(up02)                                   #70 x 64x64
    up01 = concatenate([conv01, up01], axis=3)                          #10+70 x 64x64
    print("7)", up01.shape, "80 x 64x64")

    output = Conv2D(1, (3, 3), activation='relu', padding="same")(up01)#1 x 64x64
    print("8)", output.shape, "1 x 64x64")
    output = Flatten()(output)
    model = Model(inputs=inputs, outputs=output)
    model.compile(loss="mean_squared_error", optimizer='adam')
    return model

def UNet64_2x2core_large(input_shape):
    """wie UNet64_out_expansed, aber downsampling bis 2x2"""
    inputs = Input(shape=input_shape)

    conv01 = Conv2D(10, kernel_size=(3,3), padding="same")(inputs)  #10 x 64x64
    conv01 = Activation('relu')(conv01)
    conv01_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv01)      #10 x 32x32
    print("0)", conv01_pool.shape, "10 x 32x32")

    conv02 = Conv2D(20, kernel_size=(3,3), padding="same")(conv01_pool) #20 x 32x32
    conv02 = Activation('relu')(conv02)
    conv02_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv02)          #20 x 16x16
    print("1)", conv02_pool.shape, "20 x 16x16")

    conv03 = Conv2D(20, kernel_size=(3, 3), padding="same")(conv02_pool)#20 x 16x16
    conv03 = Activation('relu')(conv03)
    conv03_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv03)          #20 x 8x8
    print("2)", conv03_pool.shape, "20 x 8x8")

    conv04 = Conv2D(20, kernel_size=(3, 3), padding="same")(conv03_pool)#20 x 8x8
    conv04 = Activation('relu')(conv04)
    conv04_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv04)          #20 x 4x4
    print("3)", conv04_pool.shape, "20 x 4x4")

    conv05 = Conv2D(20, kernel_size=(3, 3), padding="same")(conv04_pool)#20 x 4x4
    conv05 = Activation('relu')(conv05)
    conv05_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv05)          #20 x 2x2
    print("4)", conv05_pool.shape, "20 x 2x2")

### UPSAMPLING:
    up05 = UpSampling2D((2, 2))(conv05_pool)                            #20 x 4x4
    up05 = concatenate([conv05, up05], axis=3)                          #40 x 4x4
    print("4)", up05.shape, "40 x 4x4")

    up04 = UpSampling2D((2, 2))(up05)                                   #10 x 8x8
    up04 = concatenate([conv04, up04], axis=3)                          #20+40 x 8x8
    print("4)", up04.shape, "60 x 8x8")

    up03 = UpSampling2D((2, 2))(up04)                                   #30 x 16x16
    up03 = concatenate([conv03, up03], axis=3)                          #20+60 x 16x16
    print("5)", up03.shape, "80 x 16x16")

    up02 = UpSampling2D((2, 2))(up03)                                   #80 x 32x32
    up02 = concatenate([conv02, up02], axis=3)                          #20+80 x 32x32
    print("6)", up02.shape, "100 x 32x32")

    up01 = UpSampling2D((2, 2))(up02)                                   #100 x 64x64
    up01 = concatenate([conv01, up01], axis=3)                          #10+100 x 64x64
    print("7)", up01.shape, "110 x 64x64")

    output = Conv2D(1, (3, 3), activation='relu', padding="same")(up01)#1 x 64x64
    print("8)", output.shape, "1 x 64x64")
    output = Flatten()(output)
    model = Model(inputs=inputs, outputs=output)
    model.compile(loss="mean_squared_error", optimizer='adam')
    return model

def UNet64_sigmoid_tanh(input_shape):
    """gleich wie UNet64_output_expansed, teilweise mit sigmoid und tanh statt relu."""
    inputs = Input(shape=input_shape)

    conv01 = Conv2D(10, kernel_size=(3,3), padding="same")(inputs)  #10 x 64x64
    conv01 = Activation('tanh')(conv01)
    conv01_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv01)      #10 x 32x32
    print("0)", conv01_pool.shape, "10 x 32x32")

    conv02 = Conv2D(20, kernel_size=(3,3), padding="same")(conv01_pool) #20 x 32x32
    conv02 = Activation('tanh')(conv02)
    conv02_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv02)          #20 x 16x16
    print("1)", conv02_pool.shape, "20 x 16x16")

    conv03 = Conv2D(20, kernel_size=(3, 3), padding="same")(conv02_pool)#20 x 16x16
    conv03 = Activation('tanh')(conv03)
    conv03_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv03)          #20 x 8x8
    print("2)", conv03_pool.shape, "20 x 8x8")

    conv04 = Conv2D(20, kernel_size=(3, 3), padding="same")(conv03_pool)#20 x 8x8
    conv04 = Activation('relu')(conv04)
    conv04_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv04)          #20 x 4x4
    print("3)", conv04_pool.shape, "20 x 4x4")

### UPSAMPLING:
    up04 = UpSampling2D((2, 2))(conv04_pool)                            #20 x 8x8
    up04 = concatenate([conv04, up04], axis=3)                          #20+20 x 8x8
    print("4)", up04.shape, "40 x 8x8")

    up03 = UpSampling2D((2, 2))(up04)                                   #40 x 16x16
    up03 = concatenate([conv03, up03], axis=3)                          #20+40 x 16x16
    print("5)", up03.shape, "60 x 16x16")

    up02 = UpSampling2D((2, 2))(up03)                                   #60 x 32x32
    up02 = concatenate([conv02, up02], axis=3)                          #20+60 x 32x32
    print("6)", up02.shape, "80 x 32x32")

    up01 = UpSampling2D((2, 2))(up02)                                   #80 x 64x64
    up01 = concatenate([conv01, up01], axis=3)                  #15+80 x 64x64
    print("7)", up01.shape, "95 x 64x64")

    output = Conv2D(1, (3, 3), activation='relu', padding="same")(up01)#1 x 64x64
    #output = Activation('tanh')(output)
    print("8)", output.shape, "1 x 64x64")
    output = Flatten()(output)
    model = Model(inputs=inputs, outputs=output)
    model.compile(loss="mean_squared_error", optimizer='nadam')
    #ToDo: try Nesterov Adam optimizer (nadam)
    # http://proceedings.mlr.press/v28/sutskever13.pdf
    return model

def UNet64x2(input_shape):
    """default network extendet to predict 2 timesteps at once"""
    inputs = Input(shape=input_shape)

    conv01 = Conv2D(10, kernel_size=(3,3), padding="same")(inputs)  #10 x 64x64
    conv01 = Activation('relu')(conv01)
    conv01_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv01)      #10 x 32x32
    print("0)", conv01_pool.shape, "10 x 32x32")

    conv02 = Conv2D(20, kernel_size=(3,3), padding="same")(conv01_pool) #20 x 32x32
    conv02 = Activation('relu')(conv02)
    conv02_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv02)          #20 x 16x16
    print("1)", conv02_pool.shape, "20 x 16x16")

    conv03 = Conv2D(20, kernel_size=(3, 3), padding="same")(conv02_pool)#20 x 16x16
    conv03 = Activation('relu')(conv03)
    conv03_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv03)          #20 x 8x8
    print("2)", conv03_pool.shape, "20 x 8x8")

    conv04 = Conv2D(20, kernel_size=(3, 3), padding="same")(conv03_pool)#20 x 8x8
    conv04 = Activation('relu')(conv04)
    conv04_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv04)          #20 x 4x4
    print("3)", conv04_pool.shape, "20 x 4x4")

### UPSAMPLING:
    up04 = UpSampling2D((2, 2))(conv04_pool)                            #20 x 8x8
    up04 = concatenate([conv04, up04], axis=3)                          #20+20 x 8x8
    print("4)", up04.shape, "40 x 8x8")

    up03 = UpSampling2D((2, 2))(up04)                                   #40 x 16x16
    up03 = concatenate([conv03, up03], axis=3)                          #20+40 x 16x16
    print("5)", up03.shape, "60 x 16x16")

    up02 = UpSampling2D((2, 2))(up03)                                   #60 x 32x32
    up02 = concatenate([conv02, up02], axis=3)                          #20+60 x 32x32
    print("6)", up02.shape, "80 x 32x32")

    up01 = UpSampling2D((2, 2))(up02)                                   #80 x 64x64
    up01 = concatenate([conv01, up01], axis=3)                          #10+80 x 64x64
    print("7)", up01.shape, "90 x 64x64")

    output = Conv2D(2, (1, 1), activation='relu')(up01)                 #2 x 64x64
    print("8)", output.shape, "2 x 64x64")
    output = Flatten()(output)
    model = Model(inputs=inputs, outputs=output)
    model.compile(loss="mean_squared_error", optimizer='adam')
    return model


if __name__ == '__main__':
    print("=)")