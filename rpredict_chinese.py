import mxnet as mx
import numpy as np
import struct
from PIL import Image



test  = mx.io.MNISTIter(
    image      = "D:\\ubyte_chinese_train_image",
    label      = "D:\\ubyte_chinese_train_label",
    batch_size = 1,
    shuffle    = 0,)

model = mx.model.FeedForward.load('model_chinese_mlp', 20)

[probs, data, label] = model.predict(X = test, return_data=True)

print len(probs), len(data), len(label)

error_num = 0
for i in range(len(probs)):
    #if np.argmax(probs[i]) != label[i]:
    #    print 'error'
    #print np.argmax(probs[i]), label[i], probs[i]
    
    print 'label:', int(label[i]), '\tmax:', np.argmax(probs[i]), 
    if np.argmax(probs[i])!= int(label[i]):
        error_num = error_num + 1
        print ' \terror',
    print    

print    len(probs), error_num, error_num*1.0/ len(probs)

def IntToStr(fn, slen):
    temLen = len(str(fn))
    if temLen >= slen:
        return str(fn)
    else:
        res = ''
        for i in range(slen-temLen):    
            res = res + '0'
        res = res + str(fn)
        return res
        
print IntToStr(12345, 6)    