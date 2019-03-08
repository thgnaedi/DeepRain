import numpy as np
import pickle


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


def load_Sample_Bundle(path):
    path += ".sb"
    with open(path, 'rb') as input:
        sb = pickle.load(input)
        # assert isinstance(sb, Sample_Bundle)
    return sb


if __name__ == '__main__':
    sb = load_Sample_Bundle("einObjekt")
    print(sb.info())
    print(sb.details)
