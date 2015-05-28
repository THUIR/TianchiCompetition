__author__ = 'wangchao'


import neurolab as nl
import numpy as np

from wc_common import *

class WCMLModel():
    def fit(self, train_x, train_y):
        pass

    def predict(self, feature_list):
        pass

class WCMultilayerPerceptron(WCMLModel):
    def __init__(self, layer_num=3, feature_min_value=0, feature_max_value = 10, output_max_value = 10.0):
        self.net = None
        self.layer_num = layer_num
        self.feature_max_value = feature_max_value
        self.feature_min_value = feature_min_value
        self.output_max_value = output_max_value

    def fit(self, train_x, train_y):
        if len(train_x) == 0:
            return
        #print "TRAIN X: "
        #for x in train_x:
        #    print arr_string(x)
        #print "TRAIN Y: "
        #for y in train_y:
        #    print str(y)
        target = []
        for y in train_y:
            target.append([y / self.output_max_value])
        feature_dimension = len(train_x[0])
        feature_min_max_list = []
        for i in range(0, feature_dimension):
            feature_min_max_list.append([self.feature_min_value, self.feature_max_value])
        self.net = nl.net.newff(feature_min_max_list, [feature_dimension / 4, feature_dimension / 8, 1])
        error = self.net.train(train_x, target, epochs=1000, show=200, goal=0.0001)
        #print "WCMultilayerPerceptron error: " + str(error)

    def predict(self, feature_list):
        in_list = []
        in_list.append(feature_list)
        out_list = self.net.sim(in_list)
        return out_list[0][0] * self.output_max_value