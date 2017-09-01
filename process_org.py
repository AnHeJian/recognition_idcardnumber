import mxnet as mx
import numpy as np
import os
import struct
from PIL import Image

def read_image(filename):
    f = open(filename, 'rb')
    index = 0
    buf = f.read()
    f.close()
    magic, images, rows, columns = struct.unpack_from('>IIII' , buf , index)
    print magic, images, rows, columns
    index += struct.calcsize('>IIII')
    
    savedir = 'test_zzz'
    if not os.path.exists(savedir): 
        os.mkdir(savedir) 
    
    for i in xrange(images):
    #for i in xrange(2000):
        image = Image.new('L', (columns, rows))
        for x in xrange(rows):
            for y in xrange(columns):
                image.putpixel((y, x), int(struct.unpack_from('>B', buf, index)[0]))
                index += struct.calcsize('>B')
        print 'save ' + str(i) + 'image'
        image.save(savedir + os.sep + str(i) + '.jpg')
        
def read_label(filename, saveFilename):
    f = open(filename, 'rb')
    index = 0
    buf = f.read()
    f.close()
    
    magic, labels = struct.unpack_from('>II' , buf , index)
    index += struct.calcsize('>II')
    labelArr = [0] * labels
    #labelArr = [0] * 2000
    for x in xrange(labels):
    #for x in xrange(2000):
        labelArr[x] = int(struct.unpack_from('>B', buf, index)[0])
        index += struct.calcsize('>B')
        
    save = open(saveFilename, 'w')
    save.write('\n'.join(map(lambda x: str(x), labelArr)))
    save.write('\n')
    save.close()
    print 'save labels success'

def pick_image(filename, savefile, picknum=9990):
    f = open(filename, 'rb')
    index = 0
    buf = f.read()
    f.close()
    magic, images, rows, columns = struct.unpack_from('>IIII' , buf , index)
    index += struct.calcsize('>IIII')
    
    save = open(savefile, 'wb')
    save.write(buf[0:4])
    save.write(struct.pack('>I',picknum))
    save.write(buf[8:4*4])
    save.write(buf[4*4+0*28*28: 4*4+picknum*28*28])
    save.close()
    
    
def pick_label(filename, savefile, picknum=9990):
    f = open(filename, 'rb')
    index = 0
    buf = f.read()
    f.close()    
    magic, labels = struct.unpack_from('>II' , buf , index)
    index += struct.calcsize('>II')
    
    save = open(savefile, 'wb')
    save.write(buf[0:4])
    save.write(struct.pack('>I',picknum))
    save.write(buf[8+0: 8+picknum])
    save.close()

def addbackground_image(filename):
    f = open(filename, 'rb')
    index = 0
    buf = f.read()
    f.close()
    magic, images, rows, columns = struct.unpack_from('>IIII' , buf , index)
    index += struct.calcsize('>IIII')
    
    save = open('myimage2', 'wb')
    save.write(buf[0:4])
    save.write(struct.pack('>I',10))
    rowincr =5
    save.write(struct.pack('>II',rows+2*rowincr,28))
    tbuf = ''
    for i in xrange(images):
        for j in xrange(rowincr):
            tbuf = ''.join([tbuf,struct.pack('>IIIIIII',0,0,0,0,0,0,0)])
        tbuf = ''.join([tbuf, buf[16+i*784: 16+(i+1)*784]])
        for j in xrange(rowincr):
            tbuf = ''.join([tbuf,struct.pack('>IIIIIII',0,0,0,0,0,0,0)])
    save.write(tbuf)
    save.close()

def resize_image(filename):
    f = open(filename, 'rb')
    index = 0
    buf = f.read()
    f.close()
    magic, images, rows, columns = struct.unpack_from('>IIII' , buf , index)
    index += struct.calcsize('>IIII')
    
    save = open('myimage3', 'wb')
    save.write(buf[0:4])
    save.write(struct.pack('>I',10))
    save.write(struct.pack('>II',28,28))
    
    tbuf = ''
    for i in xrange(images):
        image = Image.new('L', (columns, rows))
        for x in xrange(rows):
            for y in xrange(columns):
                image.putpixel((y, x), int(struct.unpack_from('>B', buf, index)[0]))
                index += struct.calcsize('>B')
        image = image.resize((28,28))
        #image = image.rotate(45)
        print 'save ' + str(i) + 'image'
        image.save('test1/' + str(i) + '.jpg')
        
        for x in xrange(28):
            for y in xrange(28):
                tbuf = ''.join([tbuf,struct.pack('>B', image.getpixel((y,x)))])
    
    save.write(tbuf)
    save.close()
    

if __name__ == '__main__':
    read_image('ddd')
    #read_label('t10k-labels-idx1-ubyte', 'label.txt')
    #pick_image('t10k-images-idx3-ubyte', 'myimage')
    #pick_label('t10k-labels-idx1-ubyte', 'temp-label-ubyte')
    #addbackground_image('myimage')
    #read_image('myimage2')
    #resize_image('myimage2')

    