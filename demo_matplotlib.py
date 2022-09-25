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

step = 0.01
bound = 80
x = np.arange(-bound,bound,step)
y = np.arange(-bound,bound,step)
X,Y = np.meshgrid(x,y)

# define function
Z = (X**2+Y**2)

#solve function
bar = ProgressBar().start()
num_phase = 1200
phase = np.linspace(np.pi,num_phase*np.pi,num_phase)
contour = plt.contour(X,Y,Z,phase,colors='k')
bar.finish()
draw_gds(contour)