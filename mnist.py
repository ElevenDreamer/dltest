#!/usr/bin/env python

import struct
from datetime import datetime
from bp import Network
import numpy as np

###
#def transpose(args):
#    return map(
#            lambda arg: map(
#                lambda line: np.array(line).reshape(len(line), 1)
#                , arg)
#            , args
#    )
class Loader(object):
    def __init__(self, path, count):
        self.path = path
        self.count = count
    def get_file_content(self):
        f = open(self.path, 'rb')
        content = f.read()
        f.close()
        return content
    def to_int(self, byte):
        return struct.unpack('B', byte)[0]

class ImageLoader(Loader):
    def get_picture(self, content, index):
        start = index * 28 * 28 + 16
        picture = []
        for i  in range(28):
            picture.append([])
            for j in range(28):
                picture[i].append(self.to_int(content[start + i * 28 + j]))
        return picture
    def get_one_sample(self, picture):
        sample = []
        for i in range(28):
            for j in range(28):
                sample.append(picture[i][j])
        return sample

    def load(self):
        content = self.get_file_content()
        data_set = []
        for index in range(self.count):
            data_set.append(
                    self.get_one_sample(
                        self.get_picture(content, index)))
        return data_set
class LableLoader(Loader):
    def load(self):
        content = self.get_file_content()
        labels = []
        for index in range(self.count):
            labels.append(self.norm(content[index + 8]))
        return labels
    def norm(self, label):
        label_vec = []
        label_value = self.to_int(label)
        for i in range(10):
            if i == label_value:
                label_vec.append(0.9)
            else:
                label_vec.append(0.1)
        return label_vec
def get_training_data_set():
    image_loader = ImageLoader('train-images.idx3-ubyte', 60000)
    label_loader = LableLoader('train-labels.idx1-ubyte', 60000)
    return image_loader.load(), label_loader.load()
def get_test_data_set():
    image_loader = ImageLoader('t10k-images.idx3-ubyte', 10000)
    label_loader = LableLoader('t10k-labels.idx1-ubyte', 10000)
    return image_loader.load(), label_loader.load()

def get_result(vec):
    max_value_index = 0
    max_value = 0
    for i in range(len(vec)):
        if vec[i] > max_value:
            max_value = vec[i]
            max_value_index = i
    return max_value_index
def now():
    return datetime.now().strftime('%c')
def evaluate(network, test_data_set, test_labels):
    error = 0
    total = len(test_data_set)

    for i in range(total):
        label = get_result(test_labels[i])
        predict = get_result(network.predic(test_data_set[i]))
        if label != predict:
            error += 1
    return float(error) / float(total)

def train_and_evaluate():
    last_error_ratio = 1.0
    epoch = 0
    train_data_set, train_labels = get_training_data_set()
    print 'train_data_size =%d '  % len(train_data_set)
    test_data_set, test_labels = get_test_data_set()
    network = Network([784, 100, 10])
    while True:
        epoch += 1
        network.train(train_labels, train_data_set, 0.3, 1)
        print '%s epoch %d finished ' % (now(), epoch)
        if epoch % 10 == 0:
            error_ratio = evaluate(network, test_data_set, test_labels) 
            print '%s after epoch %d, error ratio is %f' % (now(), epoch, error_ratio)
            if error_ratio > last_error_ratio:
                break
            else:
                last_error_ratio = error_ratio

if __name__ == '__main__':
    train_and_evaluate()
