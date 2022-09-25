#导入模块
from mailbox import linesep
from pydoc import importfile
import numpy as np
import matplotlib.pyplot as plt
import gdstk
import time
import math
from progressbar import *

def draw_gds(contour):
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
        vertex = contour.allsegs[line_index][0]*1000
        line = gdstk.Polygon(vertex,layer=0,datatype=0)
        vertex_out = contour.allsegs[line_index+1][0]*1000
        line_out = gdstk.Polygon(vertex_out,layer=layer,datatype=0)
        annulus = gdstk.boolean(line_out,line, "not")
        
        main.add(annulus[0])
        layer = layer + 1
        # print("drawing curve %d/%d",line_index,len(contour.allsegs))
        

    # save file
    bar.finish()
    lib.write_gds("gds_{}.gds".format(time.strftime("%Y%m%d_%H%M",time.localtime())))

#建立步长为0.01，即每隔0.01取一个点
step = 0.01
bound = 80
x = np.arange(-bound,bound,step)
y = np.arange(-bound,bound,step)
#也可以用x = np.linspace(-10,10,100)表示从-10到10，分100份

#将原始数据变成网格数据形式
X,Y = np.meshgrid(x,y)
#写入函数，z是大写
Z = (X**2+Y**2)
#设置打开画布大小,长10，宽6
#plt.figure(figsize=(10,6))
#填充颜色，f即filled
# plt.contourf(X,Y,Z)
#画等高线
# plt.contour(X,Y,Z)
# plt.show()

#solve function
bar = ProgressBar().start()
num_phase = 1200
phase = np.linspace(np.pi,num_phase*np.pi,num_phase)
# phase = np.linspace((num_phase-1)*np.pi,num_phase*np.pi)
contour = plt.contour(X,Y,Z,phase,colors='k')
# plt.scatter(contour.allsegs[0][0][:,0],contour.allsegs[0][0][:,1])
# plt.show()
#等高线上标明z（即高度）的值，字体大小是10，颜色分别是黑色和红色
# plt.clabel(contour,fontsize=10,colors=('k'))
# plt.show()
bar.finish()
draw_gds(contour)