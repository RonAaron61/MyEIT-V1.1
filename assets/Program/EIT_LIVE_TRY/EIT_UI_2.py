import numpy as np
import serial
from time import sleep
import keyboard

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 
from pyqtgraph.console import ConsoleWidget
from pyqtgraph.dockarea.Dock import Dock
from pyqtgraph.dockarea.DockArea import DockArea

import matplotlib.pyplot as plt
from matplotlib import colors

import pyeit.eit.bp as bp
import pyeit.eit.jac as jac
import pyeit.eit.protocol as protocol
import pyeit.mesh as mesh
from pyeit.eit.fem import EITForward
from pyeit.mesh import shape, distmesh, plot_distmesh
from pyeit.mesh.wrapper import PyEITAnomaly_Circle

import EIT_Reconstruct as MyEIT
import average  #Untuk merata-rata satu data aja


"""ARDUINO"""
try:
    ser = serial.Serial('COM7', 115200)
    ser.close()
    ser.open()
    print("Connected!")
except:
    print("Please check the com")

app = pg.mkQApp("INI JUDUL")

pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', 'w')

win = QtWidgets.QMainWindow()
area = DockArea()
win.setCentralWidget(area)
win.resize(550,600)
win.setWindowTitle('EIT (BP)')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)


d1 = Dock("Main", size=(500, 270), closable=False)
d2 = Dock("Anomaly Graph", size=(500,300), closable=False)
d3 = Dock("Homogen Graph", size=(500,300), closable=False)
d4 = Dock("Status", size=(500, 100),closable=False)


area.addDock(d1)
area.addDock(d2, 'bottom', d1)
area.addDock(d3, 'bottom', d2)
area.addDock(d4, 'bottom', d3)


plotGraph_H = pg.GraphicsLayoutWidget(show=True, title="Testing")
plotH = plotGraph_H.addPlot(row=1, col=1, colspan=1,title="Homogen Data")
curve_H = plotH.plot(pen=pg.mkPen('r', width=2))
plotGraph_A = pg.GraphicsLayoutWidget(show=True, title="Testing")
plotA = plotGraph_A.addPlot(row=1, col=1, colspan=1,title="Anomaly Data")
curve_A = plotA.plot(pen=pg.mkPen('r', width=2))

Main_Info = pg.GraphicsLayoutWidget(show=True, title="Testing")
table = pg.TableWidget()


d1.addWidget(Main_Info)
d2.addWidget(plotGraph_A)
d3.addWidget(plotGraph_H)
d4.addWidget(table)

"""MAIN INFO"""
"""l1 = QLabel()
l1.setFont(QFont('Arial', 12))
l1.setText(f"MyEIT")
Main_Info.addItem(l1, row=0,col=0)"""

btn1 = QtWidgets.QPushButton("Get Homogen Data")
#btn1.setGeometry(100,100,100,100)
proxy1 = QtWidgets.QGraphicsProxyWidget()
proxy1.setWidget(btn1)
Main_Info.addItem(proxy1, row=2, col=0, colspan=2, rowspan=2)

btn2 = QtWidgets.QPushButton("Get Anomaly Data")
proxy2 = QtWidgets.QGraphicsProxyWidget()
proxy2.setWidget(btn2)
Main_Info.addItem(proxy2, row=4, col=0, colspan=2, rowspan=2)

rec_Hgn_btn = QtWidgets.QPushButton("Reconstruct With Homogen Data")
rec_proxy1 = QtWidgets.QGraphicsProxyWidget()
rec_proxy1.setWidget(rec_Hgn_btn)
Main_Info.addItem(rec_proxy1, row=6, col=0, colspan=1, rowspan=2)

rec_Ave_btn = QtWidgets.QPushButton("Reconstruct With Average Data")
rec_proxy2 = QtWidgets.QGraphicsProxyWidget()
rec_proxy2.setWidget(rec_Ave_btn)
Main_Info.addItem(rec_proxy2, row=6, col=1, colspan=1, rowspan=2)

