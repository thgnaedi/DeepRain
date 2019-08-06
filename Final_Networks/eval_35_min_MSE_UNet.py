from Data.evaluate_Network_on_realData import eval_trainlogfile
from Final_Networks.predict35minutes_MSE import generate_Data_5_7
from NetworkTypes.extendet_CNN_test import load_last_net
import numpy as np
import matplotlib.pyplot as plt

def eval_validationSet(data, label, net, usebase=True):

    #Netz predicten lassen
    firstdim = data.shape[0]
    prediction = net.predict(data)
    labelr = label.reshape((firstdim,64,64,7))
    predr = prediction.reshape((firstdim,64,64,7))


    #schauen, wie es sich über die Zeit (3te dimension verhält)
    __eval_by_time(firstdim, labelr, predr, data, usebase=usebase)

    #schauen, welcher Pixel wie gut korelliert ?
    #__eval_correlation(firstdim, labelr, predr, data)


    plt.show()
    return

def __eval_by_time(firstdim, labelr, predr, data, usebase=True):
    loss = []
    base = []
    zero = []
    for sample in range(firstdim):
        currentloss = []
        baselineloss = []
        zeroloss = []
        baseline = data[sample,:,:,4]
        for timestep in range(7):
            a = labelr[sample,:,:,timestep] - predr[sample,:,:,timestep]
            b = labelr[sample,:,:,timestep] - baseline
            #plotten? bzw. Bilder abspeichern!
            currentloss.append(np.sum(abs(a)))
            baselineloss.append(np.sum(abs(b)))
            zeroloss.append(np.sum(labelr[sample,:,:,timestep]))
        loss.append(currentloss)
        base.append(baselineloss)
        zero.append(zeroloss)
    l = np.array(loss)
    b = np.array(base)
    z = np.array(zero)

    suma = np.sum(l, axis=0)
    sumb = np.sum(b, axis=0)
    sumz = np.sum(z, axis=0)
    print("sum of prediction diff: ",   suma)
    print("sum of baseline diff: ",     sumb)
    print("sum of zero image diff: ",     sumz)

    if(not usebase):
        b = z   #zerso als vergleich verwenden
    fig, axes = plt.subplots(nrows=2, ncols=7, sharey=True, sharex=True)
    label = ["5min", "10min", "15min", "20min", "25min", "30min", "35min"]
    color = ['red', 'tan', 'lime', 'blue', 'orange', 'green', 'magenta']
    bins = [0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50]
    name_of_othermethod = "base "
    if not usebase:
        name_of_othermethod = "zeros "

    meanlinewidth=1
    for i in range(7):
        axes[0, i].hist(l[:, i], rwidth=0.7, color=color[i], label="pred " + label[i], density=True, bins=bins)
        axes[0, i].legend()
        axes[1,i].hist(b[:,i],rwidth=0.7,color=color[i], label=name_of_othermethod+label[i], density=True, bins=bins)
        axes[1,i].legend()

        axes[1,i].axvline(np.percentile(b[:, i], 25), alpha=0.7, color='gray', linestyle='dashed', linewidth=meanlinewidth)
        axes[0,i].axvline(np.percentile(l[:, i], 25), alpha=0.7, color='gray', linestyle='dashed', linewidth=meanlinewidth)
        axes[1,i].axvline(np.percentile(b[:, i], 75), alpha=0.7, color='gray', linestyle='dashed', linewidth=meanlinewidth)
        axes[0,i].axvline(np.percentile(l[:, i], 75), alpha=0.7, color='gray', linestyle='dashed', linewidth=meanlinewidth)

        axes[1, i].axvline(b[:, i].mean(), color='k', linestyle='dashed', linewidth=meanlinewidth)
        axes[0, i].axvline(l[:, i].mean(), color='k', linestyle='dashed', linewidth=meanlinewidth)

    fig2, axes = plt.subplots(nrows=1, ncols=7, sharey=True, sharex=True)
    for i in range(7):
        axes[i].axvline(l[:, i].mean(), color="blue", linestyle='dashed', linewidth=meanlinewidth)
        axes[i].axvline(b[:, i].mean(), color="orange", linestyle='dashed', linewidth=meanlinewidth)
        axes[i].hist(l[:, i], rwidth=1.0,color="blue", label="pred " + label[i], density=True, bins=bins)
        axes[i].hist(b[:,i],rwidth=0.5,color="orange", label=name_of_othermethod+label[i], density=True, bins=bins)
        axes[i].legend()

    plt.figure("performance change over time (prediction)")
    plt.hist(l[:, 0], color=color[0], density=True, bins=bins, histtype = 'step', fill = False, label="5min")
    plt.hist(l[:, 6], color=color[5], density=True, bins=bins, histtype = 'step', fill = False, label="35min")
    plt.legend()

    plt.figure("performance change over time ({})".format(name_of_othermethod))
    plt.hist(b[:, 0], color=color[0], density=True, bins=bins, histtype = 'step', fill = False, label="5min")
    plt.hist(b[:, 6], color=color[5], density=True, bins=bins, histtype = 'step', fill = False, label="35min")
    plt.legend()
    return

def __eval_correlation(firstdim, labelr, predr, data, vmax=10):
    suml = np.zeros((64,64,7))
    sumb = np.zeros((64, 64, 7))
    for sample in range(firstdim):
        baseline = data[sample, :, :, 4]

        a = labelr[sample, :, :, :] - predr[sample, :, :, :]
        b = np.zeros((64,64,7))

        for timestep in range(7):
            b[:,:,timestep] = labelr[sample, :, :, timestep] - baseline

        suml += np.abs(a)
        sumb += np.abs(b)

    for i in range(7):
        plt.figure("Prediction "+str(i*5+5)+" min")
        plt.text(46,63,"sum: "+str(int(np.sum(suml[:, :, i]))), color="white")
        plt.imshow(suml[:, :, i], vmax=vmax, vmin=0)
        plt.figure("Baseline "+str(i*5+5)+" min")
        plt.text(46,63,"sum: "+str(int(np.sum(sumb[:, :, i]))), color="white")
        plt.imshow(sumb[:, :, i], vmax=vmax, vmin=0)

    return


if __name__ == '__main__':
    #Lernkurve:
    eval_trainlogfile("./trainphase_MSE.log", plot=True)

    #DatenSammeln
    s1,s2 = generate_Data_5_7("..\\Data\\samplebundles\\{}_5in_7out_64x64_without_border", only_2004=True)

    all_data=None
    for bundle in s1:
        data, label = bundle.get_all_data_label(channels_Last=True, flatten_output=True)
        if all_data is None:
            all_data = data
            all_label = label
        else:
            all_data = np.concatenate((all_data,data), axis=0)
            all_label = np.concatenate((all_label, label), axis=0)
    validation_data = all_data[:623]
    validation_label = all_label[:623]

    net,offset = load_last_net("10years")
    assert net is not None
    eval_validationSet(validation_data, validation_label, net, usebase=False)
    ## Lernkurve beschreiben, beides Fällt stark, dann auswerten, ob Fehler auch gut ist.
    ## Pro Zeitschritt evaluieren
    ## Nochmal Trainieren lassen und nochmal evaluieren, ob das muster weitergeht