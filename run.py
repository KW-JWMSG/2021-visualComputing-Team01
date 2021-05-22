import PanoramaUtil as pu
import cv2 as cv
import sys

def main():
    print(sys.argv[0])
    if(len(sys.argv)<3):
        print("Useage: run.py <sizeX>:<sizeY> <imgpath1>, <imgpath2>, ... <imgpathN>")
        exit()
    imges = pu.ImageIO(sys.argv[2:])
    rsizeX = int(sys.argv[1].split(":")[0])
    rsizeY = int(sys.argv[1].split(":")[1])
    imges.resize((rsizeX,rsizeY))

    pm = pu.Parnorama()
    for i in range(0,len(imges)):
        pm.addNewImg(imges.get(i))
    
    pm.showMatchLines()

    


if __name__ == "__main__":
    main()