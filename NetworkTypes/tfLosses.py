from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import six
from keras import  backend as K
from keras.utils.generic_utils import deserialize_keras_object
from keras.utils.generic_utils import serialize_keras_object


def mean_squared_error_kopie(y_true, y_pred):
    #ToDo: implement loss function here:
    return K.mean(K.square(y_pred - y_true), axis=-1)