btn3 = QtWidgets.QPushButton("Calibrate")
proxy3 = QtWidgets.QGraphicsProxyWidget()
proxy3.setWidget(btn3)
Main_Info.addItem(proxy3, row=10, col=0, colspan=2, rowspan=2)

btn4 = QtWidgets.QPushButton("Live Reconstruction (Hmg reference)")
proxy4 = QtWidgets.QGraphicsProxyWidget()
proxy4.setWidget(btn4)
Main_Info.addItem(proxy4, row=8, col=0, colspan=1, rowspan=2)

btn5 = QtWidgets.QPushButton("Live Reconstruction (Ave reference)")
proxy5 = QtWidgets.QGraphicsProxyWidget()
proxy5.setWidget(btn5)
Main_Info.addItem(proxy5, row=8, col=1, colspan=1, rowspan=2)

n_el = 16

"""PROSES AMBIL DATA"""
def Get_homogen(btn1):
    global reference
    string = "D"
    ser.write(string.encode('utf-8')) 
    reference = []
    while True:
        ser_data = ser.readline()
        ser_data = ser_data.decode().rstrip()
        if ser_data == "Done":
            break
        else:
            reference.append(float(ser_data))

    curve_H.setData(reference)
    #print(reference)
    print(f"Data Length: {len(reference)}")
    


def Get_data(btn2):
    global data
    string = "D"
    ser.write(string.encode('utf-8')) 
    data = []

    while True:
        ser_data = ser.readline()
        ser_data = ser_data.decode().rstrip()
        if ser_data == "Done":
            break
        else:
            data.append(float(ser_data))

    curve_A.setData(data)
    #print(data)
    print(f"Data Length: {len(data)}")

def Calibrate(btn3):
    string = "C"
    ser.write(string.encode('utf-8'))
    print("Electrode inject on 1-2 and read at 3-4")

    ser_data = ser.readline()
    ser_data = ser_data.decode().rstrip()
    print(ser_data)


def EIT_Reconstruct_noR(rec_Ave_btn):    
    print("Reconstruct with no homogen data (Average)")
    reconstruct = MyEIT.EIT_reconstruct(data=data, reference=[], use_ref=0, n_el=16)
    yoo = reconstruct.Reconstruct()

def EIT_Reconstruct_R(rec_Hgn_btn):  
    print("Reconstruct with homogen data")
    reconstruct = MyEIT.EIT_reconstruct(data=data, reference=reference, use_ref=1, n_el=16)
    yoo = reconstruct.Reconstruct() 

