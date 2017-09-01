from PIL import Image
import struct
import os
import os.path
import random

def image2byte(rootdir , trainratio ):
    cols = 13
    rows = 21
    train_img_buf = ''
    train_lab_buf = ''
    val_img_buf = ''
    val_lab_buf = ''
    train_img_num = 0
    val_img_num = 0
    for parent,dirnames,filenames in os.walk(rootdir):    #os.walk：遍历目录 
														  #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        #for dirname in  dirnames:                       #输出文件夹信息
        #    print "parent is:" + parent
        #    print  "dirname is:" + dirname
        for filename in filenames:                        #输出文件信息
            print 'process ' + os.path.join(parent,filename) #输出文件路径信息
            temprandom = random.random()                         #生成0和1之间的随机浮点数float
            if  temprandom < trainratio:
                train_img_num = train_img_num + 1
                img = Image.open(os.path.join(parent,filename))
                cols, rows= img.size
                
                #process train image
                for x in xrange(rows):
                    for y in xrange(cols):
                        #print img.getpixel((y,x))
                        train_img_buf = train_img_buf + struct.pack('>B',img.getpixel((y,x)))
                        
                #process train label
                train_lab_buf = train_lab_buf + struct.pack('>B',int(parent.split(os.sep)[-1]))   #os.sep:路径分隔符（windows下：\）
            else: 
                val_img_num = val_img_num + 1
                img = Image.open(os.path.join(parent,filename))
                cols, rows= img.size
                
                #process val image
                for x in xrange(rows):
                    for y in xrange(cols):
                        #print img.getpixel((y,x))
                        val_img_buf = val_img_buf + struct.pack('>B',img.getpixel((y,x)))
                        
                #process val label
                val_lab_buf = val_lab_buf + struct.pack('>B',int(parent.split(os.sep)[-1]))
                
            
    print train_img_num, val_img_num
    train_img_buf = struct.pack('>IIII',1, train_img_num, rows, cols) + train_img_buf
    save = open('ubyte_train_image', 'wb')
    print 'ubyte_train_image'
    save.write(train_img_buf)
    save.close()

    train_lab_buf = struct.pack('>II',1, train_img_num) + train_lab_buf
    save = open('ubyte_train_label', 'wb')
    save.write(train_lab_buf)
    save.close()
    
    val_img_buf = struct.pack('>IIII',1, val_img_num, rows, cols) + val_img_buf
    save = open('ubyte_val_image', 'wb')
    save.write(val_img_buf)
    save.close()

    val_lab_buf = struct.pack('>II',1, val_img_num) + val_lab_buf
    save = open('ubyte_val_label', 'wb')
    save.write(val_lab_buf)
    save.close()

if __name__ == '__main__':
    image2byte('D:\\\\dir_integer_trans', 0.8)

'''
img = Image.open("zzz.png")
cols, rows= img.size

buf = struct.pack('>IIII',1, 1, rows, cols)
for x in xrange(rows):
    for y in xrange(cols):
        #print img.getpixel((y,x))
        buf = buf + struct.pack('>B',img.getpixel((y,x)))
                
save = open('ddd', 'wb')
save.write(buf)
save.close()
'''