from cmath import sqrt
from mailbox import linesep
from pydoc import importfile
import numpy as np
import matplotlib.pyplot as plt
import gdstk
import time
import math 
from progressbar import *
from rdp import rdp
import argparse

class teh_chin_point:
    def __init__(self) -> None:
        self.point = np.zeros(2)
        self.cosine = 0
        self.k = 0

def Chord_length(p1,p2):
    return sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2).real

def Differential(p1,p2):
    return (p2[1]-p1[1])/p2[0]-p1[0]

def teh_chin(line):
    # step 1 : support range
    teh_chin_line = []
    teh_chin_line_out = []
    for point in range(0,line.shape[0],1):
        if (point<=1):
            inst_teh_chin_point = teh_chin_point()
            inst_teh_chin_point.point = line[point]
            inst_teh_chin_point.cosine = 1
            inst_teh_chin_point.k = 1
            teh_chin_line.append(inst_teh_chin_point)
            continue
        for k in range(1,min(point,line.shape[0]-point),1):
            if (k+1>point or point+k+1>line.shape[0]-1):
                inst_teh_chin_point = teh_chin_point()
                inst_teh_chin_point.point = line[point]
                inst_teh_chin_point.cosine = 1
                inst_teh_chin_point.k = k
                break
            d_k = Differential(line[point-k],line[point+k])
            l_k = Chord_length(line[point-k],line[point+k])
            d_kp1 = Differential(line[point-k-1],line[point+k+1])
            l_kp1 = Chord_length(line[point-k-1],line[point+k+1])
            if ((d_k/l_k>=d_kp1/l_kp1 and d_k >=0) or (d_k/l_k<=d_kp1/l_kp1 and d_k <0)):
                inst_teh_chin_point = teh_chin_point()
                inst_teh_chin_point.point = line[point]
                a = line[point-k] - line[point]
                b = line[point+k] - line[point]
                chord_a = Chord_length([0,0],a)
                chord_b = Chord_length([0,0],b)
                inst_teh_chin_point.cosine = (a[0]*b[0]+a[1]*b[1])/(chord_a*chord_b)
                inst_teh_chin_point.k = k
                break
        teh_chin_line.append(inst_teh_chin_point)

    # step 2 : filter points
    for point in range(2,line.shape[0],1):
        if (teh_chin_line[point].cosine+1<epsilon):
            # if the cosine the too small, drop the point
            continue
        if (teh_chin_line[point].cosine>=teh_chin_line[point-math.floor(teh_chin_line[point].k/2)].cosine):
            teh_chin_line_out.append(teh_chin_line[point].point)
            
    return np.array(teh_chin_line_out)

def draw_gds(contour,epsilon):
    # define lib
    lib = gdstk.Library()
    main = lib.new_cell("Main")

    # collect point
    # vertex = contour.allsegs[0][0]
    layer = 0
    bar = ProgressBar().start()
    for line_index in range(0,len(contour.allsegs),2):
        # vertex = np.append(vertex,contour.allsegs[line+1][0],axis=0)
        # draw gdsii

        # print out points numbers
        print('raw line points is %d ',contour.allsegs[line_index][0].shape)

        # rpd sparse
        # contour_sparse = rdp(contour.allsegs[line_index][0], epsilon=epsilon)
        # teh_chin sparse
        contour_sparse = teh_chin(contour.allsegs[line_index][0])
        print('sparse line points is %d ',contour_sparse.shape)

        vertex = contour_sparse*1000
        line = gdstk.Polygon(vertex,layer=0,datatype=0)
        # contour_sparse = rdp(contour.allsegs[line_index+1][0], epsilon=epsilon)
        contour_sparse = teh_chin(contour.allsegs[line_index+1][0])
        vertex_out = contour_sparse*1000
        line_out = gdstk.Polygon(vertex_out,layer=layer,datatype=0)
        annulus = gdstk.boolean(line_out,line, "not")
        
        main.add(annulus[0])
        layer = layer + 1
        # print("drawing curve %d/%d",line_index,len(contour.allsegs))

    # save file
    bar.finish()
    lib.write_gds("gds_{}_{}.gds".format(time.strftime("%Y%m%d_%H%M",time.localtime()),epsilon))


parser = argparse.ArgumentParser(description='命令行中传入一个数字')
#type是要传入的参数的数据类型  help是该参数的提示信息
parser.add_argument('epsilon', type=float, help='ep silon for dp algo',default=1)

args = parser.parse_args()

# print(args.integers)
epsilon = args.epsilon

step = 0.1
bound = 80
x = np.arange(-bound,bound,step)
y = np.arange(-bound,bound,step)
X,Y = np.meshgrid(x,y)

# define function
Z = (100*X**2+Y**2)*0.05

#solve function
bar = ProgressBar().start()
num_phase = 20
phase = np.linspace(np.pi,num_phase*np.pi,num_phase)
contour = plt.contour(X,Y,Z,phase,colors='k')
# plt.show()
bar.finish()
# convert contour into gdsii file 
draw_gds(contour,epsilon)
