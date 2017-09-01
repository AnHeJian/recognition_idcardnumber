import os 
import pygame 
import string
import codecs 
import cv2
import numpy as np

def genChar(ch, myfont, fname):       #encode,font,path
    font = pygame.font.Font(myfont, 36)
    rtext = font.render(ch, True, (255, 255, 255), (0, 0, 0)) #着色
    pygame.image.save(rtext, fname) 
    
def CropImage(img, srow, scol, erow, ecol):
    img_temp = np.zeros((erow-srow+1, ecol-scol+1), np.uint8)  #创建矩阵并初始化为0，int型
    for x in range(srow, erow+1):
        for y in range(scol, ecol+1):
            img_temp[x-srow,y-scol] = img[x, y]
    return img_temp

def RotateImageShiftToBackground(imgorg, bgRows, bgCols, mydir):
    global fn                                                           #全局变量
    for myangle in range(-7,8, 7):
        M_rotate = cv2.getRotationMatrix2D((imgorg.shape[1]/2, imgorg.shape[0]/2), myangle, 1)
        img = cv2.warpAffine(imgorg, M_rotate, (imgorg.shape[1], imgorg.shape[0]))  
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
                    if fn==100:
                        cv2.imshow('org', img)
                        cv2.imshow('trans', save_img)
                        cv2.waitKey(0)
                        '''
def RotateImageToBackground(imgorg, bgRows, bgCols, mydir):
    global fn
    for myangle in range(-7,8, 1):
        M_rotate = cv2.getRotationMatrix2D((imgorg.shape[1]/2, imgorg.shape[0]/2), myangle, 1)
        img = cv2.warpAffine(imgorg, M_rotate, (imgorg.shape[1], imgorg.shape[0]))  
        offsetx = (bgRows-img.shape[0])/2
        offsety = (bgCols-img.shape[1])/2
        save_img = np.zeros((bgRows,bgCols),np.uint8)
        #print img.shape, offsetx, offsety, save_img[offsetx, offsety]
        for x in range(img.shape[0]):
            for y in range(img.shape[1]):
                if offsetx+x < save_img.shape[0] and offsety+y<save_img.shape[1]:
                    save_img[offsetx+x, offsety+y] = img[x,y]
        cv2.imwrite(mydir+os.sep+str(fn)+".png", save_img)
        fn = fn+1 
        '''
        if fn==100:
            cv2.imshow('org', img)
            cv2.imshow('trans', save_img)
            cv2.waitKey(0)
            '''    
            
def trans(img, mydir):
    global fn 
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
                            RotateImageToBackground(img_affine, 28, 28, mydir)
    '''
    
    #透视变换
    step = 6    
    pts1 = np.float32([[0,0],[rows-1,0],[0,cols-1],[rows-1,cols-1]])
    for i in range(0, step):
        for j in range(0,step):
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
                RotateImageToBackground(dstimg, 28, 28, mydir)
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
                RotateImageToBackground(dstimg, 28, 28, mydir)
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
                RotateImageToBackground(dstimg, 28, 28, mydir)
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
                RotateImageToBackground(dstimg, 28, 28, mydir)

    for exp_ratio in np.arange(1, 0.5, -0.05):
        tem_img = cv2.resize(img, (int(exp_ratio*img.shape[1]), int(exp_ratio*img.shape[0])), interpolation=cv2.INTER_CUBIC)
        RotateImageToBackground(tem_img, 28, 28, mydir)


if __name__ == '__main__':
    fn = 0
    
    orgdir = 'd:\\\\dir_integer_org'
    
    pygame.init()
    myfont = 'Font_OCRB_10_BT.TTF'
    
    f = open('transIntegerTable.txt', "r")
    chlist = f.readlines()
    
    if not os.path.exists(orgdir):
        os.mkdir(orgdir) 
        
    num = 0
    for ch in chlist:
        chgbk=ch.strip('\n')
        print chgbk
        chunichr = chgbk.decode('gbk')
        print repr(chunichr)
        savefilename = orgdir+'/'+str(num)+'.png'
        genChar(chunichr, myfont, savefilename)
        img = cv2.imread(savefilename, 0)
        img = CropImage(img, 2, 1, img.shape[0]-9, img.shape[1]-2)
        cv2.imwrite(savefilename, img)
        num = num+1
	
    transdir = 'd:\\\\dir_integer_trans'
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
            