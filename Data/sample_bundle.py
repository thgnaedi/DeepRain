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


def load_Sample_Bundle(path):
    path += ".sb"
    with open(path, 'rb') as input:
        sb = pickle.load(input)
        assert isinstance(sb, sample_bundle.Sample_Bundle)
    return sb


if __name__ == '__main__':
    sb = load_Sample_Bundle("einObjekt")
    print(sb.info())
    for i in range(10):
        sb.all_samples.append(sb.get_item_at(0))
        sb.all_samples[i+1][0][0][0]=i
    print(sb.get_item_at(0)[0].shape)
    d,l = sb.get_batch(batchsize=4)
    print("anz Batches:",len(d))
    print(sb.subimg)
    print(sb.resizeshape)