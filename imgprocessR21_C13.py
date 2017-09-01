from PIL import Image
import numpy as np  
import cv2 
import matplotlib.pyplot as plt
import struct
import mxnet as mx

engBackground = cv2.imread('engBackground.png',0)
chnBackground = cv2.imread('chnBackground.png',0)
blkBackground = np.zeros((21,13),np.uint8)

def DrawNeighAver(asum):
    for i in range(len(asum)-2):
        asum[i] = (asum[i]+asum[i+1]+asum[i+2])/3
    #plt.plot(asum)

def CompProject(canny):
    rows = canny.shape[0]
    cols = canny.shape[1]
    rowsum = np.zeros(rows)
    colsum = np.zeros(cols)
    for x in range(rows):
        for y in range(cols):
            rowsum[x] = rowsum[x] + canny[x,y]
            colsum[y] = colsum[y] + canny[x,y]
    return rowsum, colsum        

def PolyFit(arr, polynum):
    xaxis = np.arange(0,len(arr))
    z1 = np.polyfit(xaxis, arr, polynum)
    p1 = np.poly1d(z1)
    return p1(xaxis)

def CompMean(arr):
    tem_mean = np.mean(arr)
    mean_arr = np.zeros(len(arr))
    for k in range(len(arr)):
        mean_arr[k] = tem_mean
    return mean_arr   
    
def CompRowBound(rsubsum):
    submax = np.max(rsubsum)
    submin = np.min(rsubsum)
    
    incr = []
    rows = len(rsubsum)
    endrow = int(0.75*rows)+1
    k = rows-1 
    while k >= endrow:
        tem = 0 
        while k>=endrow and rsubsum[k]-rsubsum[k-1] > 0:
            tem = tem + rsubsum[k]-rsubsum[k-1]
            k = k-1 
        if tem > 0 and tem>0.1*(submax-submin):
            incr.append(k)
        k = k-1
    return incr[0]
    

def CompRowBound1(rsubsum):
    submax = np.max(rsubsum)
    submin = np.min(rsubsum)
    rows = len(rsubsum)
    print submax,submin
    startrow = int(rows*0.68)
    maxchange1 = rsubsum[startrow]-rsubsum[startrow+1]
    temrow1 = startrow+1
    maxchange2 = rsubsum[startrow+1]-rsubsum[startrow+2]
    temrow2 = startrow+2
    k = startrow+3 
    while (k < rows):
        tem = 0
        while (k < rows and rsubsum[k-1]-rsubsum[k] > 0):
            tem = tem + rsubsum[k-1]-rsubsum[k]
            k = k + 1
        if tem > maxchange2:
            if maxchange1 < maxchange2:
                maxchange1 = maxchange2
                temrow1 = temrow2
            maxchange2 = tem
            temrow2 = k
        elif tem > maxchange1:
            maxchange1 = maxchange2
            temrow1 = temrow2
            maxchange2 = tem
            temrow2 = k
        k = k + 1
    
    print startrow, temrow1, temrow2
    temrow = temrow1
    if maxchange2 > 2*maxchange1:
        temrow = temrow2
    return temrow
    
def CompColBound(csubsum):
    maxincr = 0 
    idx = 0
    cols = len(csubsum)
    for i in range(1, cols):
        tem = 0
        j = i
        for d in range(3):
            while j<cols and csubsum[j]-csubsum[j-1] > 0:
                tem = tem + csubsum[j]-csubsum[j-1]
                j = j+1 
            j = j + 1
        if tem > maxincr:
            maxincr = tem 
            idx = i
            
    return idx
    
def CropImage(img, srow, scol, erow, ecol):
    img_temp = np.zeros((erow-srow+1, ecol-scol+1), np.uint8)  
    for x in range(srow, erow+1):
        for y in range(scol, ecol+1):
            img_temp[x-srow,y-scol] = img[x, y]
    return img_temp

