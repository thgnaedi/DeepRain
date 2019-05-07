import numpy as np
import pickle
import sample_bundle


class Sample_Bundle():
    def __init__(self, subimg, resizeshape, all_samples, details=""):
        self.subimg = subimg
        self.resizeshape = resizeshape
        self.all_samples = all_samples
        self.details = details
        self.id = 0
        self.cleared = -1   # clear threshold

    def info(self):
        return "Set Bundle with " + str(len(self.all_samples)) + " Samples " + self.details

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

    ## axis = position batchsize in shape, default: (x, y, n_data, batchsize)
    def get_batch(self, batchsize, random=True, axis=3):
        if random:
            indexlist = np.random.permutation(len(self.all_samples))
        else:
            indexlist = np.arange(len(self.all_samples))

        all_b_data = []
        all_b_label = []
        b_data = None
        b_label = None
        for i in range(len(self.all_samples)):
            a = self.all_samples[indexlist[i]]
            if i%batchsize == 0:
                if b_data is not None:
                    all_b_data.append(np.stack(b_data, axis=axis))
                    all_b_label.append(np.stack(b_label, axis=axis))
                b_data = []
                b_label = []
            b_data.append(a[0])
            b_label.append(a[1])
        if len(b_data) > 0:
            all_b_data.append(np.stack(b_data, axis=axis))
            all_b_label.append(np.stack(b_label, axis=axis))
        return all_b_data, all_b_label

    def get_all_data_label(self, channels_Last):
        data = []
        label = []
        for item in self.all_samples:
            data.append(item[0])
            label.append(item[1])
        if channels_Last:
            return np.array(data), np.array(label)
        return np.swapaxes(np.array(data),1,3), np.swapaxes(np.array(label),1,3)

    def clear_samples(self, threshold=1):
        if not hasattr(self, 'cleared'):   #supports older versions of Objects
            print("You are using an outdatet Version of sample_bundle! this may cause to errors!")
            self.cleared = -1
            print((locals()))
        print("cleared is da")
        if threshold <= self.cleared:
            print("cleared already done with threshold {}".format(self.cleared))
            return
        index = 0
        while(True):
            a = self.all_samples[index]
            if np.max(a[0]) < threshold:
                del self.all_samples[index]
            else:
                index += 1
            if index >= len(self.all_samples):
                break
        self.cleared = threshold
        return

    def save_object(self, filename):
        filename += ".sb"
        with open(filename, 'wb') as output:  # Overwrites any existing file.
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)
        print(filename + " saved successfully")
        return


def load_Sample_Bundle(path):
    path += ".sb"
    with open(path, 'rb') as input:
        sb = pickle.load(input)
        assert isinstance(sb, sample_bundle.Sample_Bundle)
    return sb


if __name__ == '__main__':
    sb = load_Sample_Bundle("einObjekt")
    print(sb.info())
    #duplicate first Sample 10 times, so 11 images are avaliable
    for i in range(10):
        sb.all_samples.append(sb.get_item_at(0))
        sb.all_samples[i+1][0][0][0]=i
    print("one sample has shape:",sb.get_item_at(0)[0].shape)
    d,l = sb.get_batch(batchsize=4)
    print("anz Batches:",len(d),"mit shape:",d[0].shape,"und label-shape:",l[0].shape)
    print(sb.subimg)
    print(sb.resizeshape)
    data, label = sb.get_all_data_label(channels_Last=True)
    print("data:",data.shape, "label",label.shape)