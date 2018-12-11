import numpy as np
import WetterStation_KN.Read_TXT as rtxt

def read_historical_txt_file(path, return_all=False):
    assert path.__contains__("02712")               # check ID is Konstanz!
    rainsum_month = np.zeros(12, dtype=np.float32)  # Monthly rainfall
    all_data = []                                   # each measurement
    sum = 0
    n_rain = 0
    max_value = 0                                   # max ammount of rainfall
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
        if value > 2.50:
            print(rtxt.convert_date_pretty(datum), value)

    fp.close()
    if return_all:
        return rainsum_month, all_data, max_value
    return rainsum_month

if __name__ == '__main__':
    filename = "produkt_ein_min_rr_20171201_20171231_02712"

    rsm = read_historical_txt_file(filename+".txt")
    print(rsm)
