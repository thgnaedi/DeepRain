import numpy as np


# returns date as String YYYYMMDDHHMM and rainfall as float32
def get_data(line):
    a = line.split(";")
    return (a[1], np.float32(a[3]))


# change representation of String from .txt file
def convert_date_pretty(date):
    return "{}.{}.{} {}:{}".format(date[6:8], date[4:6], date[0:4], date[8:10], date[10:12])


# Path to local copy
PATH = "produkt_ein_min_rr_20180101_20181125_02712"

# open file
fp = open(PATH + ".txt", "r")
headers = fp.readline()
## header = ID; ?; ?; Regenmenge; ?

for line in fp:
    datum, value = get_data(fp.readline())
    if value > 0.0:
        print(convert_date_pretty(datum), value)
        # print(datum)

fp.close()
