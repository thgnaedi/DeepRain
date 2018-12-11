import numpy as np
import WetterStation_KN.Read_TXT as rtxt

def read_historical_txt_file(path, return_all=False, showPeaks=True):
    assert path.__contains__("02712")               # check ID is Konstanz!
    rainsum_month = np.zeros(12, dtype=np.float32)  # Monthly rainfall
    all_data = []                                   # each measurement
    sum = 0
    n_rain = 0
    max_value = 0                                   # max ammount of rainfall
    date = None
    # open file
    fp = open(path, "r")
    headers = fp.readline()
    #STATIONS_ID;MESS_DATUM_BEGINN;MESS_DATUM_ENDE;QN;RS_01;RTH_01;RWH_01;RS_IND_01;eor
    for line in fp:
        datum, value = rtxt.get_data(line,rainfallIndex=4)
        all_data.append(value)
        sum += value
        if value > 0.0:
            n_rain += 1
            month = int(datum[4:6]) - 1
            rainsum_month[month] += value
            if value > max_value:
                max_value = value
                date = datum
        if value > 2.50 and showPeaks:
            print(rtxt.convert_date_pretty(datum), value)

    fp.close()
    if return_all:
        return rainsum_month, all_data, date, max_value, n_rain
    return rainsum_month


def vis_statistic_month(all_data, n_rain, max_value, date, month_id, rainsum_reference=None, showDetails=True, showHeader=True):
    np_data = np.array(all_data, dtype=np.float32)

    if showDetails:
        print("Ausgewerteter Monat:                      {}".format(str(month_id).zfill(2)))
        print("maximalwert:                              {:1.2f} erreicht am {}".format(max_value, rtxt.convert_date_pretty(date)))
        print("Regen/gesamt:                             {:1.2f}%".format(int(n_rain * 100 / np_data.size)))
        print("gesamt Regenmenge:                        {:1.2f}".format(np_data.sum()))
        print("Durchschnittliche regenmenge:             {:1.2f}".format(np_data.sum() / np_data.size))
        print("Durchschnittliche Regenmenge (bei Regen): {:1.2f}".format(np_data.sum() / n_rain))
    if rainsum_reference is not None:
        if showHeader:
            print("Monat\tRef.\tMess.\tDiff.")
        rel_err = -1
        if rainsum_reference > 0:
            rel_err = abs((rainsum_reference - np_data.sum()) / rainsum_reference)
        print(" {} \t{}\t{:1.2f}\t{:1.2f}".format(str(i).zfill(2), rainsum_reference, np_data.sum(), rel_err))
    return


if __name__ == '__main__':
    #Placeholder for month and day
    filename = "historical\\produkt_ein_min_rr_2017{}01_2017{}{}_02712"
    lastDayOfMonth=np.array([31,28,31,30,31,30,31,31,30,31,30,31])

    #ToDo regenreferenz einbauen:
    for i in range(1,13):
        rsm, all_data, max_date, max_value, n_rain= read_historical_txt_file(filename.format(str(i).zfill(2), str(i).zfill(2), lastDayOfMonth[i-1])+".txt", True, showPeaks=False)
        vis_statistic_month(all_data, n_rain, max_value, max_date, month_id=i, rainsum_reference=10.0, showDetails=False, showHeader=(i==1))

