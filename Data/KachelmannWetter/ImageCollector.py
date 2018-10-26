import matplotlib.pyplot as plt
import urllib
import numpy as np
import cv2

TARGET_PATH = "RadarData/"
HDR = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

def collect_one_img(tt, mm, yyyy, hh, mn, store=False):
    url = "https://img3.kachelmannwetter.com/images/data/cache/radar/radar-de-310-1_"
    name = yyyy + "_" + mm + "_" + tt + "_259_" + hh + mn + ".png"
    url += name

    req = urllib.request.Request(url, headers=HDR)
    resp = urllib.request.urlopen(req)

    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    if store:
        cv2.imwrite(TARGET_PATH+name, image)

    return image


def collect_day(tt, mm, yyy):
    for hh in range(24):
        for mn in range(0,60,5):
            collect_one_img(tt, mm, yyy, '{0:02d}'.format(hh), '{0:02d}'.format(mn), store=True)

    return

if __name__ == '__main__':
    collect_day("01","10","2018")
