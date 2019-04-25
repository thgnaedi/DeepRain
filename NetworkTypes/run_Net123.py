import simple_CNN_test
import networkBox
import keras

if __name__ == '__main__':
    N_INPUTS = 5
    input_shape = (N_INPUTS, 100, 100)  # Channels First!
    N_TRAIN = 25000
    model = networkBox.get_deeper_net(input_shape=input_shape, loss=keras.losses.mean_squared_error, dropout=True)

    for i in range(20):
        model = simple_CNN_test.train_model(model, diffToLabel=5, epochs=1, savename="CNN_deeper_"+str(i+1)+"epoch_25k", n_train=N_TRAIN)

    print("Skript ist Fertig, bitte die Daten (CNN_deeper_xxepoch_25k.h5) auf git hochladen,\ndankeschön =)")