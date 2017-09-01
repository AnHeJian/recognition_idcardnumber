import os 
import pygame 
import string
import codecs 
import cv2
import numpy as np
import random

def genChar(ch, myfont, fname):
    font = pygame.font.Font(myfont, 28)
    rtext = font.render(ch, True, (255, 255, 255), (0, 0, 0)) 
    pygame.image.save(rtext, fname) 
    
def CropImage(img, srow, scol, erow, ecol):
    img_temp = np.zeros((erow-srow+1, ecol-scol+1), np.uint8)  
    for x in range(srow, erow+1):
        for y in range(scol, ecol+1):
            img_temp[x-srow,y-scol] = img[x, y]
    return img_temp
    
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
    
def RotateImageShiftToBackground(imgorg, bgRows, bgCols, mydir):
    global fn
    for myangle in range(-2,3,2):
        M_rotate = cv2.getRotationMatrix2D((imgorg.shape[1]/2, imgorg.shape[0]/2), myangle, 1)
        img_rotate = cv2.warpAffine(imgorg, M_rotate, (imgorg.shape[1], imgorg.shape[0]))          
        
        for exp_ratio in np.arange(1, 0.6, -0.15):
            img = cv2.resize(img_rotate, (int(exp_ratio*img_rotate.shape[1]), int(exp_ratio*img_rotate.shape[0])), interpolation=cv2.INTER_CUBIC)
            for offsetx in range((bgRows-img.shape[0])+1):
                for offsety in range((bgCols-img.shape[1])+1):
                    save_img = np.zeros((bgRows,bgCols),np.uint8)
                    #print img.shape, offsetx, offsety, save_img[offsetx, offsety]
                    for x in range(img.shape[0]):
                        for y in range(img.shape[1]):
                            if offsetx+x < save_img.shape[0] and offsety+y<save_img.shape[1]:
                                save_img[offsetx+x, offsety+y] = img[x,y]
                    cv2.imwrite(mydir+os.sep+str(fn)+".png", save_img)
                    fn = fn+1      
        '''
        #只放在中间位置
        save_img = np.zeros((bgRows,bgCols),np.uint8)
        offsetx = (bgRows-img.shape[0])/2 
        offsety = (bgCols-img.shape[1])/2 
        for x in range(img.shape[0]):
            for y in range(img.shape[1]):
                if offsetx+x < save_img.shape[0] and offsety+y<save_img.shape[1]:
                    save_img[offsetx+x, offsety+y] = img[x,y]
        cv2.imwrite(mydir+os.sep+str(fn)+".png", save_img)
        fn = fn+1     
        '''   
def RotateImageToBackground(imgorg, bgRows, bgCols, mydir):
    global fn
    for myangle in range(-5,6, 1):
        M_rotate = cv2.getRotationMatrix2D((imgorg.shape[1]/2, imgorg.shape[0]/2), myangle, 1)
        img = cv2.warpAffine(imgorg, M_rotate, (imgorg.shape[1], imgorg.shape[0]))  
        for exp_ratio in np.arange(1, 0.65, -0.05):
            tem_img = cv2.resize(img, (int(exp_ratio*img.shape[1]), int(exp_ratio*img.shape[0])), interpolation=cv2.INTER_CUBIC)  
            save_img = np.zeros((bgRows,bgCols),np.uint8)
            offsetx = (bgRows-tem_img.shape[0])/2
            offsety = (bgCols-tem_img.shape[1])/2
            for x in range(tem_img.shape[0]):
                for y in range(tem_img.shape[1]):
                    if offsetx+x < save_img.shape[0] and offsety+y<save_img.shape[1]:
                        save_img[offsetx+x, offsety+y] = tem_img[x,y]
            step = 3            
            for randratio in range(0, 7):         
                myimg = save_img.copy()
                for x in range(step, save_img.shape[0]-step):
                    for y in range(step, save_img.shape[1]-step):
                        mycount = 0
                        for i in range(-step, step+1, 1):
                            for j in range(-step, step+1, 1):
                                if save_img[x+i,y+j] > 0:
                                    mycount = mycount + 1 
                        if 1.0*mycount/((2*step+1)*(2*step+1))>0.3:
                            trand = random.randint(0, 140)
                            rratio = random.randint(0,9)
                            if rratio < randratio and trand > myimg[x,y]:                                    
                                myimg[x,y] = trand
                cv2.imwrite(mydir+os.sep+str(fn)+".png", myimg)
                fn = fn+1 
        
