from PIL.Image import NONE
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons


class ImageIO:
    def __init__(self,imgPathAry):
        self.imgPathAry = imgPathAry
        self.loadedImgs = []
        self._load()

    def __len__(self):
        return len(self.loadedImgs)

    def _load(self):
        for i in self.imgPathAry:
            self.loadedImgs.append(cv.imread(i))
    def resize(self,xy):
        for i in range(0,len(self.loadedImgs)):
            self.loadedImgs[i] = cv.resize(self.loadedImgs[i], xy)
    def get(self,i):
        if(i>len(self.loadedImgs)-1):
            return None
        return self.loadedImgs[i]

class FigViewer:
    def __init__(self, figID = None):
        self.fig = plt.figure(figID)
        pass
    def plot_img(self,rows, cols, index, img, title):
        self.ax = plt.subplot(rows,cols,index)
        if(len(img.shape) == 3):
            self.ax_img = plt.imshow(img[...,::-1])
        else:
            self.ax_img = plt.imshow(img, cmap='gray')
        plt.axis('on')
        if(title != None): plt.title(title) 
        return self.ax_img, self.ax
    def show(self):
        plt.figure(self.fig)
        plt.show()

class Parnorama:
    def __init__(self):
        self.currentIdx = 0
        self.imageFrame = None
        self.matches_lines_ary = []
        self.goodCoors = []

    def addNewImg(self, img):
        if(self.currentIdx == 0):
            self.imageFrame = np.zeros((img.shape[0]*3,img.shape[1],3),np.uint8)
            self.imageFrame[img.shape[0]:img.shape[0]*2:,:] = img
        else:
            self.stitch(img)
        self.currentIdx += 1

    def stitch(self,img):
        #최종 이미지의 가로세로 정의
        total_row = self.imageFrame.shape[0]
        total_col = self.imageFrame.shape[1] + img.shape[1]

        #SIFT + FLANN  써서 
        sift = cv.SIFT_create()
        flann = cv.FlannBasedMatcher({"algorithm":1, "trees":5}, {"checks":50})

        org_kp, org_des = sift.detectAndCompute(self.imageFrame, None)
        img_kp, img_des = sift.detectAndCompute(img, None)
        matches = flann.knnMatch(org_des, img_des, k=2)

        goodCorr = []
        goodCorr.clear()
        for m,n in matches:
            if m.distance/n.distance < 0.8: # Coreespondences 수치 및 적용
                goodCorr.append(m)

        matches_lines = cv.drawMatches(self.imageFrame,org_kp,img,img_kp,goodCorr,None,
                                        matchColor=(0,255,0),singlePointColor=None,matchesMask=None,flags=2)
        self.matches_lines_ary.append(matches_lines)
        self.goodCoors.append(goodCorr)

        org_pts = np.float32([ org_kp[m.queryIdx].pt for m in goodCorr ]).reshape(-1,1,2)
        img_pts = np.float32([ img_kp[m.trainIdx].pt for m in goodCorr ]).reshape(-1,1,2)
        Homography, H_Mask = cv.findHomography(img_pts, org_pts, cv.RANSAC, 5.0)

        img_rs = cv.warpPerspective(img, Homography, (total_col, total_row),
                                 flags=cv.INTER_LINEAR, borderMode=cv.BORDER_TRANSPARENT)

        org_rs = np.zeros((total_row, total_col, 3), np.uint8)
        org_rs[0:self.imageFrame.shape[0], 0:self.imageFrame.shape[1]] = self.imageFrame

        # result1, result2와 서로 겹치는 마스크 도출
        and_img = cv.bitwise_and(img_rs, org_rs)
        and_img_gray = cv.cvtColor(and_img, cv.COLOR_BGR2GRAY)
        # 마스크와 역 마스크 생성
        Threshold, T_Mask = cv.threshold(and_img_gray, 1, 255, cv.THRESH_BINARY)
        T_Mask= cv.cvtColor(T_Mask,cv.COLOR_GRAY2BGR)
        T_Mask_INV = cv.bitwise_not(T_Mask)
        # T_Mask_INV = cv.cvtColor(T_Mask_INV,cv.COLOR_GRAY2BGR)

        # 마스크로 겹치는 부분 겹쳐 뽑기
        mask_layer = cv.bitwise_and( T_Mask, (img_rs*0.5 + org_rs*0.5).astype(np.uint8) )
        
        # 역마스크로 겹치지 않는 부분 각각 뽑기
        print(org_rs.shape,T_Mask_INV.shape)
        org_layer = cv.bitwise_and(T_Mask_INV,org_rs)
        img_layer = cv.bitwise_and(T_Mask_INV,img_rs)

        total_rs = np.zeros((total_row, total_col, 3), np.uint8)
        total_rs = org_layer.astype(np.uint8) + mask_layer.astype(np.uint8) +img_layer.astype(np.uint8)

        self.imageFrame = None
        self.imageFrame = total_rs


    def getImg(self):
        if(self.currentIdx < 1):
            raise "There are no imgs"
        return self.imageFrame


        

    def showMatchLines(self):
        fv = FigViewer()
        lines = len(self.matches_lines_ary)
        for i in range(0,lines):
            fv.plot_img(1,lines,i+1,self.matches_lines_ary[i],'STEP(%s)'%str(i+1))
        fv.show()
    