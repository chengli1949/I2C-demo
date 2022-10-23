# 基于计算全息图的非球面高精度检测技术研究 邱宏伟
# 光学面形检测计算全息补偿器的制造关键技术及其精度评价 甘子豪
from cmath import sqrt
# import imp
from mailbox import linesep
from pydoc import importfile
from random import random
import numpy as np
import matplotlib.pyplot as plt
import gdstk
import time
import math 
from progressbar import *
from rdp import rdp
import argparse
from sympy import *

class teh_chin_point:
    def __init__(self) -> None:
        self.point = np.zeros(2)
        self.cosine = 0
        self.k = 0

def Chord_length(p1,p2):
    return sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2).real

'''
已知直线上的两点P1(X1,Y1) P2(X2,Y2)， P1 P2两点不重合。则直线的一般式方程AX+BY+C=0中，A B C分别等于：
A = Y2 - Y1
B = X1 - X2
C = X2*Y1 - X1*Y2
'''
def phase_function(X,Y):
    r = 46.706898 # [mm]
    x = X/r
    y = Y/r

    term1 = 0;
    term2 = 0*X;
    term3 = 1489.179649*y;
    term4 = 13.658412 * (2*(x**2 + y**2) - 1);
    term5 = 2.248171 * (x**2 - y**2);
    term6 = 0 * 2*x*y;

    Z = (term1 + term2 + term3 + term4 + term5 + term6 ) * 2*np.pi
    return Z

def get_num_phase(X_num,Y_num,Z_num,precision=0.1):
    # define function
    r = 46.706898 # [mm]
    X, Y = symbols('x, y')
    x = X/r
    y = Y/r
    term1 = 0;
    term2 = 0*X;
    term3 = 1489.179649*y;
    term4 = 13.658412 * (2*(x**2 + y**2) - 1);
    term5 = 2.248171 * (x**2 - y**2);
    term6 = 0 * 2*x*y;
    Z = (term1 + term2 + term3 + term4 + term5 + term6 ) * 2*np.pi
    dx = diff(Z,X)
    dy = diff(Z,Y)
    grad  = sqrt(dx**2 + dy**2)
    # calc cgh curve 
    # 1. define numeric x and y
    
    width = precision +1 # init width to start the loop
    n = 1
    phase = n*np.pi
    measure_point = []
    while(width>precision):
        contour = plt.contour(X_num,Y_num,Z_num,[phase])
        # randomly choose 5 measure point
        for measure in range(1,5,1):
            point = int(random() * contour.allsegs[0][0].shape[0])
            # calc the gradiant of thte measure point
            measure_point.append(np.pi / grad.subs({X:contour.allsegs[0][0][point][0],Y:contour.allsegs[0][0][point][1]})/np.pi)
        width = np.mean(measure_point)
        n = n+1
        phase = n*np.pi
        print("current width is {}, phase num is {}".format(str(width),str(n)))
        
    return n-1


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

        contour_sparse = contour.allsegs[line_index][0]
        print('sparse line points is %d ',contour_sparse.shape)

        vertex = contour_sparse*1000 # [um]
        line = gdstk.Polygon(vertex,layer=0,datatype=0)
        contour_sparse = contour.allsegs[line_index+1][0]
        vertex_out = contour_sparse*1000 # [um]
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

step = 1
# set bound manually
x = np.arange(-200,200,step)
y = np.arange(-1600,-1200,step)
X,Y = np.meshgrid(x,y)

# define function
Z = phase_function(X,Y)
Z = Z - Z.min()

num_phase = 500
# TODO : find out the right scale for Z
phase = np.linspace(np.pi,num_phase*np.pi,num_phase)
# phase = np.linspace(633e-7/2,num_phase*633e-7/2,num_phase)
contour = plt.contour(X,Y,Z,phase,colors='k')

fig = plt.figure(2)
# draw the actuall cgh surf
ax = plt.axes(projection='3d')
ax.plot_surface(X,Y,Z)
# plt.show()
# convert contour into gdsii file 
draw_gds(contour,epsilon)