def SplitTextLine(smooth):
    peak = []
    if smooth[0]>smooth[1]:
        peak.append(0)
    mlen = len(smooth)
    for i in range(1,mlen-1):
        if smooth[i-1]<smooth[i] and smooth[i]>= smooth[i+1]:
            peak.append(i)
    if smooth[mlen-2]<smooth[mlen-1]:
        peak.append(mlen-1)
    
    valley = []
    if smooth[0]<smooth[1]:
        valley.append(0)
    for i in range(1, mlen-1):
        if smooth[i-1]>smooth[i] and smooth[i]<= smooth[i+1]:
            valley.append(i)
    if smooth[mlen-2]>smooth[mlen-1]:
        valley.append(mlen-1)        
    return peak, valley
    
def LineSmooth3(rsum):
    lensum = len(rsum)
    tsum = np.zeros(lensum)
    if lensum < 3:
        for i in range(lensum):
            tsum[i] = rsum[i]
    else:
        tsum[0] = (5.0*rsum[0]+2.0*rsum[1]-rsum[2])/6.0
        for i in range(1, lensum-1):
            tsum[i] = (rsum[i-1]+rsum[i]+rsum[i+1])/3.0
        tsum[lensum-1] = (5.0*rsum[lensum-1]+2.0*rsum[lensum-2]-rsum[lensum-3])/6.0
    return tsum
    
def LineSmooth5(rsum):
    lensum = len(rsum)
    tsum = np.zeros(lensum)
    if lensum < 5:
        for i in range(lensum):
            tsum[i] = rsum[i]
    else:
        tsum[0] = (3.0*rsum[0]+2.0*rsum[1]+rsum[2]-rsum[4])/5.0
        tsum[1] = (4.0*rsum[0]+3.0*rsum[1]+2.0*rsum[2]+rsum[3])/10.0
        for i in range(2, lensum-2):
            tsum[i] = (rsum[i-2]+rsum[i-1]+rsum[i]+rsum[i+1]+rsum[i+2])/5.0
        tsum[lensum-2] = (4.0*rsum[lensum-1]+3.0*rsum[lensum-2]+2.0*rsum[lensum-3]+rsum[lensum-4])/10.0
        tsum[lensum-1] = (3.0*rsum[lensum-1]+2.0*rsum[lensum-2]+rsum[lensum-3]-rsum[lensum-5])/5.0
    return tsum

def Smooth(isum, n=4):
    sm = LineSmooth7(isum)
    for i in range(1,n):
        sm = LineSmooth7(sm)
    return sm
    
def LineSmooth7(rsum):
    lensum = len(rsum)
    tsum = np.zeros(lensum)
    if lensum < 7:
        for i in range(lensum):
            tsum[i] = rsum[i]
    else:
        tsum[0] = (13.0*rsum[0]+10.0*rsum[1]+7.0*rsum[2]+4.0*rsum[3]+rsum[4]-2.0*rsum[5]-5.0*rsum[6])/28.0
        tsum[1] = (5.0*rsum[0]+4.0*rsum[1]+3.0*rsum[2]+2.0*rsum[3]+rsum[4]-rsum[6])/14.0
        tsum[2] = (7.0*rsum[0]+6.0*rsum[1]+5.0*rsum[2]+4.0*rsum[3]+3.0*rsum[4]+2.0*rsum[5]+rsum[6])/28.0
        for i in range(3, lensum-3):
            tsum[i] = (rsum[i-3]+rsum[i-2]+rsum[i-1]+rsum[i]+rsum[i+1]+rsum[i+2]+rsum[i+3])/7.0
        tsum[lensum-3] = (7.0*rsum[lensum-1]+6.0*rsum[lensum-2]+5.0*rsum[lensum-3]+4.0*rsum[lensum-4]+3.0*rsum[lensum-5]+2.0*rsum[lensum-6]+rsum[lensum-7])/28.0
        tsum[lensum-2] = (5.0*rsum[lensum-1]+4.0*rsum[lensum-2]+3.0*rsum[lensum-3]+2.0*rsum[lensum-4]+rsum[lensum-5]-rsum[lensum-7])/14.0
        tsum[lensum-1] = (13.0*rsum[lensum-1]+10.0*rsum[lensum-2]+7.0*rsum[lensum-3]+4.0*rsum[lensum-4]+rsum[lensum-5]-2.0*rsum[lensum-6]-5.0*rsum[lensum-7])/28.0
    return tsum

