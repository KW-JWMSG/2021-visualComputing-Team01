from PIL.Image import NONE
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

class FigViewer:
    def __init__(self, figID = None):
        self.fig = plt.figure(figID)
        pass
    def plot_img(self, rows, cols, index, img, title):
        plt.figure(self.fig)
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
