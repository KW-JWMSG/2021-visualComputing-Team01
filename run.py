import PanoramaUtil as pu
import cv2 as cv
import sys

from threading import Thread

def runQ(pm1, pm2):
    p1 = Thread(target=pm1.stitch, args=())
    p2 = Thread(target=pm2.stitch, args=())
    p1.start()
    p2.start()
    p1.join()
    p2.join()

def main():
    print(sys.argv[0])
    if(len(sys.argv)<3):
        print("Useage: run.py <sizeX>:<sizeY> <imgpath1>, <imgpath2>, ... <imgpathN>")
        exit()
    imges = pu.ImageIO(sys.argv[2:])
    rsizeX = int(sys.argv[1].split(":")[0])
    rsizeY = int(sys.argv[1].split(":")[1])
    imges.resize((rsizeX,rsizeY))

    pms = [pu.Parnorama(imges.get(i),imges.get(i+1)) for i in range(0, len(imges),2)]

    while len(pms) > 1:
        n_pms = []
        print("loop",len(pms),len(n_pms))
        for i in range(0,len(pms),2):
            if(i+1 < len(pms)):
                runQ(pms[i],pms[i+1])
                n_pms.append(pu.Parnorama(pms[i].getRs(),pms[i+1].getRs()))
            else:
                pms[i].stitch()
                n_pms.append(pms[i])
        print("loop",len(pms),len(n_pms))
        pms = n_pms
    if( len(pms) == 1):
        pms[0].stitch()

    fv = pu.FigViewer()
    for i in range(0,len(pms)):
        fv.plot_img(len(pms),1,i+1,pms[i].getRs(),str("RS"+str(i)))
    fv.show()

if __name__ == "__main__":
    main()