def FilterSmallPeak(isum):
    npmin = int(np.min(isum))
    isum = isum - npmin
    peak, valley = SplitTextLine(isum) 
    plen = len(peak)
    vlen = len(valley)
    res = []
    i = 0
    j = 0 
    while i < plen and j < vlen:
        if peak[i] < valley[j]:
            res.append([peak[i],0])
            i = i + 1 
        else:
            res.append([valley[j],1])
            j = j + 1 
    while i < plen:
        res.append([peak[i],0])
        i = i + 1 
    while j < vlen:
        res.append([valley[j],1])
        j = j + 1 
    
    maxheight = 0
    rlen = len(res)
    for i in range(rlen):
        if res[i][1]==0:
            if i > 0:
                tem = isum[res[i][0]]-isum[res[i-1][0]]
                if i < rlen-1:
                    if tem > isum[res[i][0]]-isum[res[i+1][0]]:
                        tem = isum[res[i][0]]-isum[res[i+1][0]]
                if tem > maxheight:
                    maxheight = tem
            else:
                tem = isum[res[i][0]]-isum[res[i+1][0]]
                if tem > maxheight:
                    maxheight = tem
                    
    filterRatio = 0.15                      
    for i in range(rlen):
        if res[i][1]==0:
            if i > 0:
                tem = isum[res[i][0]]-isum[res[i-1][0]]
                if tem < filterRatio*maxheight:
                    if i < rlen - 1:
                        if isum[res[i][0]]-isum[res[i+1][0]] < filterRatio*maxheight:
                            res[i][1] = 2 
                            res[i+1][1] = 2 
                    else:   
                        res[i][1] = 2 
            else:
                if isum[res[i][0]]-isum[res[i+1][0]] < filterRatio*maxheight:
                    res[i][1] = 2 

    lowRatio = 0.15
    npmax = int(np.max(isum))
    for i in range(rlen):
        if res[i][1] == 0:
            if isum[res[i][0]] < lowRatio*npmax:
                res[i][1] = 2 
                if i < rlen-1:
                    res[i+1][1] = 2

    res2 = []
    for i in range(rlen):
        if res[i][1] != 2:
            res2.append(res[i][0])
            
    peak = []        
    for i in range(rlen):
        if res[i][1] == 0:
            peak.append(res[i][0])
    valley = []
    for i in range(rlen):
        if res[i][1] == 1:
            valley.append(res[i][0])
    
    return peak, valley    


def MyResize(img):
    myheight = 480
    return cv2.resize(img, (int(img.shape[1]*myheight/img.shape[0]),myheight), interpolation=cv2.INTER_CUBIC)

def IDRowBound(isum):
    mlen = len(isum)
    idx1 = 0 
    idx2 = mlen - 1    
    
    maxchange = 0
    for i in range(mlen-1,-1, -1):
        temmax = 0 
        for k in range(1,10):
            if i-k>=0 and isum[i-k]-isum[i] > temmax:
                temmax = isum[i-k]-isum[i]
        if temmax > maxchange:
            maxchange = temmax
            idx2 = i
            
    maxchange = 0        
    for i in range(mlen):
        temmax = 0
        for k in range(1,10):
            if i+k < mlen and isum[i+k]-isum[i] > temmax:
                temmax = isum[i+k]-isum[i]
        if temmax > maxchange:
            maxchange = temmax
            idx1 = i
    return idx1, idx2
    
def TrimRowImg1(img):
    #print img.shape
    rsum, csum = CompProject(img)
    idx1,idx2 = IDRowBound(rsum)
    return CropImage(img, idx1, 0, idx2, img.shape[1]-1)
    
