import os 
import pygame 
import string
import codecs 
import cv2
import numpy as np

def genChar(ch, myfont, mydir):
    font = pygame.font.Font(myfont, 22)
    rtext = font.render(ch, True, (255, 255, 255), (0, 0, 0)) 
    pygame.image.save(rtext, "mmmmm.png") 

    img = cv2.imread('mmmmm.png')
    rows, cols, channels =  img.shape
    #print img.shape

    pts1 = np.float32([[rows/2-4,cols/2-4],[rows/2+4,cols/2+4],[rows/2-4,cols/2+4]])
        
    fn = 0
    for r in range(-1,2):
        for s in range (-1,2):
            for p in range (-1,2):
                for q in range(-1,2):
                    for i in range (-1,2):
                        for j in range (-1,2):
                            a = pts1[0][0] + r
                            b = pts1[0][1] + s
                            c = pts1[1][0] + p
                            d = pts1[1][1] + q
                            e = pts1[2][0] + i
                            f = pts1[2][1] + j
                            pts2 = np.float32([[a,b],[c,d],[e,f]])
                            
                            M_affine = cv2.getAffineTransform(pts1,pts2)
                            img_affine = cv2.warpAffine(img, M_affine, (cols, rows))
                            imggray = cv2.cvtColor(img_affine,cv2.COLOR_BGR2GRAY)
                            cv2.imwrite(mydir+str(fn)+".png", imggray)
                            
                            fn = fn+1
                            
if __name__ == '__main__':
    chinese_dir = 'chinese'
    if not os.path.exists(chinese_dir): 
        os.mkdir(chinese_dir) 
        
    pygame.init() 
    myfont = "Font_STXIHEI.TTF"
    
    num = 0
    
    start,end = (0x4E00, 0x4E03) #所有汉字编码范围  (0x4E00, 0x9FA5)
    for codepoint in range(int(start),int(end)): 
        ch  = unichr(codepoint) 
        mydir = chinese_dir + '/' + str(num) + '/'
        if not os.path.exists(mydir): 
            os.mkdir(mydir) 
        genChar(ch, myfont, mydir)
        num = num + 1