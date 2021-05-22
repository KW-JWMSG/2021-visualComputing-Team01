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

    def get(self,i):
        if(i>len(self.loadedImgs)-1):
            raise 'ImageOverFlow'
        return self.loadedImgs[i]
