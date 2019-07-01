import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

def generate_stuff(dim, p=0.01, pad=5, sigma=3, scale=True):
    array = np.zeros(dim)
    array = np.random.choice([0,1],size=dim,p=[1-p, p])
    array = add_padding_border(array, pad_value=0, size=pad)
    array = gaussian_filter(array,sigma=sigma)

    if scale:
        array = array/np.max(array)

    return array

def add_padding_border(array, pad_value=0, size=2):
    pad = np.zeros((array.shape[0],size))
    pad.fill(pad_value)
    array = np.concatenate((array,pad), axis=1) #rechter Rand
    array = np.concatenate((pad,array), axis=1) #linker Rand
    pad = np.zeros((size, array.shape[1]))
    pad.fill(pad_value)
    array = np.concatenate((array,pad), axis = 0) #unterer Rand
    array = np.concatenate((pad,array), axis = 0) #oberer Rand
    return array

#nur rechtsbewegung beachtet!
#noch keine schrittweite/speed einstellbar!
def generate_one_sample(_dim, n_input, schrittweite=2, pad=5, channelsLast=False):
    internPAD = 5
    n = n_input+1
    dim = (_dim[0]-2*pad, _dim[1]-2*pad)
    dim2 = (dim[0]-2*internPAD,dim[1]+n*schrittweite-2*internPAD)
    img = generate_stuff(dim2, p=0.01, pad=internPAD, sigma=3, scale=True)
    samplelist=[]
    for i in range(n):
        tmp = img[0:dim[0],schrittweite*i:schrittweite*i+dim[1]]
        if i == n_input:
            label = tmp
        else:
            tmp = add_padding_border(tmp, pad_value=0, size=pad)
            samplelist.append(tmp)
    input_data = np.array(samplelist)

    if channelsLast:
        input_data = input_data.swapaxes(0,1)
        input_data = input_data.swapaxes(1,2)

    return input_data, label

def plot_6_images(data, label):
    f, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3)
    f.suptitle('Data and Labels')
    ax1.imshow(data[0])
    ax2.imshow(data[1])
    ax3.imshow(data[2])
    ax4.imshow(data[3])
    ax5.imshow(data[4])
    ax6.imshow(label)
    plt.show()
    return

def eval_output(output, label, name="", rescale=False, save_img_name=None, vmax=1):
    if output.shape[0] == 1:
        output = output.reshape(label.shape)
    if rescale:
        output = output / np.max(output)
        name += " SCALED!"
    if len(label.shape) > 2:
        print("habe 3D dingens zum zeigen, nehme letztes Bild!", label.shape)
        output = output[:,:,label.shape[2]-1]
        label = label[:, :, label.shape[2]-1]
    f, (ax1, ax2, ax3) = plt.subplots(1, 3)
    ax1.imshow(output, cmap="gray", vmin=0, vmax=vmax)
    ax1.set_title("prediction")
    ax2.imshow(label, cmap="gray", vmin=0, vmax=vmax)
    ax2.set_title("label")
    ax3.imshow(np.abs(label-output), cmap="gray", vmin=0, vmax=1)
    ax3.set_title("diff")
    f.suptitle(name)

    if save_img_name is None:
        plt.show()
    else:
        plt.savefig(save_img_name+".png")
    plt.close('all')
    return

if __name__ == '__main__':

    if True:
        data, label = generate_one_sample((100,100), 5, schrittweite=10)
        print(data.shape, label.shape)
        #Shape von Data = (n,x,y)
        plot_6_images(data, label)
    else:
        a = generate_stuff(dim=(100,200))
        print(a.shape)
        plt.imshow(a, vmin=0, vmax=1, cmap='gray')
        plt.show()
