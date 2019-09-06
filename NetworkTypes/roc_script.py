import numpy as np
import matplotlib.pyplot as plt
from NetworkTypes.eval_2D_classification import generate_classification, load_last_net


def drawROC(class1, class2):
    # Plot the distirutions of incomming data
    plt.figure("distribution")
    plt.hist(class1, bins=20, alpha=0.5, label='class 1')
    plt.hist(class2, bins=20, alpha=0.5, label='class 2')
    plt.legend(loc='upper right')

    # Calculate TruePositive and FalsePositives for each threshold
    tps = []
    fps = []
    for threshold in np.arange(0,1,0.05):
        tp = 0
        fp = 0
        tn = 0
        fn = 0

        for e in class1:
            if e <= threshold: # class 1 hit
                tn = tn + 1
            else:           # class 1 miss
                fp = fp + 1
        for e in class2:
            if e <= threshold:  # class2 miss
                fn = fn + 1
            else:           # class2 hit
                tp = tp+1
        # get propabilities
        tp = tp / len(class2)
        fp = fp / len(class1)
        tps.append(tp)
        fps.append(fp)

    # calculate Area Under the Curve
    auc = getAUCfromROC(tps, fps)
    # plot ROC
    plt.figure("ROC")
    plt.plot([0,0,1], [0,1,1], color="gray", alpha=0.6, label="AUC = 1")
    plt.plot(tps, fps, label="AUC = {:.3}".format(auc))
    plt.xlim(-0.02,1.02)
    plt.ylim(-0.02,1.02)
    plt.ylabel("P(TP)")
    plt.xlabel("P(FP)")
    plt.legend()
    plt.show()
    return


def getAUCfromROC(tp, fp):
    # calculate AUC from ROC, using trapezoidal method
    summ = 0
    print(tp)
    print(fp)
    for i in range(len(tp)-1):
        h1 = fp[i]
        h2 = fp[i+1]
        diff = h1-h2
        b = tp[i]-tp[i+1]
        summ = summ + h2* b         # square
        summ = summ + diff * b / 2  # triangle

    return summ


def get_probability_lists(net, data, label):
    prediction = net.predict(data)

    target_shape = (8123, 64, 64, 2)
    print("Prediction shape: {}".format(prediction.shape))
    prediction = prediction.reshape(target_shape)
    label = label.reshape(target_shape)

    probability_category_a = []
    probability_category_b = []
    for idx, value in np.ndenumerate(prediction):
        pred_pixel_categories = prediction[idx[0], idx[1], idx[2], :]
        x = pred_pixel_categories[0]

        true_class = label[idx[0], idx[1], idx[2], :]
        list_selector = np.where(true_class == 1)[0][0]
        if list_selector == 0:
            probability_category_a.append(x)
        else:
            probability_category_b.append(x)
    return probability_category_a, probability_category_b


def main():
    directory = "..\\Data\\Training\\2categories\\treshold_0\\"
    # DatenSammeln
    data, label = generate_classification()
    val_data = data[:623]
    val_lbl = label[:623]

    # NetzLaden
    netname = "categorical_crossentropy_hidden-softmax_output-softmax_above"
    net, offset = load_last_net(netname, _dir=directory)
    assert net is not None
    probabilities_a, probabilities_b = get_probability_lists(net, data=data, label=label)
    drawROC(probabilities_b, probabilities_a)


if __name__ == '__main__':
    main()
    #a = np.random.normal(0.45, 0.12, 1000)
    #b = np.random.normal(0.6, 0.12, 1000)
    #print(np.max(b), np.min(b))
    #a = [0.2,0.3,0.4,0.7]
    #b = [0.6, 0.8, 0.9]
    #drawROC(b, a)