def TrimRowImg(img):
    rsum, csum = CompProject(img)
    
    rsmooth = Smooth(rsum, 4)
    temmin = np.min(rsmooth)
    rsmooth = rsmooth - temmin
    
    csmooth = Smooth(csum, 4)
    temmin = np.min(csmooth)
    csmooth = csmooth - temmin    
    
    peak, valley = SplitTextLine(rsmooth)
    peak, valley = FilterSmallPeak(rsmooth)
    
    if len(peak)==0 or len(valley)==0:
        return None
        
    trimRatio = 0.85
    
    rtotal = 0
    rlen = len(rsmooth)
    for i in range(rlen):
        rtotal = rtotal + rsmooth[i]
    temtotal = rsmooth[peak[0]]
    halfheight = 12
    for i in range(1, rlen):
        if peak[0]+i<rlen:
            temtotal = temtotal + rsmooth[peak[0]+i]
        if peak[0]-i >= 0:
            temtotal = temtotal + rsmooth[peak[0]-i]
        if i>12:
            if 1.0*temtotal/rtotal > trimRatio:
                halfheight = i 
                break
        if peak[0]+i >= rlen and peak[0]-i < 0:
            break
    
    startrow = peak[0]-halfheight if peak[0]-halfheight>0 else 0 
    endrow = peak[0]+halfheight if peak[0]+halfheight<rlen else rlen-1
    
    return CropImage(img, startrow, 0, endrow, img.shape[1]-1)
    
def TrimTextImg(img):
    rsum, csum = CompProject(img)
    
    rsmooth = Smooth(rsum, 4)
    temmin = np.min(rsmooth)
    rsmooth = rsmooth - temmin
    
    csmooth = Smooth(csum, 4)
    temmin = np.min(csmooth)
    csmooth = csmooth - temmin    
    
    peak, valley = SplitTextLine(rsmooth)
    peak, valley = FilterSmallPeak(rsmooth)
    
    if len(peak)==0 or len(valley)==0:
        return None
        
    trimRatio = 0.90
    
    rtotal = 0
    rlen = len(rsmooth)
    for i in range(rlen):
        rtotal = rtotal + rsmooth[i]
    temtotal = rsmooth[peak[0]]
    halfheight = 12
    for i in range(1, rlen):
        if peak[0]+i<rlen:
            temtotal = temtotal + rsmooth[peak[0]+i]
        if peak[0]-i >= 0:
            temtotal = temtotal + rsmooth[peak[0]-i]
        if i>12:
            if 1.0*temtotal/rtotal > trimRatio:
                halfheight = i 
                break
        if peak[0]+i >= rlen and peak[0]-i < 0:
            break
    
    startrow = peak[0]-halfheight if peak[0]-halfheight>0 else 0 
    endrow = peak[0]+halfheight if peak[0]+halfheight<rlen else rlen-1
    if startrow<5:
        startrow = 0 
    if endrow > img.shape[0]-5:
        endrow = img.shape[0]-1
    
    peak, valley = SplitTextLine(csmooth)
    peak, valley = FilterSmallPeak(csmooth)
    
    ctotal = 0 
    clen = len(csmooth)
    for i in range(clen):
        ctotal = ctotal + csmooth[i]
    temtotal = csmooth[peak[0]]
    halfwidth = 12 
    for i in range(1,clen):
        if peak[0]+i < clen:
            temtotal = temtotal + csmooth[peak[0]+i]
        if peak[0]-i >= 0:
            temtotal = temtotal + csmooth[peak[0]-i]
        if i > 12:
            if 1.0*temtotal/ctotal > trimRatio:
                halfwidth = i 
                break
        if peak[0]+i >= clen and peak[0]-i<0:
            break
    
    startcol = peak[0]-halfwidth if peak[0]-halfwidth>0 else 0 
    endcol = peak[0]+halfwidth if peak[0]+halfwidth<clen else clen-1
    
    if startcol<10:
        startcol = 0 
    if endcol > img.shape[1]-8:
        endcol = img.shape[1]-1
       
    return CropImage(img, startrow, startcol, endrow, endcol)

