
import os 
import pygame 
import string
import codecs 
import cv2
import numpy as np

'''
start,end = (0x4E00, 0x9FA5) 
with codecs.open("chinese.txt", "wb", encoding="utf-8") as f: 
    for codepoint in range(int(start),int(end)): 
        f.write(unichr(codepoint)) 
'''

chinese_dir = 'integer_org'
if not os.path.exists(chinese_dir): 
    os.mkdir(chinese_dir) 
  
pygame.init() 

myfont = "Font_OCRB_10_BT.ttf"

if not pygame.font: print('Warning, fonts disabled')

for codepoint in xrange(10): 
    word = str(codepoint)
    font = pygame.font.Font(myfont, 22)
    rtext = font.render(word, True, (255, 255, 255), (0, 0, 0)) 
    pygame.image.save(rtext, os.path.join(chinese_dir,word+".png")) 
 
for word in string.lowercase:
    font = pygame.font.Font(myfont, 22)
    rtext = font.render(word, True, (255, 255, 255), (0, 0, 0)) 
    pygame.image.save(rtext, os.path.join(chinese_dir,word+".png")) 
    
for word in string.uppercase:
    font = pygame.font.Font(myfont, 22)
    rtext = font.render(word, True, (255, 255, 255), (0, 0, 0)) 
    pygame.image.save(rtext, os.path.join(chinese_dir, 'u_'+word+".png")) 
'''

pygame.init() 
myfont = "Font_STXIHEI.TTF"

font = pygame.font.Font(myfont, 22)    
word = u'我'
rtext = font.render(word, True, (255, 255, 255), (0, 0, 0)) 

pygame.image.save(rtext, "mmmmm.png") 

img = cv2.imread('mmmmm.png')

rows, cols, channels =  img.shape

pts1 = np.float32([[8,8],[14,14],[8,14]])
pts2 = np.float32([[8,6.5],[14,13.5],[8,13.5]])

M_affine = cv2.getAffineTransform(pts1,pts2)
img_affine = cv2.warpAffine(img, M_affine, (cols, rows))
cv2.imwrite("mmbbb.png", img_affine)

if not os.path.exists('temp'): 
    os.mkdir('temp') 
    
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
                        fn = fn+1
                        cv2.imwrite("temp/"+str(fn)+".png", img_affine)
'''