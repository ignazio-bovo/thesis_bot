import numpy as np

class Perceptron:
    def __init__(self, N):
        self.weight_ = np.zeros(N)

    def update(self, feat, targ):
         mist = int(feat.dot(self.weight_) * targ >=0 ) 
         self.weight_ += np.sign(targ) * feat * mist

    def predict(self, feat):
        return np.sign(feat.dot(self.weight_))


class SOPerceptron:
    def __init__(self,N, a=.1):
        self.weights = np.zeros(N)
        self.M_inv = 1/a * np.eye(N)
        self.g_sum = np.zeros(N)
        
    def predict(self, feat):
        return np.sign(self.weights.dot(feat))
    
    def update(self, feat, targ):
        mistake = int(targ * np.sign(feat.dot(self.weights)) <= 0)
        increase = np.outer(feat, feat) * mistake
        self.M_inv -= self.M_inv.dot(increase).dot(self.M_inv)/(1+ feat.dot(self.M_inv).dot(feat))
        self.g_sum += targ * feat * mistake
        self.weights = self.M_inv.dot(self.g_sum)