def FixedShape(img, ch=0): 
    fixRow = 21
    fixCol = 13
    resImg = []
    if ch == 0:
        resImg = blkBackground.copy()
    elif ch == 1:
        resImg = engBackground.copy()
    else:
        fixRow = 28
        fixCol = 28
        resImg = chnBackground.copy()
    #resImg = np.zeros((fixRow, fixCol), np.uint8)
    if 1.0*img.shape[0]/fixRow > 1.0*img.shape[1]/fixCol:
        temRow = fixRow
        temCol = int(img.shape[1]*fixRow/img.shape[0])            
        temImg = cv2.resize(img, (temCol, temRow), interpolation=cv2.INTER_CUBIC)
        colOffset = (fixCol-temCol)/2
        #print colOffset, fixCol, temCol
        for x in range(temImg.shape[0]):
            for y in  range(temImg.shape[1]):
                resImg[x,colOffset+y] = temImg[x,y]
    else:
        temRow = int(img.shape[0]*fixCol/img.shape[1])
        temCol = fixCol
        temImg = cv2.resize(img, (temCol, temRow), interpolation=cv2.INTER_CUBIC)
        rowOffset = (fixRow-temRow)/2
        #print rowOffset, fixRow, temRow
        for x in range(temImg.shape[0]):
            for y in  range(temImg.shape[1]):
                resImg[rowOffset+x,y] = temImg[x,y]
    return resImg       

def BackgroundPix(sm):
    lensm = len(sm)
    temmax = 0 
    idxmax = 0
    for i in range(lensm):
        if sm[i] > temmax:
            temmax = sm[i]
            idxmax = i 
    for i in range(idxmax+1, lensm):
        if sm[i] > sm[i-1]:
            return i
    return lensm-1
    
def ToBinary(img): 
    hist = cv2.calcHist([img], [0], None, [256], [0.0,255.0])
    sm = Smooth(hist[:,0], 4)
    bg = BackgroundPix(sm)
    for x in range(img.shape[0]):
        for y in range(img.shape[1]):
            if img[x,y]<=bg:
                img[x,y] = 0
    return img
############################################
#processing id number
############################################    
def ProcessIDNumber(img_ID):
    img_ID = TrimRowImg(img_ID)
    rsum,csum = CompProject(img_ID)
    smooth = Smooth(csum, 4)
    peak, valley = SplitTextLine(smooth)
    peak, valley = FilterSmallPeak(smooth)
    bd1 = 0
    bd2 = img_ID.shape[0]-1
    
    plt.plot(smooth)
    
    avewidth = 0
    lenvalley = len(valley)
    for i in range(12):
        avewidth = avewidth + valley[lenvalley-3-i]-valley[lenvalley-3-i-1]
    avewidth = int(avewidth/12.0)
    valley[-1] = valley[-2]+avewidth+1
    valley[-19] = valley[-18]-avewidth
    
    for i in range(0, 6):
        temImg = CropImage(img_ID, 0, valley[i], img_ID.shape[0]-1, valley[i+1])
        #cv2.imshow('text'+str(i), temImg)
        
    imgList = []
    startIDNumIdx = 6
    avewidth2 = 0 
    for i in range(4):
        avewidth2 = avewidth2 + valley[i+1]-valley[i]
    avewidth2 = int(avewidth2/4)
    if valley[0]>=avewidth2:
        startIDNumIdx = 5
    for i in range(startIDNumIdx, len(valley)-1):
        temImg = CropImage(img_ID, bd1, valley[i], bd2, valley[i+1])
        #temImg = TrimTextImg(temImg)
        temImg = ToBinary(temImg)
        if temImg is not None:
            temImg= FixedShape(temImg, 0)
            imgList.append(temImg)
            #print '-------------------show-------------------'
            #cv2.imshow('text'+str(i), temImg)
            #cv2.waitKey(0)
    
    cv2.line(img_ID,(0, bd1),(cols-1, bd1),255,1)
    cv2.line(img_ID,(0, bd2),(cols-1, bd2),255,1)
    for i in range(len(valley)):
        cv2.line(img_ID,(valley[i], bd1),(valley[i], bd2),255,1)
    
    #cv2.imshow('img_ID', img_ID)
       
    return imgList 
        
