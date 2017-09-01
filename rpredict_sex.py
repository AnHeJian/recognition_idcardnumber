import mxnet as mx
import numpy as np
import struct
from PIL import Image



test  = mx.io.MNISTIter(
    image      = "ubyte_sex_val_image",
    label      = "ubyte_sex_val_label",
    batch_size = 1,
    shuffle    = 0,)

model = mx.model.FeedForward.load('model_sex_mlp', 20)

[probs, data, label] = model.predict(X = test, return_data=True)

print len(probs), len(data), len(label)

error_num = 0
for i in range(len(probs)):
    #if np.argmax(probs[i]) != label[i]:
    #    print 'error'
    #print np.argmax(probs[i]), label[i], probs[i]
    if np.argmax(probs[i])!= int(label[i]):
        error_num = error_num + 1
    print len(probs[i]), np.argmax(probs[i]), label[i]

print    len(probs), error_num, error_num*1.0/ len(probs)


    