def trans(img, mydir):
    global fn 
    bgRows = 28
    bgCols = 28
    rows, cols =  img.shape
    
    if not os.path.exists(mydir): 
        os.mkdir(mydir) 

    '''仿射变换
    pts1 = np.float32([[rows/2-3,cols/2-3],[rows/2+3,cols/2+3],[rows/2-3,cols/2+3]])
    
    step = 1
    for r in range(-step,step+1):
        for s in range (-step,step+1):
            for p in range (-step,step+1):
                for q in range(-step,step+1):
                    for i in range (-step,step+1):
                        for j in range (-step,step+1):
                            a = pts1[0][0] + r
                            b = pts1[0][1] + s
                            c = pts1[1][0] + p
                            d = pts1[1][1] + q
                            e = pts1[2][0] + i
                            f = pts1[2][1] + j
                            pts2 = np.float32([[a,b],[c,d],[e,f]])
                            
                            M_affine = cv2.getAffineTransform(pts1,pts2)
                            img_affine = cv2.warpAffine(img, M_affine, (cols, rows))
                            RotateImageToBackground(img_affine, bgRows, bgCols, mydir)
    
    '''
    
    RotateImageToBackground(img, 28, 28, mydir)
    
    #透视变换    
    step = 3   
    pts1 = np.float32([[0,0],[rows-1,0],[0,cols-1],[rows-1,cols-1]])
    
    # top
    for i in range(0, step):
        for j in range(0,step):
            if i!=0 or j!=0:
                a = pts1[0][0] + i
                b = pts1[0][1]
                c = pts1[1][0] - j
                d = pts1[1][1]
                e = pts1[2][0]
                f = pts1[2][1]
                g = pts1[3][0]
                h = pts1[3][1] 
                pts2 = np.float32([[a,b],[c,d],[e,f],[g,h]])
                M = cv2.getPerspectiveTransform(pts1,pts2)
                dstimg = cv2.warpPerspective(img,M,(cols, rows))
                #cv2.imwrite(mydir+os.sep+str(fn)+".png", dstimg)
                #fn = fn+1
                RotateImageToBackground(dstimg, bgRows, bgCols, mydir)
    # bottom
    for i in range(0, step):
        for j in range(0,step):
            if i!=0 or j!=0:
                a = pts1[0][0]
                b = pts1[0][1]
                c = pts1[1][0]
                d = pts1[1][1]
                e = pts1[2][0] + i
                f = pts1[2][1]
                g = pts1[3][0] - j
                h = pts1[3][1] 
                pts2 = np.float32([[a,b],[c,d],[e,f],[g,h]])
                M = cv2.getPerspectiveTransform(pts1,pts2)
                dstimg = cv2.warpPerspective(img,M,(cols, rows))
                #cv2.imwrite(mydir+os.sep+str(fn)+".png", dstimg)
                #fn = fn+1
                RotateImageToBackground(dstimg, bgRows, bgCols, mydir)
    # left 
    for i in range(0, step):
        for j in range(0, step):
            if i!=0 or j!=0:
                a = pts1[0][0]
                b = pts1[0][1] + i
                c = pts1[1][0]
                d = pts1[1][1]
                e = pts1[2][0]
                f = pts1[2][1] - j 
                g = pts1[3][0]
                h = pts1[3][1]
                pts2 = np.float32([[a,b],[c,d],[e,f],[g,h]])
                M = cv2.getPerspectiveTransform(pts1,pts2)
                dstimg = cv2.warpPerspective(img,M,(cols, rows))
                #cv2.imwrite(mydir+os.sep+str(fn)+".png", dstimg)
                #fn = fn+1
                RotateImageToBackground(dstimg, bgRows, bgCols, mydir)
            
    # right
    for i in range(0, step):
        for j in range(0,step):
            if i!=0 or j!=0:
                a = pts1[0][0]
                b = pts1[0][1]
                c = pts1[1][0]
                d = pts1[1][1] + i
                e = pts1[2][0]
                f = pts1[2][1]
                g = pts1[3][0]
                h = pts1[3][1] - j 
                pts2 = np.float32([[a,b],[c,d],[e,f],[g,h]])
                M = cv2.getPerspectiveTransform(pts1,pts2)
                dstimg = cv2.warpPerspective(img,M,(cols, rows))
                #cv2.imwrite(mydir+os.sep+str(fn)+".png", dstimg)
                #fn = fn+1
                RotateImageToBackground(dstimg, bgRows, bgCols, mydir)   
                
    
        

if __name__ == '__main__':
    print int('0000123')
    fn = 0
    
    orgdir = 'd:\\\\dir_chinese_org'
    
    pygame.init()
    myfont = 'Font_STXIHEI.TTF'
    
    f = open('transChineseTable.txt', "r")
    chlist = f.readlines()
    
    if not os.path.exists(orgdir):
        os.mkdir(orgdir) 
        
    num = 0
    for ch in chlist:
        chgbk=ch.strip('\n')
        print chgbk
        chunichr = chgbk.decode('gbk')
        print repr(chunichr)
        savefilename = orgdir+'/'+IntToStr(num, 5)+'.png'
        genChar(chunichr, myfont, savefilename)
        img = cv2.imread(savefilename, 0)
        img = CropImage(img, 8, 0, img.shape[0]-4, img.shape[1]-2)
        cv2.imwrite(savefilename, img)
        num = num+1

    transdir = 'd:\\\\dir_chinese_trans'
    if not os.path.exists(transdir): 
        os.mkdir(transdir) 
    
    for parent,dirnames,filenames in os.walk(orgdir):
        for filename in filenames:
            print 'process ' + os.path.join(parent,filename)
            img = cv2.imread(os.path.join(parent,filename), 0)
            img = CropImage(img, 0, 0, img.shape[0]-4, img.shape[1]-1)
            temroot = transdir + os.sep + filename.split('.')[0]
            fn = 0
            trans(img, temroot)
