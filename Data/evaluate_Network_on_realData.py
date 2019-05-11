import matplotlib.pyplot as plt
import numpy as np
import sample_bundle
from eval_stored_network import load_model
from evaluate_realData import display_one_img



#Alle Netze laden und lernkurve (auf ein bsp Bild) anzeigen
#letztes Bild auf alle testdaten laufen lassen und MSE berechnen für letztes Bild und für ausgabe
    # Schlechteste Werte anschauen und auswerten.
def load_and_eval_network(testdata, testlabel, learncurvesample, learncurvelabel, network_path_prefix, networkpath_postfix = "", max_number_networks=100, plotit=True):
    learncurve = []
    for i in range(1, max_number_networks+1):
        net_model = load_model(network_path_prefix+str(i)+networkpath_postfix+".h5", verbose=True)
        prediction = net_model.predict(np.expand_dims(learncurvesample, axis=0))
        MSE = (np.square(learncurvelabel.flatten() - prediction)).mean(axis=1)
        learncurve.append(MSE)

    lbl, base = compare_mse(net_model, testdata, testlabel)

    if plotit:
        plt.plot(learncurve)
        plt.xlabel("epoch")
        plt.ylabel("mse")
        plt.title("learning curve")
        plt.show()
    print("lc",learncurve)
    print("lbl",lbl)
    print("base",base)

    return net_model, (learncurve, lbl, base)

def compare_mse(net_model, testdata, testlabel):
    values_on_label = []
    values_baseline = []
    for i in range(len(testdata)):
        prediction = net_model.predict(np.expand_dims(testdata[i], axis=0))
        MSE = (np.square(testlabel[i].flatten() - prediction)).mean(axis=1)
        Baseline = (np.square(testlabel[i].flatten() - testdata[i][..., 4].flatten())).mean(axis=0)
        values_on_label.append(MSE)
        values_baseline.append(Baseline)
    return values_on_label, values_baseline


