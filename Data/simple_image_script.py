import matplotlib.pyplot as plt
import cv2
import numpy as np
import os
import glob
import pickle
import sys

try:    #commandline import
    import sample_bundle as sb
except: #IDE import with other cwd
    import Data.sample_bundle as sb


class Data_converter():
    def __init__(self, path, max_num_samples, n_data, n_label, start_img=None, subimg_startpos=None, subimg_shape=None,
                 output_shape=None, silent=False, pre="scaled_raa01-yw2017.002_10000-", post="-dwd---bin.png", invalid_value=-1):
        """
		Object to create sampleBundles (.sb File) from given path and parameters.
		path			Directory with radar images
		max_num_samples	collection progress will stop if number of samples reached max or no more images are avaliable in the given path
		n_data			number of images/timesteps for input data (n_data=5 means 5 consecutive pictures are used as input)
		n_label			number of images/timesteps for output data
        start_img       not implemented yet, set this to None
        subimg_startpos tupel with x,y coordinates were subimage sould be taken from
        subimg_shape    tupel with shape of the selected subimage, can also be None
        output_shape    None, tuple or int, shape for images, can be used to rescale the selected subimage.
		silent			True means no print messages
		pre				offset for imagenames, should be changed, if PNGs are renamed
		post			see post just after timestep
		invalid_value	int, pixels with this value will be repaced by zero (can be used to remove pixels without radardata at the edges)
        """
        assert os.path.exists(path)
        if start_img is not None:
            assert os.path.exists(start_img)
            raise NotImplementedError("Path is okay, but functionality not implemented yet!")
        assert n_data > 0 and n_label > 0
        self.path = path
        self.silent = silent
        self.max_num_samples = max_num_samples
        self.n_data = n_data
        self.n_label = n_label
        self.pre = pre
        self.post = post
        if subimg_startpos is None or subimg_shape is None:
            self.subimg = None
        else:
            assert isinstance(subimg_startpos, tuple)
            assert isinstance(subimg_shape, tuple)
            self.subimg = (subimg_startpos, subimg_shape)  # z.B. ((100, 100), (200, 200))
        assert output_shape is None or isinstance(output_shape, tuple) or isinstance(output_shape, int)
        self.resize_shape = output_shape  # (60, 60)

        self.all_images = self.collect_images()
        if len(self.all_images) > 0:
            self.create_images(invalid_value)

        self.id = 0  # id for .get_next()
        if not self.silent:
            print("data", self.all_samples[0][0].shape, "label", self.all_samples[0][1].shape)
        return

    def get_next(self):
        tmp = self.all_samples[self.id]
        self.id += 1
        if len(self.all_samples) > self.id:
            self.id = 0
        return tmp

    def get_item_at(self, i):
        return self.all_samples[i]

    def get_number_samples(self):
        return len(self.all_samples)

    def _info(self):
        return "DWD Radarbilder"  # ToDo: shape len usw.

    def collect_images(self):
        all_images = []
        path = self.path + "*.png"
        for image_path in glob.glob(path):
            all_images.append(image_path)
        all_images.sort()  # Sortieren
        # ToDo: pattern ersetzen durch regexp
        pattern = self.pre
        while len(all_images) > 0 and pattern not in all_images[0]:
            del all_images[0]
        while len(all_images) > 0 and pattern not in all_images[-1]:
            del all_images[-1]

        all_valid_images = []
        print("found",len(all_images), "in", self.path)
        legals = []
        first_d = None
        next_d = None
        datecomp = Date_Comperator(pre=self.path + self.pre, post=self.post)
        for i in all_images:
            first_d = next_d
            next_d = i
            if first_d is None:
                legals = [next_d]
                continue
            if datecomp.compare(first_d, next_d):
                # Datum okay:
                legals.append(next_d)
                if len(legals) == self.n_data + self.n_label:
                    all_valid_images.extend(legals)
                    next_d = None
                    legals = []
            else:
                # Datum nicht okay
                legals = [next_d]
        print("could create", len(all_valid_images), "samples")
        return all_valid_images

    def create_images(self, invalid_value):
        min_n = self.n_data + self.n_label
        self.all_samples = []
        number_done = 0
        print("creating {} images:".format(min(int(len(self.all_images)/min_n), self.max_num_samples)))
        number_todo = min(int(len(self.all_images)/min_n), self.max_num_samples)
        while len(self.all_images) >= min_n:
            data = None
            label = None
            error = False
            for i in range(self.n_data):
                current = self.all_images.pop(0)
                current = open_one_img(path=current, _subimg=self.subimg, _resize_shape=self.resize_shape,
                                       raiseError=True, silent=self.silent, invalid_value=invalid_value)
                if current is None:
                    #Open schlug Fehl!
                    error = True
                    break
                if data is None:
                    data = np.atleast_3d(current)
                else:
                    data = np.dstack((data, current))
            for i in range(self.n_label):
                if error:
                    break
                current = self.all_images.pop(0)
                current = open_one_img(path=current, _subimg=self.subimg, _resize_shape=self.resize_shape,
                                       raiseError=True, silent=self.silent, invalid_value=invalid_value)
                if current is None:
                    error = True
                    break
                if label is None:
                    label = np.atleast_3d(current)
                else:
                    label = np.dstack((label, current))
            if error:
                continue
            one_sample = (data, label)
            self.all_samples.append(one_sample)
            number_done += 1
            if number_done % 10 == 0:
                percentage = int((number_done / number_todo)*100)
                sys.stdout.write("\r{}% |{}{}|".format(percentage,'#' * int(percentage/5),' ' * (20 - int(percentage/5))))
                sys.stdout.flush()
            if len(self.all_samples) == self.max_num_samples:
                break
        return

    def save_object(self, filename, details="", clear=0, ignorevalue=-1, move=True, percentage=0.2):
        """
        :param filename:    name for stored object
        :param details:     custom infostring, will be displayed by calling .info()
        :param clear:       minimum value, can be used to delete empty samples
        :param ignorevalue: can be used to clipp the 'out of Range' values (no radar data avaliable at this pixel)
        :param move:        if True, samples without moveing will be deleted
        :return:            None
        """
        filename += ".sb"
        obj = sb.Sample_Bundle(self.subimg, self.resize_shape, self.all_samples, details=details)
        if clear > 0:
            obj.clear_samples(threshold=clear, ignorevalue=ignorevalue, move=move, percentage=percentage)
        with open(filename, 'wb') as output:  # Overwrites any existing file.
            pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)
        return