############################################
#processing name                           
############################################
def ProcessName(img_name, img_precrop, validTextCol, bound1, bound2):
    img_name = TrimRowImg(img_name)
    rsum,csum = CompProject(img_name)
    smooth = Smooth(csum,6)
    peak, valley = SplitTextLine(smooth) 
    peak, valley = FilterSmallPeak(smooth)
    
    '''
    avewidth = 0
    for i in range(1, len(valley)-1):
        avewidth = avewidth + valley[i]-valley[i-1]
    avewidth = avewidth/(len(valley)-2)
    print len(valley)
    '''
    imgList = []
    for i in range(len(valley)-1):
        temImg = CropImage(img_name, 0, valley[i], img_name.shape[0]-1, valley[i+1])
        temImg = TrimTextImg(temImg)
        if temImg is not None:
            temImg= FixedShape(temImg, 2)
            imgList.append(temImg)
            #cv2.imshow('name'+str(i), temImg)
    '''
    temImg = CropImage(img_name, 0, valley[-2], img_name.shape[0]-1, valley[-2]+avewidth+5)
    temImg = TrimTextImg(temImg)
    if temImg is not None:
        temImg= FixedShape(temImg, 2)
        imgList.append(temImg)
        cv2.imshow('name'+str(3), temImg)
    '''       
    for i in range(len(valley)):
        cv2.line(img_precrop,(validTextCol+valley[i], bound1),(validTextCol+valley[i], bound2),255,1)   
        
    #cv2.imshow('img_name', img_name)
    
    return imgList 
    
############################################
#process sex
############################################
def ProcessSex(img_sex, img_precrop, validTextCol, bound1, bound2):
    img_sex = TrimRowImg(img_sex)
    rsum,csum = CompProject(img_sex)
    smooth = Smooth(csum,4)
    peak, valley = SplitTextLine(smooth) 
    peak, valley = FilterSmallPeak(smooth)
    
    imgList = []
    temImg = CropImage(img_sex, 0, valley[0], img_sex.shape[0]-1, valley[1])
    temImg = TrimTextImg(temImg)
    if temImg is not None:
        temImg= FixedShape(temImg, 2)
        imgList.append(temImg)
    for i in range(3, len(valley)-1):
        temImg = CropImage(img_sex, 0, valley[i], img_sex.shape[0]-1, valley[i+1])
        temImg = TrimTextImg(temImg)
        if temImg is not None:
            temImg= FixedShape(temImg, 2)
            imgList.append(temImg)
        #cv2.imshow('text'+str(i), temImg)
        
    for i in range(len(valley)):
        cv2.line(img_precrop,(validTextCol+valley[i], bound1),(validTextCol+valley[i], bound2),255,1)
        
    #cv2.imshow('img_sex', img_sex)    
    
    return imgList 

############################################
#process birth
############################################        
def ProcessBirth(img_birth, img_precrop, validTextCol, bound1, bound2):
    img_birth = TrimRowImg(img_birth)
    rsum,csum = CompProject(img_birth)
    smooth = Smooth(csum,4)
    peak, valley = SplitTextLine(smooth) 
    peak, valley = FilterSmallPeak(smooth)
    
    imgList = []
    for i in range(0, len(valley)-1):
        temImg = CropImage(img_birth, 0, valley[i], img_birth.shape[0]-1, valley[i+1])
        temImg = TrimTextImg(temImg)
        if temImg is not None:
            temImg= FixedShape(temImg, 2)
            imgList.append(temImg)
        #cv2.imshow('text'+str(i), temImg)
        
    for i in range(len(valley)):
        cv2.line(img_precrop,(validTextCol+valley[i], bound1),(validTextCol+valley[i], bound2),255,1)
    for i in range(len(valley)):
        cv2.line(img_birth,(valley[i], 0),(valley[i], img_birth.shape[0]-1),255,1)   
    
    #cv2.imshow('birth', img_birth)  
    
    return imgList   

