import mxnet as mx
import numpy as np
import struct
from PIL import Image


train = mx.io.MNISTIter(
    image      = "ubyte_train_image",
    label      = "ubyte_train_label",
    batch_size = 32,)
val   = mx.io.MNISTIter(
    image      = "ubyte_val_image",
    label      = "ubyte_val_label",
    batch_size = 32,)

test  = mx.io.MNISTIter(
    image      = "ubyte_val_image",
    label      = "ubyte_val_label",
    batch_size = 1,
    shuffle    = 0,)

data = mx.symbol.Variable('data')
fc1  = mx.symbol.FullyConnected(data = data, num_hidden=1024)
act1 = mx.symbol.Activation(data = fc1, act_type="relu")
fc2  = mx.symbol.FullyConnected(data = act1, num_hidden = 512)
act2 = mx.symbol.Activation(data = fc2, act_type="relu")
fc3  = mx.symbol.FullyConnected(data = act2, num_hidden=11)
mlp  = mx.symbol.SoftmaxOutput(data = fc3, name = 'softmax')

model = mx.model.FeedForward(
    symbol = mlp,
    num_epoch = 20,
    learning_rate = .1)
model.fit(X = train, eval_data = val)

model.save("model_card")
'''
[probs, data, label] = model.predict(X = test, return_data=True)

print len(probs), len(data), len(label)

for i in range(len(probs)):
    #if np.argmax(probs[i]) != label[i]:
    #    print 'error'
    print np.argmax(probs[i]), label[i]
'''

    