class Date_Comperator():
    def __init__(self, pre, post, timediff=5):
        self.pre = pre
        self.post = post
        self.diff = timediff

    def compare(self, vFirst, vNext):
        try:
            time = vFirst.replace(self.pre, "").replace(self.post, "")
            time = int(time)
            time2 = vNext.replace(self.pre, "").replace(self.post, "")
            time2 = int(time2)
            if time == time2 - self.diff:
                return True         #Basisfall 16:05 && 16:10
            return time == time2-45 #Sonderfall 16:55 && 17:00
        except:
            raise ValueError("There are problems converting img name to timestamp!",self.pre, self.post)
            return False


def open_2D_img(path, silent=False):
    img = cv2.imread(path)
    if img is None:
        if not silent:
            print("Datei nicht vorhanden")
        return None
    if len(img.shape) > 2:
        if not silent:
            print("Eingelesenes Bild hat zu hohe Dimension (wird gekürzt auf 2D)")
        img = img[:, :, 0]
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
        shape = (shape, shape)
    assert isinstance(shape, tuple)
    res = cv2.resize(img, dsize=shape, interpolation=cv2.INTER_CUBIC)
    return res


def select_subimg(img, startpos=(0, 0), _size=None, raiseError=False):
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
    size = (min(size[0], tmp[0]), min(size[1], tmp[1]))
    if raiseError and not size == _size:
        raise ValueError("selected size not possible with startposition " + str(startpos))

    return img[startpos[0]:startpos[0] + size[0], startpos[1]:startpos[1] + size[1]]


# ToDo: Methode noch nicht verwendet, später in Objekt ziehen!
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


def open_one_img(path, _subimg=None, _resize_shape=None, raiseError=False, show_result=False, silent=False, vmax=None, invalid_value=-1, clip=False) -> np.ndarray:
    """
    :param path:            path for the image to open
    :param _subimg:         tuple to restrict the image area: tuple like ( (y,x-coordinate to start at), (width, height - to cut out subimage) ), can be None
    :param _resize_shape:   shape to resize the selected subimage, can be None
    :param raiseError:      should be set to True while testing areas to get Error messages, can be disabled later, default=False
    :param show_result:     plots a figure if set to True
    :param silent:          if set to True, no outputs will be printed
    :param vmax:            optional clipping the image to vmax
    :param invalid_value:   optional value for pixels without radar data
    :param clip:            if set to True, values will be at least zero, no clipping for max value
    :return:                image (numpy ndarray)
    """
    img2D = open_2D_img(path, silent)
    if img2D is None:
        print("open_one_img failed for:", path)
        return None
    if vmax is None:
        vmax = 255
    if _subimg is None:
        img2D_sub = img2D
    else:
        assert isinstance(_subimg, tuple)
        img2D_sub = select_subimg(img2D, startpos=_subimg[0], _size=_subimg[1], raiseError=raiseError)

    img2D_sub[img2D_sub == invalid_value] = 0
    if _resize_shape is None:
        scaled = img2D_sub
    else:
        scaled = resize_img(img2D_sub, shape=_resize_shape)
    if clip:
        scaled = np.clip(scaled, a_min=0, a_max=None)  # clipping
    if show_result:
        images = [img2D, img2D_sub, scaled]
        titles = ["Original Bild", "Ausschnitt (200x200)", "Skaliert (80x80)"]
        fig = plt.figure()
        columns = 3
        rows = 1
        for i in range(len(images)):
            fig.add_subplot(rows, columns, i + 1)
            plt.imshow(images[i], vmin=0, vmax=vmax, cmap="gray")
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
    #add information to the samplebundle object, wich will be build and store now
    filename = "samplebundleFilename"       # can also be a path (/path/to/filename) ending can be freely chosen
    additionalInfo= "testing Samples"       # information can be displayed to identify the samplebundles
    #select the start position and shape of your region in the dwd images (.pngs)
    SUBIMG_TUPLE = ((820, 400), (200, 200)) #((y,x),(width,height)

    path = "/[PATH TO IMAGES]/unpacked/"    #Path to the unpacked images (produced by the DWDtoPngScript.py)
    max_num_samples = 1000                  # maximum number of created Samples
    n_data = 5                              # number of timesteps (t) for inputdata of the network (x,y,t)
    n_label = 1                             # number of timesteps (t) for outputdata (predicted timesteps)
    subimg_startpos = SUBIMG_TUPLE[0]       # coordinate to select subimage. (0,0) is top left corner
    subimg_shape = SUBIMG_TUPLE[1]          # size of the subimage
    output_shape = 200                      # shape to resize the cropped image area (can also be tuple)

    #create a dataConverter Object
    dc = Data_converter(path, max_num_samples, n_data, n_label, None, subimg_startpos, subimg_shape,
                            output_shape, pre="scaled_", post=".png", silent=True)
    #print status
    print("there were {} samples collected with your given settings from path {}".format(dc.get_number_samples(), path))
    dc.save_object(filename, additionalInfo)

    print("your File is now stored here: {}".format(filename))