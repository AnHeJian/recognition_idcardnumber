import mxnet as mx
import numpy as np
import struct
from PIL import Image

def get_mlp():                                     #这里定义mlp网络
    """
    multi-layer perceptron
    """
    data = mx.symbol.Variable('data')
    fc1  = mx.symbol.FullyConnected(data = data, num_hidden=128)
    act1 = mx.symbol.Activation(data = fc1, act_type="relu")
    fc2  = mx.symbol.FullyConnected(data = act1, num_hidden = 64)
    act2 = mx.symbol.Activation(data = fc2, act_type="relu")
    fc3  = mx.symbol.FullyConnected(data = act2, num_hidden=11)
    mlp  = mx.symbol.SoftmaxOutput(data = fc3, name = 'softmax')
    return mlp

def get_lenet(add_stn=False):
    """
    LeCun, Yann, Leon Bottou, Yoshua Bengio, and Patrick
    Haffner. "Gradient-based learning applied to document recognition."
    Proceedings of the IEEE (1998)
    """
    data = mx.symbol.Variable('data')
    if(add_stn):
        data = mx.sym.SpatialTransformer(data=data, loc=get_loc(data), target_shape = (28,28),
                                         transform_type="affine", sampler_type="bilinear")
    # first conv
    conv1 = mx.symbol.Convolution(data=data, kernel=(5,5), num_filter=20)
    tanh1 = mx.symbol.Activation(data=conv1, act_type="tanh")
    pool1 = mx.symbol.Pooling(data=tanh1, pool_type="max",
                              kernel=(2,2), stride=(2,2))
    # second conv
    conv2 = mx.symbol.Convolution(data=pool1, kernel=(5,5), num_filter=50)
    tanh2 = mx.symbol.Activation(data=conv2, act_type="tanh")
    pool2 = mx.symbol.Pooling(data=tanh2, pool_type="max",
                              kernel=(2,2), stride=(2,2))
    # first fullc
    flatten = mx.symbol.Flatten(data=pool2)
    fc1 = mx.symbol.FullyConnected(data=flatten, num_hidden=500)
    tanh3 = mx.symbol.Activation(data=fc1, act_type="tanh")
    # second fullc
    fc2 = mx.symbol.FullyConnected(data=tanh3, num_hidden=11)
    # loss
    lenet = mx.symbol.SoftmaxOutput(data=fc2, name='softmax')
    return lenet


#定义训练集迭代器
train = mx.io.MNISTIter(
    image      = "ubyte_integer_train_image",
    label      = "ubyte_integer_train_label",
    batch_size = 128,)                                  #“批尺寸”，实际上表示的是一次处理样本的个数

	
#定义测试集迭代器 
val   = mx.io.MNISTIter(
    image      = "ubyte_integer_val_image",
    label      = "ubyte_integer_val_label",
    batch_size = 128,)

test  = mx.io.MNISTIter(
    image      = "ubyte_integer_val_image",
    label      = "ubyte_integer_val_label",
    batch_size = 1,
    shuffle    = 0,)

#训练网络
model = mx.model.FeedForward(
    symbol = get_lenet(),                          #即前面定义的网络
    num_epoch = 20,                              #训练的次数
    learning_rate = .1)	                         #学习常数
model.fit(X = train, eval_data = val)            #拟合数据结果

model.save("model_integer_lenet")

[probs, data, label] = model.predict(X = test, return_data=True)

print len(probs), len(data), len(label)

enum = 0
for i in range(len(probs)):
    if np.argmax(probs[i]) != label[i]:
        enum = enum + 1
    #print np.argmax(probs[i]), label[i]
print enum, len(probs), enum*1.0/len(probs)    