def Live_Reconstruct1(btn_4):
    def Live_Rec(data1, data2, n_el = 16):
        """Inverse Problem """
        node_ds = 192.0 * eit.solve(data1, data2, normalize=True)

        # extract node, element, alpha
        pts = mesh_obj.node
        tri = mesh_obj.element

        """ Plot Hasil """

        im = ax1.tripcolor(
            pts[:, 1],
            pts[:, 0],
            tri,
            np.real(node_ds),
            shading="flat",
            alpha=1,
            cmap=plt.cm.twilight_shifted,    #For colormap -> https://matplotlib.org/stable/gallery/color/colormap_reference.html
            norm = colors.CenteredNorm() #Biar colormap nya gk geser2
        )
        colorbar = None

        if colorbar is not None:
            colorbar.remove()
            colorbar = fig.colorbar(im)

        fig.canvas.draw()  # Update the canvas
        fig.canvas.flush_events()  # Flush the drawing queue   
        plt.show() 

    """MAIN CODE"""

    def _fd(pts):
        """shape function"""
        return shape.circle(pts, pc=[0, 0], r=1.0)

    def _fh(pts):
        """distance function"""
        r2 = np.sum(pts**2, axis=1)
        return 0.2 * (2.0 - r2)

    # build fix points, may be used as the position for electrodes
    p_fix = shape.fix_points_circle(ppl=n_el)
    # firs num nodes are the positions for electrodes
    el_pos = np.arange(n_el)

    # build triangle
    mesh_obj = mesh.create(fd=_fd, fh=_fh, p_fix=p_fix, h0=0.04)
    """lower h0 to raise the number of triangle, vice versa"""

    el_pos = mesh_obj.el_pos

    """ 1. FEM forward simulations """
    # setup EIT scan conditions
    protocol_obj = protocol.create(n_el, dist_exc=1, step_meas=1, parser_meas="std")
    print("Mesh done...")

    """ 2. naive inverse solver using back-projection """
    """BP Mehtohd"""
    eit = bp.BP(mesh_obj, protocol_obj) #Backpropagation
    eit.setup(weight="simple")  #Lebih bagus pake ini

    # extract node, element, alpha
    pts = mesh_obj.node
    tri = mesh_obj.element

    print(f"number of triangles = {str(np.size(tri, 0))}, number of nodes = {str(np.size(pts, 0))}")

    """ Plot Hasil """
    print("Plotting result...")
    #Draw the number of electrode
    def dot_num(x, y, axn, n):
        elect = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
        for i in range(len(n)):
            el2 = el_pos[i]
            el = elect[i]
            xi = x[el2, 0]
            yi = y[el2, 1]
            offset = 0.06
            if round(xi,3) > 0:
                xt = xi+offset-0.04       
            elif round(xi,3) < 0:
                xt = xi-offset
            else:
                xt = xi
            
            if round(yi,3) > 0:
                yt = yi+offset-0.04
            elif round(yi,3) < 0:
                yt = yi-offset
            else:
                yt = yi

            axn.annotate(el, xy=(xt,yt))

    # draw
    plt.ion()
    fig, ax1 = plt.subplots(1, 1, constrained_layout=True, figsize=(6, 6))

    # reconstructed
    ax1.set_title(r"Reconstituted $\Delta$ Conductivities")
    ax1.triplot(pts[:, 1], pts[:, 0], tri, linewidth=0.5) #pts[:, 1], pts[:, 0] -> kebalik urutan elekt nya #draw Lines
    ax1.plot(pts[el_pos, 1], pts[el_pos, 0], "ro")  #Draw dots
    #dot_num(pts, pts, ax2, pts[el_pos, 1])

    """NUMBERING"""
    x, y = pts[:, 1], pts[:, 0]
    for i, e in enumerate(mesh_obj.el_pos):
        ax1.annotate(str(i + 1), xy=(x[e], y[e]), color="b")

 
    fig.canvas.draw()  # Update the canvas
    fig.canvas.flush_events()  # Flush the drawing queue   
    plt.show() 
    sleep(2)

    """ 3. Input Data """
    #Use existing reference data
    referenceData = np.array(reference)

    print("FIRST")
    live_r = 1
    while True:
        Get_data(True)
        Live_Rec(data1=data, data2=referenceData)
        print(f"data: {live_r}")
        live_r += 1
        if keyboard.is_pressed('q'):
            print("Loop terminated by user.")
            break

    print("Test Done!")
    plt.show(block=True)

