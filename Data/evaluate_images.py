import simple_image_script as sis
import numpy as np
import matplotlib.pyplot as plt
import os



def generate_Histogramm(img, plot=False, _print=True):
    hist, _ = np.histogram(img, bins=255, range=(0,254))
    mi = np.amin(img)
    ma = np.amax(img)
    if plot:
        plt.hist(img, bins=np.arange(255))
        plt.title("histogram")
        plt.show()
    else:
        if _print:
            print(hist)
    return (hist, mi, ma)


def get_statistic(path, max_num_samples):
    n_data = 1                            # Anzahl Zeitschritte (t) für die Eingangsdaten (x,y,t) bei n_data=3 werden also
                                            # 3 aufeinander folgende Bilder als Eingabe verwendet.
    n_label = 1                           # Anzahl Zeitschritte (t) für das Label ( wie viele Zeitschritte vorhergesagt werden sollen)
    start_img = None                      # Noch nicht verwendet, später soll hiermit trainingsdaten z.B ab 2010 sein und Label ab 1018
    subimg_startpos = (600, 400)           # Zum Ausschneiden eines Bereichs aus dem gesammtbild // (0,0) ist oben Links!
    subimg_shape = (200, 200)              # Größe des Ausschnittes von startpos beginnend
    output_shape = 60                     # Größe des outputs (resize)

    # einige Parameter haben default werte, angegeben werden muss auf jedenfall:
    # path, max_num_samples, n_data, n_label
    dc = sis.Data_converter(path, max_num_samples, n_data, n_label, start_img, subimg_startpos, subimg_shape, output_shape, silent=True)


    all_results = []
    for i in range(dc.get_number_samples()):
        sample = dc.get_next()
        all_results.append(generate_Histogramm(sample[0], _print=False))
        all_results.append(generate_Histogramm(sample[1], _print=False))

    ## alle ergebnisse gesammelt, jetzt evaluieren
    durchschnitt = np.zeros(255)
    absmax = 0
    absmin = 255
    anz = 0
    for e in all_results:
        if absmax < e[2]:
            absmax = e[2]
        if absmin > e[1]:
            absmin = e[1]
        durchschnitt=np.add(durchschnitt, e[0])
        anz += 1
    return (durchschnitt/anz).astype(int), absmin, absmax