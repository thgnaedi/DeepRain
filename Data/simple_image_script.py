import matplotlib.pyplot as plt
import cv2
import numpy as np
import os
import glob
import re

class Data_converter():
    def __init__(self, path, max_num_samples, n_data, n_label, start_img=None, sachenzumZuschneiden=None):
        assert  os.path.exists(path)
        if start_img is not None:
            assert os.path.exists(start_img)
        assert n_data > 0 and n_label > 0
        self.path = path
        self.max_num_samples = max_num_samples
        self.n_data = n_data
        self.n_label = n_label
        #ToDo:
        self.subimg = ((100, 100), (200, 200))
        self.resize_shape = (60, 60)

        self.collect_images()
        self.create_images()

        print("data", self.all_samples[0][0].shape, "label", self.all_samples[0][1].shape)
        return

    def collect_images(self):
        self.all_images = []
        path = self.path+"*.png"
        for image_path in glob.glob(path):
            self.all_images.append(image_path)
        self.all_images.sort()  # Sortieren
        #ToDo: pattern ersetzen durch regexp
        pattern = "raa01-rw_10000"
        while len(self.all_images) > 0 and pattern not in self.all_images[0]:
            del self.all_images[0]
        while len(self.all_images) > 0 and pattern not in self.all_images[-1]:
            del self.all_images[-1]
        #ToDo: jetzt schauen ob Zeitstempel alle passen, sonst fehlerhafte rauslöschen
        #       Abhängig von n_data und n_label müssen entsprechende anzahl Elemente passen.
        return

    def create_images(self):
        min_n = self.n_data+self.n_label
        self.all_samples = []
        while len(self.all_images) >= min_n:
            data = None
            label = None
            for i in range(self.n_data):
                current = self.all_images.pop(0)
                current = open_one_img(path=current, _subimg=self.subimg, _resize_shape=self.resize_shape, raiseError=True)
                if data is None:
                    data = np.atleast_3d(current)
                else:
                    data = np.dstack((data, current))
            for i in range(self.n_label):
                current = self.all_images.pop(0)
                current = open_one_img(path=current, _subimg=self.subimg, _resize_shape=self.resize_shape, raiseError=True)
                if label is None:
                    label = np.atleast_3d(current)
                else:
                    label = np.dstack((label, current))
            one_sample = (data, label)
            self.all_samples.append(one_sample)

        return

def open_2D_img(path):
    img = cv2.imread(path)
    if img is None:
        print("Datei nicht vorhanden")
        return None
    if len(img.shape) > 2:
        print("Eingelesenes Bild hat zu hohe Dimension (wird gekürzt auf 2D)")
        img = img[:,:,0]
    return img


def resize_img(img, shape=(65, 65)):
    # INTER_NEAREST - a nearest-neighbor interpolation
    # INTER_LINEAR - a bilinear interpolation (used by default)
    # INTER_AREA - resampling using pixel area relation. It may be a preferred method for image decimation, as it gives moire’-free results. But when the image is zoomed, it is similar to the INTER_NEAREST method.
    # INTER_CUBIC - a bicubic interpolation over 4x4 pixel neighborhood
    # INTER_LANCZOS4 - a Lanczos interpolation over 8x8 pixel neighborhood

    if shape is None:
        return img
    if isinstance(shape, int):
        shape = (shape,shape)
    assert isinstance(shape, tuple)
    res = cv2.resize(img, dsize=shape, interpolation=cv2.INTER_CUBIC)
    return res

def select_subimg(img, startpos=(0,0), _size=None, raiseError=False):
    size = _size
    assert isinstance(startpos, tuple)
    tmp = (img.shape[0] - startpos[0], img.shape[1] - startpos[1])
    if tmp[0] < 1 or tmp[1] < 1:
        print("subimg nicht möglich!")
        if raiseError:
            raise ValueError("startposition out of range!")
        return img
    if size is None:
        size = tmp
    size = (min(size[0],tmp[0]), min(size[1],tmp[1]))
    if raiseError and not size == _size:
        raise ValueError("selected size not possible with startposition "+str(startpos))

    return img[startpos[0]:startpos[0]+size[0],startpos[1]:startpos[1]+size[1]]


#ToDo: Methode noch nicht verwendet, später in Objekt ziehen!
def list_to_set(imgList, n_input, n_output):
    x = None
    y = None

    assert (n_input + n_output <= len(imgList))

    for i in range(n_input + n_output):
        img = imgList[i][:, :, 0]
        if i < n_input:
            if x is None:
                x = np.atleast_3d(img)
            else:
                x = np.dstack((x, img))
        else:
            if y is None:
                y = np.atleast_3d(img)
            else:
                y = np.dstack((y, img))
    return (x, y)


def open_one_img(path, _subimg=None, _resize_shape=None, raiseError=False, show_result=False):
    img2D = open_2D_img(path)
    if _subimg is None:
        img2D_sub = img2D
    else:
        assert isinstance(_subimg, tuple)
        img2D_sub = select_subimg(img2D, startpos=_subimg[0], _size=_subimg[1], raiseError=raiseError)
    if _resize_shape is None:
        scaled = img2D_sub
    else:
        scaled = resize_img(img2D_sub,shape=_resize_shape)
    if show_result:
        images = [img2D, img2D_sub, scaled]
        titles = ["Original Bild", "Ausschnitt (200x200)", "Skaliert (80x80)"]
        fig = plt.figure()
        columns = 3
        rows = 1
        for i in range(len(images)):
            fig.add_subplot(rows, columns, i + 1)
            plt.imshow(images[i], vmin=0, vmax=255, cmap="gray")
            plt.title(titles[i])
        plt.show()
    return scaled


def usage():
    path = "raa01-rw_10000-0506301650-dwd---bin.gz.png"
    print("lese Bild:", path)

    # Einfaches einlesen eines Bildes:
    OriginalBild = open_one_img(path)
    # Auswählen eines Ausschnittes (zb. region 200x200 Pixel um Konstanz):
    Ausschnitt = open_one_img(path, _subimg=((100, 100), (200, 200)))
    # Skalierter output -> output-Bildgröße = 60x60
    Skaliert = open_one_img(path, _resize_shape=60)
    # alles in einem, mit show_result -> öffnet Plot, welcher die einzelnen Schritte zeigt
    Demo = open_one_img(path, _subimg=((100, 100), (200, 200)), _resize_shape=(60, 60), raiseError=True,
                        show_result=True)


if __name__ == '__main__':
    path = ".\\"
    Data_converter(path=path, max_num_samples=2, n_data=2, n_label=1, start_img=None)