"""LIVE RECOBNSTRUCTION USING AVERAGE DATA AS THE REFERENCE DATA"""
def Live_Reconstruct2(btn_5):
    def Live_Rec(data1, n_el = 16):
        """Inverse Problem """
        data2 = average.ave(data=data1, n_elec=n_el)
        node_ds = 192.0 * eit.solve(data1, data2, normalize=True)

        # extract node, element, alpha
        pts = mesh_obj.node
        tri = mesh_obj.element

        """ Plot Hasil """
        im = ax1.tripcolor(
            pts[:, 1],
            pts[:, 0],
            tri,
            np.real(node_ds),
            shading="flat",
            alpha=1,
            cmap=plt.cm.twilight_shifted,    #For colormap -> https://matplotlib.org/stable/gallery/color/colormap_reference.html
            norm = colors.CenteredNorm() #Biar colormap nya gk geser2
        )
        colorbar = None

        if colorbar is not None:
            colorbar.remove()
            colorbar = fig.colorbar(im)

        fig.canvas.draw()  # Update the canvas
        fig.canvas.flush_events()  # Flush the drawing queue   
        plt.show() 

    """MAIN CODE"""
    def _fd(pts):
        """shape function"""
        return shape.circle(pts, pc=[0, 0], r=1.0)

    def _fh(pts):
        """distance function"""
        r2 = np.sum(pts**2, axis=1)
        return 0.2 * (2.0 - r2)

    # build fix points, may be used as the position for electrodes
    p_fix = shape.fix_points_circle(ppl=n_el)
    # firs num nodes are the positions for electrodes
    el_pos = np.arange(n_el)

    # build triangle
    mesh_obj = mesh.create(fd=_fd, fh=_fh, p_fix=p_fix, h0=0.04)
    """lower h0 to raise the number of triangle, vice versa"""

    el_pos = mesh_obj.el_pos

    """ 1. FEM forward simulations """
    # setup EIT scan conditions
    protocol_obj = protocol.create(n_el, dist_exc=1, step_meas=1, parser_meas="std")
    print("Mesh done...")

    """ 2. naive inverse solver using back-projection """
    """BP Mehtohd"""
    eit = bp.BP(mesh_obj, protocol_obj) #Backpropagation
    eit.setup(weight="simple")  #Lebih bagus pake ini

    # extract node, element, alpha
    pts = mesh_obj.node
    tri = mesh_obj.element

    print(f"number of triangles = {str(np.size(tri, 0))}, number of nodes = {str(np.size(pts, 0))}")

    """ Plot Hasil """
    print("Plotting result...")
    #Draw the number of electrode
    def dot_num(x, y, axn, n):
        elect = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
        for i in range(len(n)):
            el2 = el_pos[i]
            el = elect[i]
            xi = x[el2, 0]
            yi = y[el2, 1]
            offset = 0.06
            if round(xi,3) > 0:
                xt = xi+offset-0.04       
            elif round(xi,3) < 0:
                xt = xi-offset
            else:
                xt = xi
            
            if round(yi,3) > 0:
                yt = yi+offset-0.04
            elif round(yi,3) < 0:
                yt = yi-offset
            else:
                yt = yi

            axn.annotate(el, xy=(xt,yt))

    # draw
    plt.ion()
    fig, ax1 = plt.subplots(1, 1, constrained_layout=True, figsize=(6, 6))

    # reconstructed
    ax1.set_title(r"Reconstituted $\Delta$ Conductivities")
    ax1.triplot(pts[:, 1], pts[:, 0], tri, linewidth=0.5) #pts[:, 1], pts[:, 0] -> kebalik urutan elekt nya #draw Lines
    ax1.plot(pts[el_pos, 1], pts[el_pos, 0], "ro")  #Draw dots
    #dot_num(pts, pts, ax2, pts[el_pos, 1])

    """NUMBERING"""
    x, y = pts[:, 1], pts[:, 0]
    for i, e in enumerate(mesh_obj.el_pos):
        ax1.annotate(str(i + 1), xy=(x[e], y[e]), color="b")

 
    fig.canvas.draw()  # Update the canvas
    fig.canvas.flush_events()  # Flush the drawing queue   
    plt.show() 
    sleep(2)

    print("Live Reconstruction Start!")
    live_r = 1
    while True:
        Get_data(True)
        Live_Rec(data1=data)
        print(f"data: {live_r}")
        live_r += 1
        if keyboard.is_pressed('q'):
            print("Loop terminated by user.")
            break

    print("Test Done!")
    plt.show(block=True)

rec_Ave_btn.clicked.connect(EIT_Reconstruct_noR)
rec_Hgn_btn.clicked.connect(EIT_Reconstruct_R)
btn1.clicked.connect(Get_homogen)
btn2.clicked.connect(Get_data)
btn3.clicked.connect(Calibrate)
btn4.clicked.connect(Live_Reconstruct1)
btn5.clicked.connect(Live_Reconstruct2)

win.show()

if __name__ == '__main__':
    pg.exec()