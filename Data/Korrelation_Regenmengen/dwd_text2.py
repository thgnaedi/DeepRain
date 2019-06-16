' r blogger über time '
import numpy as np

def make_lists():
    wp = open("date_and_rainfall.txt","r")
    rain_liste = []
    datum_liste = []
    for line in wp:
        a = line.split(" ")
        datum = a[0]
        value = a[1]
        rain_liste.append(value)
        datum_liste.append(datum)
    wp.close
    return datum_liste, rain_liste


def read_data(path):
    # open file
    fp = open(path, "r")
    wp = open("date_and_rainfall.txt","w")
    headers = fp.readline()
    for line in fp:
        datum, value = get_data(line,rainfallIndex=4)
        #endstr = datum[6:]
        wp.write(datum)
        wp.write(" ")
        wp.write(str(round(value,3)))
        wp.write(" ")
        wp.write("\n")
    fp.close
    wp.close


def get_hour(str):
    if str.length <= 10:
        return str[8] + str[9]

# returns date as String YYYYMMDDHHMM and rainfall as float32
def get_data(line, dateIndex=1, rainfallIndex=3):
    a = line.split(";")
    return (a[dateIndex], np.float32(a[rainfallIndex]))




def stuendlich():
    wr = open("date_and_rainfall.txt","r")
    wp = open("date_and_rainfall_hourly_june16.txt","w")
    regenmenge = 0.0
    index = 0

    for line in wr:
        a = line.split(" ")
        datum = a[0]
        value = float(a[1])
        if value != 0.0:
            #print(value, ' ', regenmenge)
            regenmenge = regenmenge + value
            #print('neue Menge:', regenmenge)

        if datum[11] == '0' and datum[10] == '0':
            wp.write(datum)
            wp.write(" ")
            wp.write(str(round(regenmenge,3)))
            wp.write(" ")
            wp.write("\n")
            regenmenge = 0.0
    wp.close
    wr.close







def secondNumber(num):
    if len(num) == 1:
        return ("0" + num) 
    else:
        return num   

def main(): 
    #read_data("produkt_ein_min_rr_20160601_20160630_02712.txt")
    #daten, regen = make_lists()
    stuendlich()
    
        
if __name__ == "__main__":
    main()