def default_values_UNet64_2016():
    learningcurve = [0.0125825, 0.01090752, 0.00996938, 0.00877155, 0.00785926, 0.00749076, 0.00738954, 0.00710216,
                     0.00695553, 0.00685954, 0.00685263, 0.00683551, 0.0067013, 0.00669573, 0.00663494, 0.0065361,
                     0.00656253, 0.00655892, 0.00641627, 0.00643257, 0.00642143, 0.00643228, 0.00638859, 0.00635681,
                     0.00639316, 0.00631695, 0.0062926, 0.00633417, 0.00622689, 0.00616801, 0.00625138, 0.00621941,
                     0.00615199, 0.00620083, 0.00616311, 0.00617193, 0.00621265, 0.00614376, 0.0061507, 0.00614031,
                     0.00610141, 0.00613152, 0.00613031, 0.00610272, 0.00609479, 0.0061553, 0.0061067, 0.00605778,
                     0.00606069, 0.00603255, 0.00605208, 0.00601227, 0.00600995, 0.00601041, 0.00601996, 0.0060082,
                     0.00602065, 0.00619004, 0.00603388, 0.00603091, 0.00607781, 0.00611581, 0.00606192, 0.00599001,
                     0.00598812, 0.00596377, 0.00595005, 0.00597897, 0.00595829, 0.00594891, 0.00595861, 0.00597969,
                     0.00591869, 0.00593133, 0.00592642, 0.00592538, 0.00590671, 0.00598633, 0.0060014, 0.00590481,
                     0.00590337, 0.00598106, 0.00590425, 0.00589903, 0.00587542, 0.00588902, 0.0059049, 0.00590722,
                     0.00590535, 0.00589348, 0.00586809, 0.00586199, 0.00587707, 0.00585575, 0.00584643, 0.00583368,
                     0.00580768, 0.00581735, 0.00581284, 0.00581762]

    prediction_loss = [2.05482041e-06, 2.16494586e-06, 2.3332747e-06, 2.07652893e-05, 0.00015295, 0.00028465,
                       0.00031767, 0.00037503, 0.00047629, 0.00070817, 0.00069556, 0.00071058, 0.00068717, 0.00085751,
                       0.00080836, 0.00068803, 0.0004593, 0.00038036, 0.00023775, 0.00016827, 0.00018715, 0.0001683,
                       9.01244588e-05, 1.11477099e-08, 6.33360328e-07, 1.02075804e-05, 3.32653464e-05, 3.32339511e-06,
                       2.88497277e-06, 5.62943246e-05, 1.4668768e-05, 5.08214763e-08, 5.38758653e-06, 3.22183944e-05,
                       8.69566071e-05, 0.00017487, 0.00013233, 0.00017856, 0.00021881, 0.0002324, 0.00027731,
                       0.00024965, 0.00020651, 5.31775661e-05, 4.04651739e-05, 4.03603105e-05, 1.04818476e-05,
                       2.91035737e-05, 7.37178008e-05, 5.13091154e-06]

    baseline_loss = [7.396494136870434e-07, 2.2677575932333715e-06, 3.161344194540561e-06, 3.26459474721261e-05,
                     0.0002704300929930796, 0.0005964502835447904, 0.0006755326977604766, 0.0008103178465013457,
                     0.001028285395040369, 0.0014358960495963091, 0.0013702099252691272, 0.0013215620194156094,
                     0.0014910693903787005, 0.0014552545895809305, 0.0016509913554882737, 0.001446596561418685,
                     0.0009419228782199154, 0.0006850129757785468, 0.0004638991013071895, 0.000308084630911188,
                     0.0003598450716070742, 0.000374457840734333, 0.00034752258746635915, 0.0, 4.8997080449827e-06,
                     1.4049584294502115e-05, 8.270181540753557e-05, 7.411512399077278e-06, 3.195135284505959e-06,
                     4.742391748366013e-05, 5.453881920415225e-05, 1.87728277585544e-06, 9.476523452518261e-06,
                     5.482041162053057e-05, 0.00013154871323529412, 0.0002496222907054979, 0.00020320459678969626,
                     0.00028636822376009233, 0.00028379259179161864, 0.0003579677888312187, 0.0004275173611111111,
                     0.00031476400302768166, 0.00024243229767397157, 8.324622741253364e-05, 5.39718798058439e-05,
                     8.502964604959632e-05, 1.7590139609765473e-05, 5.9633764657823906e-05, 0.00017642328070934256,
                     8.902074923106497e-06]

    statistical_evaluation_lr_baseline(baseline_loss, prediction_loss, learningcurve)
    samplebundle = sample_bundle.load_Sample_Bundle("RegenTage2016")
    samplebundle.normalize()
    blul = (([0, 63]), ([35, 35], "blueviolet"))
    purl = (([0, 63]), ([41, 41], "purple"))
    skyl = (([3, 32]), ([35, 17], "skyblue"))
    orl = (([32, 32]), ([0, 63], "orange"))
    display_one_img(samplebundle, 14, [[],[],[],[],[skyl,purl,blul,orl],[skyl,purl,blul,orl]], vmax=0.85)

    net_model = load_model("C:\\Users\\TopSecret!\\Documents\\aMSI1\\Teamprojekt\\DeepRain\\NetworkTypes\\UNet64\\UNet64_2016_100.h5", verbose=False)
    data, label = samplebundle.get_all_data_label(channels_Last=True)
    prediction = net_model.predict(np.expand_dims(data[14], axis=0))
    plt.imshow(prediction.reshape((64, 64)).T, cmap="gray", vmax=0.85)
    plt.plot(blul[0], *blul[1])
    plt.plot(purl[0], *purl[1])
    plt.plot(skyl[0], *skyl[1])
    plt.plot(orl[0], *orl[1])
    plt.title("prediction")
    plt.show()
    return


def statistical_evaluation_lr_baseline(baseline_loss, prediction_loss, learningcurve=None):
    assert len(baseline_loss) == len(prediction_loss)

    mean_bl = np.mean(np.array(baseline_loss))
    mean_pr = np.mean(np.array(prediction_loss))

    if learningcurve is not None:
        plt.plot(learningcurve, "orange")
        plt.xlabel("epoch")
        plt.ylabel("mse")
        plt.title("learning curve")
        plt.show()


    plt.plot(baseline_loss, "g+", label="baseline")
    plt.plot(prediction_loss, "r+", label="prediction")
    plt.plot(baseline_loss, "g", alpha=0.1)
    plt.plot(prediction_loss, "r", alpha=0.1)
    plt.plot([0,49], [mean_pr,mean_pr], "r", linewidth=2, alpha=0.5)
    plt.plot([0,49], [mean_bl,mean_bl], "g", linewidth=2, alpha=0.5)
    plt.legend()
    plt.show()
    return


if __name__ == '__main__':
    loadAndEval = False
    show_UNet2016 = True

    if loadAndEval:
        sb = sample_bundle.load_Sample_Bundle("RegenTage2016")
        sb.normalize()
        data, label = sb.get_all_data_label(channels_Last=True)
        test_samples = data[:50]
        test_labels = label[:50]
        lcd = data[896]
        lcl = label[896]
        path = "C:\\Users\\TopSecret!\\Documents\\aMSI1\\Teamprojekt\\DeepRain\\NetworkTypes\\UNet64\\UNet64_2016_"
        load_and_eval_network(plotit= True, testdata=test_samples, testlabel=test_labels, learncurvesample=lcd, learncurvelabel=lcl, network_path_prefix=path,max_number_networks=100)
    if show_UNet2016:
        default_values_UNet64_2016()
