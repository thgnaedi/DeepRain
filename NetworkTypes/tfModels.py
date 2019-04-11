from tensorflow.python.keras.models import Model
from tensorflow.python.keras.layers import (Input, Lambda, Conv2D, MaxPooling2D, Flatten, Dense, Dropout,
                                            Lambda, Activation, BatchNormalization, concatenate, UpSampling2D,
                                            ZeroPadding2D)

def network_differentWay(input_shape):
    inputs = Input(shape=input_shape)

    conv01 = Conv2D(16, kernel_size=(5, 5), padding='same', input_shape=input_shape)(inputs)
    #down0a_pool = MaxPooling2D((2, 2), strides=(2, 2))(down0a)
    conv01 = BatchNormalization()(conv01)
    conv01 = Activation('relu')(conv01)

    #up2 = UpSampling2D((2, 2))(down0)
    output = Conv2D(1, (3, 3), activation='relu', padding="same")(conv01)
    output = Flatten()(output)
    #print("2)",output.shape)
    model = Model(inputs=inputs, outputs=output)
    model.compile(loss="mean_squared_error", optimizer='adam')
    return model

if __name__ == '__main__':
    N_INPUTS = 5
    input_shape = (100, 100, N_INPUTS)  # Channels Last!
    model = network_differentWay(input_shape)
    train_model(model, diffToLabel=0, epochs=1, savename=None, n_train=100, channelsLast=True)
    # eval_model("tmp",0)
    data, label = generate_one_sample((100, 100), N_INPUTS, schrittweite=10, pad=0, channelsLast=True)
    prediction = model.predict(np.expand_dims(data, axis=0))
    # plot_6_images(data, label)
    eval_output(output=prediction, label=label, name="JAJA", rescale=False)