############################################
#process address
############################################    
def ProcessAddress(img_addr, img_precrop, validTextCol, bound1, bound2):
    img_addr = TrimRowImg(img_addr)
    rsum,csum = CompProject(img_addr)
    smooth = Smooth(csum,6)
    peak, valley = SplitTextLine(smooth) 
    peak, valley = FilterSmallPeak(smooth)
    
    #print peak, valley
    
    #plt.plot(smooth)
    
    imgList = []
    for i in range(len(valley)-1):
        temImg = CropImage(img_addr, 0, valley[i], img_addr.shape[0]-1, valley[i+1])
        temImg = TrimTextImg(temImg)
        if temImg is not None:
            temImg= FixedShape(temImg, 2)
            imgList.append(temImg)
            #cv2.imshow('text'+str(i), temImg)
    
    for i in range(len(valley)):
        cv2.line(img_precrop,(validTextCol+valley[i], bound1),(validTextCol+valley[i], bound2),255,1)
    
    #cv2.imshow('img_addr', img_addr)
    
    return imgList    

def ShowTextImage(panel, imgList, startRow):
    startCol = 0
    for img in imgList:
        for x in range(img.shape[0]):
            for y in range(img.shape[1]):
                panel[startRow+x, startCol+y] = img[x,y]
        startCol = startCol + img.shape[1] + 1

def RecogIDNumber(imgList):
    val_img_buf = ''
    val_lab_buf = ''
    val_img_num = 0
    rows = 21
    cols = 13
    for img in imgList:
        val_img_num = val_img_num + 1
        rows, cols= img.shape
        for x in range(rows):
            for y in range(cols):
                val_img_buf = val_img_buf + struct.pack('>B',img[x,y])
    val_img_buf = struct.pack('>IIII',1, val_img_num, rows, cols) + val_img_buf
    save = open('ubyte_test_image', 'wb')
    save.write(val_img_buf)
    save.close()
    
    test  = mx.io.MNISTIter(
        image      = "ubyte_test_image",
        label      = "ubyte_val_label",
        batch_size = 1,
        shuffle    = 0,)
    model = mx.model.FeedForward.load('model_idcard', 20)
    [probs, data, label] = model.predict(X = test, return_data=True)
    startIdx = 0 
    if len(probs) > 18:
        startIdx = len(probs)-18
    for i in range(startIdx, len(probs)):
        idnum = np.argmax(probs[i])
        if idnum<10:
            print idnum,
        else:
            print 'X',
    print
        
