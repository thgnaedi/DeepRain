import matplotlib.pyplot as plt
import numpy as np
import sample_bundle

'''
Skript zum schnellen Auswerten eines "SampleBundles",
bewertet Verteilung der Graustufen und stellt histogramm dar.
Bewertet zusätzlich prozentualen Anteil an sinnvollen Bundles (Daten mit Regen),
und gibt den Maximalwert aus (optimaler weise 100% und 255).
'''
def show_sample(samples, vmax=100, title="one Sample", return_ax=False):
    if len(samples) == 6:
        return __show_sample_6__(samples, vmax, title, return_ax)
    assert(len(samples) == 5)
    f, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(1, 5)
    all_axes = [ax1, ax2, ax3, ax4, ax5]
    for i in range(5):
        all_axes[i].imshow(samples[i], vmin=0, vmax=vmax, cmap="gray")
        all_axes[i].set_title("timestep "+str(i))
    f.suptitle(title)
    if return_ax:
        return all_axes
    return

def __show_sample_6__(samples, vmax, title, return_ax):
    assert(len(samples) == 6)
    f, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2,3)
    all_axes = [ax1, ax2, ax3, ax4, ax5, ax6]
    for i in range(6):
        all_axes[i].imshow(samples[i], vmin=0, vmax=vmax, cmap="gray")
        all_axes[i].set_title("timestep "+str(i))
    f.suptitle(title)
    if return_ax:
        return all_axes
    return


def quick_eval(sb, plotit=False, get_all_max=False):
    data, label = sb.get_all_data_label(channels_Last=False)
    n_hits = 0
    maximum_value = 0
    all_max = []
    for i in range(data.shape[0]):
        m = np.max(data[i])
        all_max.append(m)
        if m > 0:
            #print(m)
            if m > maximum_value:
                maximum_value = m
                if plotit is not False:
                    show_sample([data[i][0], data[i][1], data[i][2], data[i][3], data[i][4]], vmax=m)
                    plt.show()
            n_hits += 1
    print("there are {} usefull images [{}%], maximum value was: {}".format(n_hits, n_hits*100/data.shape[0],maximum_value))
    if get_all_max:
        return all_max
    return

def display_one_img(samplebundle, img_id, details=None, vmax=1):
    samplebundle.normalize()
    data, label = samplebundle.get_all_data_label(channels_Last=False)
    axes = show_sample([data[img_id][0], data[img_id][1], data[img_id][2], data[img_id][3], data[img_id][4],
                        label[img_id].reshape((64, 64))], vmax=vmax, return_ax=True)
    mses = []
    if details is not None:
        for i in range(len(axes)):
            detail = details[i]
            for d in detail:
                axes[i].plot(d[0],*d[1])
            #if i < 5:
            #    lbl = label[img_id].flatten()
            #    dta = data[img_id][i].flatten()
            #    mse = (np.square(lbl - dta)).mean()
            #    mses.append(mse)

    #print("MSE would be:",mses)
    plt.show()

if __name__ == '__main__':

    ### quick eval soll schnellen überblick liefern
    sb = sample_bundle.load_Sample_Bundle("RegenTage2016")
    quick_eval(sb)

    ### anschauliche darstellung von Daten&label aus 2016 (1 Bsp.)
    redl = (([0,63]), ([35,35], "r"))
    orl = (([35,35]), ([0,63], "orange"))
    #display_one_img(sb, 896, [[redl,orl],[redl,orl],[redl,orl],[redl,orl],[redl,orl],[redl,orl]])


### vergleiche Skalierungsfaktoren von 2016
    #print("beginne Auswertung:")
    #dataset = ["TestData2016", "TestData2016EDIT", "TestData2016MAL20", "RegenTage2017_5_7_kn_centered"]
    #for d in dataset:
    #    print("\n",d)
    #    sb = sample_bundle.load_Sample_Bundle(d)
    #    #print(sb.info())
    #    all_m = quick_eval(sb, get_all_max=True)
    #    plt.figure(d)
    #    plt.title(d)
    #    plt.hist(all_m, bins=25, log=True)
    #plt.show()


## Einzelbildauswertung:
    sb = sample_bundle.load_Sample_Bundle("RegenTage2017_5_7_kn_centered")
    print(sb.info())
    data, label = sb.get_all_data_label(False)
    for i in range(sb.get_number_samples()):
        m = np.max(data[i])
        if m < 0.9:
            continue
        l = label[i]
        if len(l.shape) > 2:
            l = l[:,:,0]
        show_sample([data[i][0], data[i][1], data[i][2], data[i][3], data[i][4], label[i][0].reshape((64,64))], vmax=255, title="id: {} max: {}".format(i, m))
        plt.show()


    #sb.clear_samples()
    #input(sb.info())
    #sb.clear_samples()
    #sb.save_object("Sauber")
