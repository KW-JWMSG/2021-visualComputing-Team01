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
        for img in self.loadedImgs:
            img = cv.resize(img, xy)
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
    def __init__(self, imgLeft, imgRight = None):
        self.imgLeft = imgLeft
        self.imgRight = imgRight
        self.resultIMG = imgLeft
        self.ready = True
        self.good_correspondences = []


    def drawCoreespondencesLines(self):
        img_matches = cv.drawMatches(
                                    self.imgLeft,self.left_kp,
                                    self.imgRight,self.right_kp,
                                    self.good_correspondences,None,
                                    matchColor=(0,255,0),singlePointColor=None,
                                    matchesMask=None,flags=2)
        img_matches = cv.cvtColor(img_matches, cv.COLOR_BGR2RGB)
        return img_matches

    def _genGray(self):
        #사진 흑백화
        self.imgLeft_g = cv.cvtColor(self.imgLeft, cv.COLOR_BGR2GRAY)
        self.imgRight_g = cv.cvtColor(self.imgRight, cv.COLOR_BGR2GRAY)
    
    def _calcSIFT(self):
        #SIFT 알고리즘으로 특징점 검출 및 계산
        sift = cv.SIFT_create()
        self.left_kp, self.left_des = sift.detectAndCompute(self.imgLeft, None)
        self.right_kp, self.right_des = sift.detectAndCompute(self.imgRight, None)

    def _drawKFP(self):
        #특징점 찍기
        self.imgLeft_g_kfp = cv.drawKeypoints(self.imgLeft_g, self.left_kp, 
                                      None, flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        self.imgRight_g_kfp = cv.drawKeypoints(self.imgRight_g, self.right_kp, 
                                        None, flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    
    def _flannMatch(self):
        #flann 알고리즘으로 KNN매칭
        flann = cv.FlannBasedMatcher({"algorithm":1, "trees":5}, {"checks":50})
        self.matches = flann.knnMatch(self.left_des, self.right_des, k=2)
    
    def _calc_good_correpondences(self,ratio_dist):
        self.good_correspondences.clear()
        for m,n in self.matches:
            if m.distance/n.distance < ratio_dist:
                self.good_correspondences.append(m)
    
    def _calc_H_Value(self):
        self.left_pts = np.float32([ self.left_kp[m.queryIdx].pt for m in self.good_correspondences ]).reshape(-1,1,2)
        self.right_pts = np.float32([ self.right_kp[m.trainIdx].pt for m in self.good_correspondences ]).reshape(-1,1,2)
        self.H, self.mask = cv.findHomography(self.right_pts, self.left_pts, cv.RANSAC, 5.0)
        
    def _calc_threshold(self,leftImg,rightImg):
        #왼쪽 오른쪽 마스크 뽑기
        and_img = cv.bitwise_and(leftImg, rightImg)
        and_img_gray = cv.cvtColor(and_img, cv.COLOR_BGR2GRAY)
        th, mask = cv.threshold(and_img_gray, 1, 255, cv.THRESH_BINARY)
        return th, mask

    def _stitch_imges(self,rows,cols,leftImg_Rs,rightImg_Rs,mask):
        total_Rs = np.zeros((rows, cols,3), np.uint8)
        #일단 오른쪽 그냥 붙여넣고, 왼쪽부분만 덮어씌운뒤 마스크부분을 덮어씌우는게 속도상 제일 빠름.
        total_Rs[0:self.imgLeft.shape[0], 0:self.imgLeft.shape[1]] = leftImg_Rs[0:self.imgLeft.shape[0], 0:self.imgLeft.shape[1]]
        total_Rs += rightImg_Rs
        for y in range(rows):
            for x in range(cols):
                mask_v = mask[y, x]
                if(mask_v > 0):
                    total_Rs[y, x] = np.uint8(rightImg_Rs[y,x] * 0.5 + leftImg_Rs[y,x] * 0.5)
                elif(self.imgLeft.shape[1] < x):
                    break
               
        return total_Rs

    def _do_stitching(self):
        #화면이어붙이기
        total_stitched_rows = self.imgRight.shape[0]#세로길이 정의
        total_stitched_cols = self.imgLeft.shape[1] + self.imgRight.shape[1] #가로길이 정의

        #오른쪽 이미지 변형
        imgRight_Result = cv.warpPerspective(
                                    self.imgRight, self.H, (total_stitched_cols, total_stitched_rows),
                                    flags=cv.INTER_LINEAR, borderMode=cv.BORDER_TRANSPARENT)
                                    
        #왼쪽이미지 기준점잡기
        imgLeft_Result = np.zeros((total_stitched_rows, total_stitched_cols, 3), np.uint8)
        imgLeft_Result[0:self.imgLeft.shape[0], 0:self.imgLeft.shape[1]] = self.imgLeft
        th, calc_mask = self._calc_threshold(imgLeft_Result,imgRight_Result)
        return self._stitch_imges(total_stitched_rows,total_stitched_cols,imgLeft_Result,imgRight_Result,calc_mask)

    def _preCalc(self):
        self._genGray()
        self._calcSIFT()
        self._flannMatch()
        self._calc_good_correpondences(0.7)
        self._calc_H_Value()
 
    def stitch(self):
        try:
            if self.ready:
                self._preCalc()
                self.resultIMG = self._do_stitching()
        except Exception as e:
            pass
        return self.resultIMG
    
    def getRs(self):
        return self.resultIMG
        
    
    