if __name__ == '__main__':    
    for id in xrange(1,7):    
        img_org = cv2.imread('images\\id'+ str(id) + '.jpg', 0)
        img_org = MyResize(img_org)
        img = 255 - img_org
        
        print 'resize shape:', img.shape
        rows = int(img.shape[0]*0.70)
        cols = int(img.shape[1]*0.84)    
        sr = int(img.shape[0]*0.19)
        sc = int(img.shape[1]*0.08)
        img_blur = CropImage(img, sr, sc, sr+rows, sc+cols)
        img_precrop = CropImage(img, sr, sc, sr+rows, sc+cols)
        
        img_blur = cv2.blur(img_blur, (7,7))    
        rsum,csum = CompProject(img_blur)
        
        #smooth = Smooth(rsum, 4)
        #plt.plot(smooth)
        
        #归一化
        tem_min = np.min(rsum)
        rsum = rsum - tem_min    
        tem_min = np.min(csum)
        csum = csum - tem_min
        
        canny = cv2.Canny(img_blur, 200, 355, apertureSize = 3)
        
        rowcannysum,colcannysum = CompProject(canny)
            
        rowbound = CompRowBound(rsum-rowcannysum)
        
        img_delID = np.zeros((rowbound, cols), np.uint8)  
        for x in range(rowbound):
            for y in range(cols):
                img_delID[x,y] = img_blur[x, y]
        
        rsum,csum = CompProject(img_delID)
        colbound = CompColBound(csum)
        
        img_delIDImg = np.zeros((rowbound, colbound), np.uint8)  
        for x in range(rowbound):
            for y in range(colbound):
                img_delIDImg[x,y] = img_delID[x, y]
        
        panel = np.zeros((rows*2, cols*2), np.uint8)
        panel = 255-panel
        ############################################
        #processing id number
        ############################################
        img_ID = CropImage(img_precrop, rowbound, 0, rows-1, cols-1)
        imgIDList = ProcessIDNumber(img_ID)
        ShowTextImage(panel, imgIDList, 0)
        RecogIDNumber(imgIDList)
        ############################################
        #process the text area except the id number
        ############################################
        img_text = CropImage(img_precrop, 0, 0, rowbound, colbound)
        rsum,csum = CompProject(img_text)
        smooth = Smooth(csum,4)
        textColPeak, textColValley = SplitTextLine(smooth)
        textColPeak, textColValley = FilterSmallPeak(smooth)
        validTextCol = textColValley[2]+8
        
        img_text = CropImage(img_precrop, 0, validTextCol, rowbound, colbound)        
        rsum,csum = CompProject(img_text)
        smooth = Smooth(rsum,4)
        #plt.plot(rsum)
        #plt.plot(smooth)
        textRowPeak, textRowValley = SplitTextLine(smooth)
        textRowPeak, textRowValley = FilterSmallPeak(smooth)
        for i in range(len(textRowValley)):
            cv2.line(img_precrop,(0,textRowValley[i]),(colbound,textRowValley[i]),255,1)
        ############################################
        #processing name                           
        ############################################       
        img_name = CropImage(img_text, textRowValley[0],0, textRowValley[1], img_text.shape[1]-1)
        imgNameList = ProcessName(img_name, img_precrop, validTextCol, textRowValley[0], textRowValley[1])
        ShowTextImage(panel, imgNameList, 50)
        ############################################
        #process sex
        ############################################
        img_sex = CropImage(img_text, textRowValley[1],0, textRowValley[2], img_text.shape[1]-1)
        imgSexList = ProcessSex(img_sex, img_precrop, validTextCol, textRowValley[1], textRowValley[2])
        ShowTextImage(panel, imgSexList, 100)
        ############################################
        #process birth
        ############################################
        img_birth = CropImage(img_text, textRowValley[2],0, textRowValley[3], img_text.shape[1]-1)    
        imgBirthList = ProcessBirth(img_birth, img_precrop, validTextCol, textRowValley[2], textRowValley[3])
        ShowTextImage(panel, imgBirthList, 150)  
        
        ############################################
        #process address
        ############################################
        img_addr = CropImage(img_text, textRowValley[3],0, textRowValley[4], img_text.shape[1]-1)    
        imgAddrList = ProcessAddress(img_addr, img_precrop, validTextCol, textRowValley[3], textRowValley[4])
        averAddrHeight = 0 
        for img in imgAddrList:
            averAddrHeight = averAddrHeight + img.shape[0]
        averAddrHeight = averAddrHeight/(len(imgAddrList)+0.01)
        for idxAddr in range(4, len(textRowValley)-1):
            img_addr = CropImage(img_text, textRowValley[idxAddr],0, textRowValley[idxAddr+1], img_text.shape[1]-1)  
            temList = ProcessAddress(img_addr, img_precrop, validTextCol, textRowValley[idxAddr], textRowValley[idxAddr+1])
            for img in temList:
                if img.shape[0] > 0.56*averAddrHeight:
                    imgAddrList.append(img)
        ShowTextImage(panel, imgAddrList, 200)    
            
        cv2.line(img_precrop,(colbound,0),(colbound,rowbound),255,1)
        cv2.line(img_precrop,(0,rowbound),(colbound,rowbound),255,1)    
        cv2.imshow('gray_'+str(id), img_precrop)
        
        cv2.imshow('panel', panel)
        cv2.imwrite('panel.png', panel)
        
        #DrawNeighAver(rsum-rowcannysum)    
        #pf_row = PolyFit(rsum, 20)
        #pf_col = PolyFit(csum, 2)    
        #plt.plot(rsum)
        #plt.plot(smooth)
        #plt.plot(CompMean(rsum))    
        #plt.plot(pf_row)    
        #plt.plot(csum)
        #plt.plot(CompMean(csum))
        #plt.plot(pf_col)
        plt.show()
        
        
        #cv2.waitKey(0)
        cv2.destroyAllWindows() 

        
