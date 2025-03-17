#!/usr/bin/env python3
#
#  plotter_oop_numpy_v5.py
#  
#  Copyright 2025 nap0
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import tkinter
from tkinter import ttk
import os
import sys
import csv
from tkinter import colorchooser,simpledialog,filedialog
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib import cm
from numpy import *
from scipy.optimize import root_scalar
from scipy.integrate import quad


# Class for the application derived from tkinter.Tk
class Plotter(tkinter.Tk): 
    def __init__(self): 
        super().__init__() # call init from parent class
        self.title("Plotter using Matplotlib in Tkinter")
        self.resizable(width=True,height=True)
        self.geometry("1100x750") # afmetingen voor start
        self.configure(bg='#A0A0A0')
        
        # instance variables
        
        self.invphi = (sqrt(5) - 1) / 2  # 1 / phi # constant for numeric method
        
        self.initexpr = "x" # expression to be plotted, a simple "x" at startup
        self.tstart = -1.0 # startvalue for x
        self.tstop = 1.0 # endvalue for x
        self.N = 1000 # number of values in plot
        self.linethickness = 2 # line thickness used for plot
        self.fontsize = 15
        self.xymode = tkinter.BooleanVar() # mode voor xy plot
        self.xymode.set(False)
        self.polarmode = tkinter.BooleanVar() # mode voor polar plot
        self.polarmode.set(False)
        self.line3dmode = tkinter.BooleanVar() # mode voor 3d line plot
        self.line3dmode.set(False)
        self.surface3dmode = tkinter.BooleanVar() # mode voor 3d surface plot
        self.surface3dmode.set(False)
        
        
        # set behaviour at resizing for the various grid rows and column
        self.rowconfigure(0, weight = 3)
        self.rowconfigure(1, weight = 0)
        self.rowconfigure(2, weight = 0)
        self.rowconfigure(3, weight = 0)
        self.rowconfigure(4, weight = 0)
        self.columnconfigure(0, weight = 1)
        
        # define Figure object from Matplotlib and set background color
        self.fig = Figure()
        self.fig.patch.set_facecolor('#ffffff')
        
        # generate a plot from the Fifure object - Matplotlib
        self.ax = self.fig.add_subplot()  
        
        # generate a canvas object from Matplotlib with the Figure object 
        # from matplotlib and the Tk object from Tkinter as argument
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        self.canvas.get_tk_widget().configure(background='#ffffff')
        self.canvas.draw()        
        
        # define menus - Tkinter
        self.menubar=tkinter.Menu(self,background="#A0A0A0", fg="#000000",font=("FreeSans",11,"bold"))
        self.menufile=tkinter.Menu(self.menubar,tearoff=0,background="#A0A0A0", fg="#000000",font=("calibri",11,"bold"))
        self.menufile.add_command(label="Save as CSV",command=self.saveascsv)
        self.menufile.add_command(label="Save as image",command=self.saveasimg)
        self.menufile.add_separator()
        self.menufile.add_command(label="Exit",command=self.destroy)
        self.menubar.add_cascade(label="File",menu=self.menufile)
        self.menutools=tkinter.Menu(self.menubar,tearoff=0,background="#A0A0A0", fg="#000000",font=("FreeSans",11,"bold"))
        self.menutools.add_command(label="Find root",command=self.findroot)
        self.menutools.add_command(label="Find maximum",command=self.findmaximum)
        self.menutools.add_command(label="Find minimum",command=self.findminimum)
        self.menutools.add_command(label="Integrate",command=self.findintegralscipyquad)        
        self.menubar.add_cascade(label="Tools",menu=self.menutools)
        self.menusettings=tkinter.Menu(self.menubar,tearoff=0,background="#A0A0A0", fg="#000000",font=("FreeSans",11,"bold"))
        self.menusettings.add_command(label="Number of points",command=self.setnumberofpoints)
        self.menusettings.add_separator()
        self.submenucolors=tkinter.Menu(self.menusettings,tearoff=0,background="#A0A0A0", fg="#000000",font=("FreeSans",11,"bold"))
        self.submenucolors.add_command(label="Line color",command=self.setlinecolor)
        self.submenucolors.add_command(label="Label color",command=self.setlabelcolor)
        self.submenucolors.add_command(label="Grid color",command=self.setgridcolor)
        self.submenucolors.add_command(label="Axis color",command=self.setaxiscolor)
        self.submenucolors.add_command(label="Plot background color",command=self.setplotbackgroundcolor)
        self.submenucolors.add_command(label="Background color",command=self.setbackgroundcolor)
        self.menusettings.add_cascade(label="Set colors", menu=self.submenucolors)
        self.menusettings.add_command(label="Line thickness", command=self.setlinethickness)
        self.menusettings.add_command(label="Font size",command=self.setfontsize)
        self.menusettings.add_separator()
        self.menusettings.add_checkbutton(label="x y plot", onvalue=1, offvalue=0, variable=self.xymode, command=self.update)
        self.menusettings.add_checkbutton(label="polar plot (experimental)", onvalue=1, offvalue=0, variable=self.polarmode, command=self.update)
        self.menusettings.add_checkbutton(label="3D line plot (experimental)", onvalue=1, offvalue=0, variable=self.line3dmode, command=self.update)
        self.menusettings.add_checkbutton(label="3D surface plot (experimental)", onvalue=1, offvalue=0, variable=self.surface3dmode, command=self.update)
        self.menubar.add_cascade(label="Settings",menu=self.menusettings)
        self.menuexamples=tkinter.Menu(self.menubar,tearoff=0,background="#A0A0A0", fg="#000000",font=("FreeSans",11,"bold"))
        self.menuexamples.add_command(label="Sinc",command=lambda: self.plotfunction("sinc(x)","-6","6",False,False,False,False))
        self.menuexamples.add_command(label="Wavelet",command=lambda: self.plotfunction("exp(-x**2)*sin(pi*x*4)","-e","e",False,False,False,False))
        self.menuexamples.add_command(label="Oscillation",command=lambda: self.plotfunction("(x>0)*exp(-x/3)*sin(2*pi*x)","-1","10",False,False,False,False))
        self.menuexamples.add_command(label="Polynomial",command=lambda: self.plotfunction("x**3-15*x+3","-5","5",False,False,False,False))
        self.menuexamples.add_command(label="Beat frequency",command=lambda: self.plotfunction("sin(x)+sin(1.1*x)","-pi*20","pi*20",False,False,False,False))
        self.menuexamples.add_command(label="Catenary",command=lambda: self.plotfunction("2*cosh(x/2)","-2","2",False,False,False,False))
        self.menuexamples.add_command(label="Phase control",command=lambda: self.plotfunction("((x%1)>.3)*sin(pi*x)","-2","2",False,False,False,False))
        self.menuexamples.add_separator()
        self.menuexamples.add_command(label="Lissajous",command=lambda: self.plotfunction("sin(3*x),cos(5*x)","-pi","pi",True,False,False,False))
        self.menuexamples.add_separator()
        self.menuexamples.add_command(label="Polar rose",command=lambda: self.plotfunction("2*sin(4*x)","0","pi*2",False,True,False,False))
        self.menuexamples.add_separator()
        self.menuexamples.add_command(label="3D lissajous",command=lambda: self.plotfunction("cos(x),-sin(x/3),sin(x)","-pi*3","pi*3",False,False,True,False))
        self.menuexamples.add_command(label="3D spiral",command=lambda: self.plotfunction("x*cos(x),x*sin(x),sqrt(x)","0","pi*12",False,False,True,False))
        self.menuexamples.add_command(label="3D wave",command=lambda: self.plotfunction("sin(6*x)*exp(-x**2/20),cos(6*x)*exp(-x**2/20),x","-10","10",False,False,True,False))
        self.menuexamples.add_command(label="3D sphere",command=lambda: self.plotfunction("sqrt(100-x**2)*sin(6*x),sqrt(100-x**2)*cos(6*x),x","-10","10",False,False,True,False))
        self.menuexamples.add_separator()
        self.menuexamples.add_command(label="3D surface sinc",command=lambda: self.plotfunction("sinc(sqrt(x**2+y**2))","-3","3",False,False,False,True))
        self.menuexamples.add_command(label="3D surface dome",command=lambda: self.plotfunction("-2*cosh(sqrt(x**2+y**2)/2)","-1","1",False,False,False,True))
        self.menuexamples.add_command(label="3D surface wave",command=lambda: self.plotfunction("sin(x)*cos(y)","-pi","pi",False,False,False,True))
        self.menubar.add_cascade(label="Examples",menu=self.menuexamples)
        self.menuranges=tkinter.Menu(self.menubar,tearoff=0,background="#A0A0A0", fg="#000000",font=("FreeSans",11,"bold"))
        self.menuranges.add_command(label="-1.0 .. 1.0",command=lambda: self.setrange("-1.0","1.0"))
        self.menuranges.add_command(label="0 .. 1.0",command=lambda: self.setrange("0","1.0"))
        self.menuranges.add_command(label="-10.0 .. 10.0",command=lambda: self.setrange("-10.0","10.0"))
        self.menuranges.add_command(label="0 .. 10.0",command=lambda: self.setrange("0","10.0"))
        self.menuranges.add_command(label="-pi .. pi",command=lambda: self.setrange("-pi","pi"))
        self.menuranges.add_command(label="-2.*pi .. 2*pi",command=lambda: self.setrange("-2.0*pi","2.0*pi"))
        self.menubar.add_cascade(label="X ranges",menu=self.menuranges)
        self.menucolorpreset=tkinter.Menu(self.menubar,tearoff=0,background="#A0A0A0", fg="#000000",font=("FreeSans",11,"bold"))
        self.menucolorpreset.add_command(label="Greys",command=lambda: self.presetcolor())
        self.menucolorpreset.add_command(label="Blues",command=lambda: self.presetcolor(linecolor="#666eff",axiscolor="#2671e8",labelcolor="#2671e8", \
            gridcolor="#462ab4",plotbackgroundcolor="#10100b",backgroundcolor="#000000", colormap=cm.Blues_r))
        self.menucolorpreset.add_command(label="Greens",command=lambda: self.presetcolor(linecolor="#49ff3c",axiscolor="#bcd308",labelcolor="#bcd308", \
            gridcolor="#bcd308",plotbackgroundcolor="#303030",backgroundcolor="#303030", colormap=cm.Greens_r))
        self.menucolorpreset.add_command(label="Reds",command=lambda: self.presetcolor(linecolor="#e36853",axiscolor="#d15e31",labelcolor="#d15e31", \
            gridcolor="#a92c2c",plotbackgroundcolor="#000000",backgroundcolor="#2c080e", colormap=cm.Reds_r))
        self.menucolorpreset.add_command(label="Blue on white",command=lambda: self.presetcolor(linecolor="#03007B",axiscolor="#6967CC",labelcolor="#6967CC", \
            gridcolor="#9D9BD5",plotbackgroundcolor="#FFFFFF",backgroundcolor="#D0CFEE", colormap=cm.Blues))
        self.menubar.add_cascade(label="Color presets",menu=self.menucolorpreset)
        self.config(menu=self.menubar)        
        
        
        # ttk styles 
        self.stylebutton=ttk.Style()
        self.stylebutton.configure("TButton",font=("FreeSans",11,"bold"),background="#A0A0A0",foreground="#000000")
        self.stylelabel=ttk.Style()
        self.stylelabel.configure("TLabel",font=("FreeSans",11,"bold"),background="#A0A0A0",foreground="#000000")
        self.styleframe=ttk.Style()
        self.styleframe.configure("TFrame",font=("FreeSans",11,"bold"),background="#A0A0A0",foreground="#000000")
               
        # Frames - ttk Tkinter
        self.framecontrols=ttk.Frame(master=self)
        self.framecontrols.rowconfigure(0, weight = 1)
        self.framecontrols.columnconfigure(0, weight = 1)
        self.framecontrols.columnconfigure(1, weight = 1)
        self.framecontrols.columnconfigure(2, weight = 1)
        self.framecontrols.columnconfigure(3, weight = 1)
        self.framecontrols.columnconfigure(4, weight = 1)
        self.framecontrols.columnconfigure(5, weight = 1)
        self.frameentries=ttk.Frame(master=self)
        self.frameentries.rowconfigure(0, weight = 1)
        self.frameentries.columnconfigure(0, weight = 0)
        self.frameentries.columnconfigure(1, weight = 0)
        self.frameentries.columnconfigure(2, weight = 3)
        self.framefunbuttons=ttk.Frame(master=self)
        self.framefunbuttons.rowconfigure(0, weight = 1)
        
        # entries - ttk
        self.entryxstart=tkinter.Entry(self.frameentries, width=14,font=("FreeMono",13,"bold"),insertwidth=2)
        self.entryxstart.config({"background": "#303030","foreground": "#ffffff","insertbackground": "#ffffff"})
        self.entryxstop=tkinter.Entry(self.frameentries, width=14,font=("FreeMono",13,"bold"),insertwidth=2)
        self.entryxstop.config({"background": "#303030","foreground": "#ffffff","insertbackground": "#ffffff"})
        self.entryexpr =tkinter.Entry(self.frameentries, width=45,font=("FreeMono",13,"bold"),insertwidth=2)
        self.entryexpr.config({"background": "#303030","foreground": "#ffffff","insertbackground": "#ffffff"})
        self.entryexpr.insert(tkinter.END, self.initexpr)
        
        # labels - ttk
        self.label_xstart=ttk.Label(master=self.frameentries,text="Start")
        self.label_xstop=ttk.Label(master=self.frameentries,text="Stop")
        self.label_expr=ttk.Label(master=self.frameentries,text="Expression f(x) = ")
        
        # buttons - ttk
        self.button_quit = ttk.Button(master=self.framecontrols, width=13, text="Quit", command=self.destroy)
        self.button_plot = ttk.Button(master=self.framecontrols, width=13, text="Plot", command=self.update)
        self.button_zoomout=ttk.Button(master=self.framecontrols, width=13, text="Zoom out", command=self.zoomout)
        self.button_zoomin=ttk.Button(master=self.framecontrols, width=13, text="Zoom in", command=self.zoomin)
        self.button_panleft=ttk.Button(master=self.framecontrols, width=13, text="<<", command=self.panleft)
        self.button_panright=ttk.Button(master=self.framecontrols, width=13, text=">>", command=self.panright)            
        
        
        # align widgets using grid() - ttk
        # canvas
        self.canvas.get_tk_widget().grid(row = 0, column = 0, sticky="WENS")
        # frame for function buttons
        self.framefunbuttons.grid(row=1,column=0, sticky="WENS")
        # frame for entries and labels
        self.frameentries.grid(row=2,column=0, sticky="WENS")
        self.label_xstart.grid(row=1,column=0, padx=10, sticky="W")
        self.label_xstop.grid(row=1,column=1, padx=10, sticky="W")
        self.label_expr.grid(row=1,column=2, padx=10, sticky="W")
        self.entryxstart.grid(row=2, column=0, sticky="W")
        self.entryxstop.grid(row=2, column=1, sticky="W")
        self.entryexpr.grid(row = 2, column = 2, sticky="WENS")
        # frame for control buttons
        self.framecontrols.grid(row = 3, column = 0, sticky="WENS")
        self.button_quit.grid(row = 0, column = 0, sticky="WENS")
        self.button_panleft.grid(row = 0, column = 1, sticky="WENS")
        self.button_zoomout.grid(row = 0, column = 2, sticky="WENS")
        self.button_zoomin.grid(row = 0, column = 3, sticky="WENS")
        self.button_panright.grid(row = 0, column = 4, sticky="WENS")
        self.button_plot.grid(row = 0, column = 5, sticky="WENS")
        
        # define function buttons, align using grid() and set columnconfigure
        mathfunctions=("sin","cos","tan","sinc","sinh","cosh","tanh","exp","log","log10","sign","sqrt")
        for n,fun in enumerate(mathfunctions):
            b=ttk.Button(master=self.framefunbuttons, width=6, text=fun,
                    command=lambda fun=fun: self.insertfunction(fun) )
            b.grid(row=0, column=n, sticky="WENS")
            self.framefunbuttons.columnconfigure(n, weight = 1)
        
        
        # keyboard events binding
        self.bind('<KeyRelease>',self.key_released )
        
        # fill in values for start and stop
        self.updatestartstoptxtbox()
        
        # set colors        
        self.presetcolor()   
    
    
    # add function to expression when a function button is clicked
    def insertfunction(self,fun):
        self.entryexpr.insert( tkinter.INSERT, fun + "(" )
        self.entryexpr.insert( tkinter.END, ")" )
           
        
    # zoom out plot, update values for tstart and tstop
    # remake plot with the new values
    def zoomout(self):        
        self.tspan=self.tstop-self.tstart
        self.tstart=self.tstart-self.tspan
        self.tstop=self.tstop+self.tspan     
        self.updatestartstoptxtbox()
        self.update()
        
        
    # zoom in plot, update values for tstart and tstop
    # remake plot with the new values
    def zoomin(self):
        self.tspan=self.tstop-self.tstart
        self.tstart=self.tstart+self.tspan/3
        self.tstop=self.tstop-self.tspan/3     
        self.updatestartstoptxtbox()
        self.update()
    
    # pan left plot, update values for tstart and tstop
    # remake plot with the new values
    def panleft(self):
        self.tspan=self.tstop-self.tstart
        self.tstart=self.tstart-self.tspan/4
        self.tstop=self.tstop-self.tspan/4      
        self.updatestartstoptxtbox()
        self.update()

    # pan right plot, update values for tstart and tstop
    # remake plot with the new values
    def panright(self):
        self.tspan=self.tstop-self.tstart
        self.tstart=self.tstart+self.tspan/4
        self.tstop=self.tstop+self.tspan/4   
        self.updatestartstoptxtbox()
        self.update()
        
           
    # round floating point value and convert to scietific notation, output is str
    def roundvaluestr(self, x, decimals ):
        sci=f"{x:e}"
        mantissastr,exponentstr=sci.split("e")
        mantissa=round(float(mantissastr),decimals)
        exponent=int(exponentstr)
        if (exponent!=0):
            scistr=f"{mantissa}E{exponent:+03d}"  
        else:
            scistr=f"{mantissa}"
        return scistr
    
        
    # update values of tstart en tstop entry boxes
    def updatestartstoptxtbox(self):
        self.entryxstart.delete(0, 'end')
        self.entryxstart.insert(tkinter.END,self.roundvaluestr(self.tstart,8))
        self.entryxstop.delete(0, 'end')
        self.entryxstop.insert(tkinter.END,self.roundvaluestr(self.tstop,8))
        

    # evaluate expression self.txt with values in ndarray x and optionally y
    def evalexpression(self,x,y=0):
        waarde=eval(self.txt)
        return waarde

    
    # make a plot of function f(x) 
    def plotfx(self,fillstart=0.0,fillstop=1.0,fillshow=False):
        
        if type(self.y) is not ndarray:
            waarde=self.y
            self.y=empty(self.N)
            self.y.fill(waarde)
        
        self.fig.delaxes(self.ax) 
         
        # new rectilinear plot generated on Figure object          
        self.ax = self.fig.add_subplot(projection='rectilinear') 
        
        # generate plot via matplotlib plot() function
        # values in self.y plotted in fucntion of values self.t
        self.line = self.ax.plot(self.t, self.y, color=self.linecolor, linewidth=self.linethickness)
        
        # set colors and text on the plot
        title="f(x)="+self.txt
        self.ax.set_ylabel("f(x)", fontsize = self.fontsize) # Y label
        self.ax.set_xlabel("x", fontsize = self.fontsize) # X label
        self.ax.grid(color = self.gridcolor, linewidth = 0.5)
        self.ax.set_title(title,fontweight="bold", size=self.fontsize, color=self.linecolor) # Title
        self.ax.set_facecolor(self.plotbackgroundcolor)
        self.fig.set_facecolor(self.backgroundcolor)
        self.ax.xaxis.label.set_color(self.labelcolor)
        self.ax.yaxis.label.set_color(self.labelcolor)
        self.ax.tick_params(axis='x', colors=self.axiscolor)
        self.ax.tick_params(axis='y', colors=self.axiscolor)
        self.ax.spines['left'].set_color(self.axiscolor)
        self.ax.spines['bottom'].set_color(self.axiscolor)
        self.ax.spines['top'].set_color(self.axiscolor)
        self.ax.spines['right'].set_color(self.axiscolor)
        self.ax.xaxis.set_tick_params(labelsize=self.fontsize)
        self.ax.yaxis.set_tick_params(labelsize=self.fontsize)
        
        # when calculating integral
        if fillshow:
            self.ax.fill_between(self.t, self.y, where=((self.t > fillstart) & (self.t < fillstop)))
        
        # update canvas
        self.canvas.draw()
        
    # plot y(t) in function of x(t)
    def plotxy(self):
        
        # matplotlib plot delete 
        self.fig.delaxes(self.ax)     
        
        # new rectilinear plot generated on Figure object          
        self.ax = self.fig.add_subplot(projection='rectilinear')          
                
        # self.y is tuple of 2 numpy.ndarray
        xx,yy,*other = self.y    
                
        if type(xx) is not ndarray:
            waarde=xx
            xx=empty(self.N)
            xx.fill(waarde)
            
        if type(yy) is not ndarray:
            waarde=yy
            yy=empty(self.N)
            yy.fill(waarde)

        
        # plot generated using matplotlib plot() function
        # values in yy plotted in function off xx
        self.line = self.ax.plot(xx, yy, color=self.linecolor, linewidth=self.linethickness)
       
        # set coloers and text on plot
        txts=self.txt.split(",") # seperate 2 strings
        title=txts[1]+" vs "+txts[0]        
        self.ax.set_ylabel(txts[1], fontsize = self.fontsize) # Y label
        self.ax.set_xlabel(txts[0], fontsize = self.fontsize) # X label
        self.ax.grid(color = self.gridcolor, linewidth = 0.5)
        self.ax.set_title(title,fontweight="bold", size=self.fontsize, color=self.linecolor) # Title
        self.ax.set_facecolor(self.plotbackgroundcolor)
        self.fig.set_facecolor(self.backgroundcolor)
        self.ax.xaxis.label.set_color(self.labelcolor)
        self.ax.yaxis.label.set_color(self.labelcolor)
        self.ax.tick_params(axis='x', colors=self.axiscolor)
        self.ax.tick_params(axis='y', colors=self.axiscolor)
        self.ax.spines['left'].set_color(self.axiscolor)
        self.ax.spines['bottom'].set_color(self.axiscolor)
        self.ax.spines['top'].set_color(self.axiscolor)
        self.ax.spines['right'].set_color(self.axiscolor)
        self.ax.xaxis.set_tick_params(labelsize=self.fontsize)
        self.ax.yaxis.set_tick_params(labelsize=self.fontsize)
        
        # canvas and toolbar updated
        self.canvas.draw()
        
    def plot3dsurface(self):
        # matplotlib plot deleted
        self.fig.delaxes(self.ax)       
        
        if type(self.y) is not ndarray:
            Number=int(sqrt(self.N))
            waarde=self.y
            self.y=empty((Number,Number))
            self.y.fill(waarde)
        
        # surface plot generated    
        self.ax = self.fig.add_subplot(projection='3d') 
        self.ax.plot_surface(self.v , self.w , self.y, \
            cmap=self.colormap)

        # set colors and text
        title=self.txt
        self.ax.xaxis.set_pane_color(self.plotbackgroundcolor)
        self.ax.yaxis.set_pane_color(self.plotbackgroundcolor)
        self.ax.zaxis.set_pane_color(self.plotbackgroundcolor)
        self.ax.xaxis._axinfo['grid']['color'] = self.gridcolor
        self.ax.yaxis._axinfo['grid']['color'] = self.gridcolor
        self.ax.zaxis._axinfo['grid']['color'] = self.gridcolor
        self.ax.xaxis._axinfo['axisline']['color'] = self.gridcolor
        self.ax.yaxis._axinfo['axisline']['color'] = self.gridcolor
        self.ax.zaxis._axinfo['axisline']['color'] = self.gridcolor
        self.ax.set_title(title,fontweight="bold", size=self.fontsize, color=self.linecolor) # Title
        self.ax.set_facecolor(self.backgroundcolor)
        self.fig.set_facecolor(self.backgroundcolor)
        self.ax.xaxis.label.set_color(self.labelcolor)
        self.ax.yaxis.label.set_color(self.labelcolor)
        self.ax.zaxis.label.set_color(self.labelcolor)
        self.ax.tick_params(axis='x', colors=self.axiscolor)
        self.ax.tick_params(axis='y', colors=self.axiscolor)
        self.ax.tick_params(axis='z', colors=self.axiscolor)
        self.ax.xaxis.set_tick_params(labelsize=self.fontsize)
        self.ax.yaxis.set_tick_params(labelsize=self.fontsize)
        self.ax.zaxis.set_tick_params(labelsize=self.fontsize)
        
        # canvas en toolbar updaten
        self.canvas.draw()


    # plot 3D line    
    def plot3dline(self):
        # matplotlib plot deleted 
        self.fig.delaxes(self.ax)    
        self.ax = self.fig.add_subplot(projection='3d') 
        
        # self.y is tuple of 3 numpy ndarray
        xx,yy,zz,*other = self.y  
        
        if type(xx) is not ndarray:
            waarde=xx
            xx=empty(self.N)
            xx.fill(waarde)
        if type(yy) is not ndarray:
            waarde=yy
            yy=empty(self.N)
            yy.fill(waarde)      
        if type(zz) is not ndarray:
            waarde=zz
            zz=empty(self.N)
            zz.fill(waarde)

        # plot the line using 3 ndarrays
        self.ax.plot(xx, yy, zz, color=self.linecolor, linewidth=self.linethickness)
        
        # set colors and text
        title=self.txt
        self.ax.xaxis.set_pane_color(self.plotbackgroundcolor)
        self.ax.yaxis.set_pane_color(self.plotbackgroundcolor)
        self.ax.zaxis.set_pane_color(self.plotbackgroundcolor)
        self.ax.xaxis._axinfo['grid']['color'] = self.gridcolor
        self.ax.yaxis._axinfo['grid']['color'] = self.gridcolor
        self.ax.zaxis._axinfo['grid']['color'] = self.gridcolor
        self.ax.xaxis._axinfo['axisline']['color'] = self.gridcolor
        self.ax.yaxis._axinfo['axisline']['color'] = self.gridcolor
        self.ax.zaxis._axinfo['axisline']['color'] = self.gridcolor
        self.ax.set_title(title,fontweight="bold", size=self.fontsize, color=self.linecolor) # Title
        self.ax.set_facecolor(self.backgroundcolor)
        self.fig.set_facecolor(self.backgroundcolor)
        self.ax.xaxis.label.set_color(self.labelcolor)
        self.ax.yaxis.label.set_color(self.labelcolor)
        self.ax.zaxis.label.set_color(self.labelcolor)
        self.ax.tick_params(axis='x', colors=self.axiscolor)
        self.ax.tick_params(axis='y', colors=self.axiscolor)
        self.ax.tick_params(axis='z', colors=self.axiscolor)
        self.ax.xaxis.set_tick_params(labelsize=self.fontsize)
        self.ax.yaxis.set_tick_params(labelsize=self.fontsize)
        self.ax.zaxis.set_tick_params(labelsize=self.fontsize)
        
        # canvas en toolbar updated
        self.canvas.draw()

        
    # POLAR plot 
    def plotpolar(self):
        
        if type(self.y) is not ndarray:
            waarde=self.y
            self.y=empty(self.N)
            self.y.fill(waarde)
        
        # adapt data because matplotlib does not plot negative r values
        # on the negative siden of the origin
        # add pi radials for the points for which r < 0
        # then replace r with it's absolute value
        def modifyforpolar(r,theta): # this function adds pi to theta if r<0, then returns theta
            if r<0:
                theta+=pi
            return(theta)
        
        # apply modifyforpolar on all values in self.t toepassen  
        thetamod=list(map(modifyforpolar,self.y,self.t))
        
        # using map() take absolute value of rfor all points
        rmod=list(map(abs,self.y))
        
        # matplotlib plot deleted 
        self.fig.delaxes(self.ax)
        
        # create new polar plot on Figure object                  
        self.ax = self.fig.add_subplot(projection='polar') 
        
        # generate plot via matplotlib plot() 
        # plot rmod in function of thetamod 
        self.line = self.ax.plot(thetamod, rmod, color=self.linecolor, linewidth=self.linethickness)
        
        # set colors and text
        title="r(x)="+self.txt
        self.ax.grid(color = self.gridcolor, linewidth = 0.5)
        self.ax.set_title(title,fontweight="bold", size=self.fontsize, color=self.linecolor) # Title
        self.ax.set_facecolor(self.plotbackgroundcolor)
        self.fig.set_facecolor(self.backgroundcolor)
        self.ax.xaxis.label.set_color(self.labelcolor)
        self.ax.yaxis.label.set_color(self.labelcolor)
        self.ax.tick_params(axis='x', colors=self.axiscolor)
        self.ax.tick_params(axis='y', colors=self.axiscolor)
        self.ax.xaxis.set_tick_params(labelsize=self.fontsize)
        self.ax.yaxis.set_tick_params(labelsize=self.fontsize)
        
        # canvas en toolbar updated
        self.canvas.draw()
        
        
        
    # generate numpy array self.t represnting x waarden for function
    # calculate values for new plot in numpy array self.y
    # generate a new plot using self.plotfx() or self.plotxy() or self.plotpolar()
    def update(self):
        
        # get values xstart and xstop out of entry boxes and convert them
        # to numbers with error handling
        self.txt=self.entryexpr.get()
        try:
            self.tstart=eval(self.entryxstart.get())
            self.tstop=eval(self.entryxstop.get())        
        except:
            tkinter.messagebox.showerror("Error","Interval not correct")
            self.updatestartstoptxtbox() # change entry boxec to previous values and continue
        
        if "y" in self.txt:
            self.surface3dmode.set(True)        
        
        if self.surface3dmode.get():
            Number=int(sqrt(self.N))
            self.t = linspace( self.tstart , self.tstop , Number )
            self.v,self.w = meshgrid(self.t, self.t)

        else:
            # numpy array self.t generated using numpy.linspace()
            self.t = linspace( self.tstart , self.tstop , self.N )
        
        # numpy array self.y generated by applying evalexpression() on every 
        # value of numpy array t using map()
        # error handling for errors which make further calculatons useless
        if self.surface3dmode.get():
            try:        
                self.y = self.evalexpression( self.v , self.w )
            except (SyntaxError,NameError,TypeError) as inst:     
                tkinter.messagebox.showerror("Function not correct",inst.args[0])
                return(False) # False returned when error    
        else:
            try:        
                self.y = self.evalexpression( self.t )
            except (SyntaxError,NameError,TypeError) as inst:     
                tkinter.messagebox.showerror("Function not correct",inst.args[0])
                return(False) # False returned when error 
        
        # when 1 "," is present in the function self.txt it contains 2 functions for xy plot    
        # when 2 ","are present it is an 3D line plot
        match self.txt.count(","):
            case 0:
                self.xymode.set(False)
                self.line3dmode.set(False)
            case 1:
                self.xymode.set(True)
                self.line3dmode.set(False)
                self.surface3dmode.set(False)
            case 2:
                self.xymode.set(False)
                self.line3dmode.set(True)
                self.surface3dmode.set(False)
                
                    
        # plotten, type of plot depends on tkinter booleans self.polarmode and self.xymode
        if self.surface3dmode.get():
            self.plot3dsurface()
        elif self.polarmode.get():
            self.plotpolar()
        elif self.xymode.get():
            self.plotxy()
        elif self.line3dmode.get():
            self.plot3dline()
        else:
            self.plotfx()        
        
        return(True) # True returned when all is ok
        
    # doe a and b have same sign, True of False
    # funktion used by numerical method
    def signissame(self,a,b):
        if(a>=0) and (b>=0):
            return(True)
        elif(a<0) and (b<0):
            return(True)
        else:
            return(False)

            
    # find root of function using extra window of class self.findnumericwindow
    def findroot(self):
        # self.update() returns False in case of error in fucntion 
        # check if a toplevel window is not opened yet using self.get_toplevel_windows()
        if self.update() and (len(self.get_toplevel_windows())==0): #update succesvol en nog geen ander Toplevel() venster open
            tolerance=1E-13
            Nmaxinterations=5000
            self.findnumericwindow=Findnumericwindow("root") # custom dialoog box creeren
            self.findnumericwindow.startentry.delete(0, 'end')
            self.findnumericwindow.startentry.insert(tkinter.END,self.roundvaluestr(self.tstart,8))
            self.findnumericwindow.stopentry.delete(0, 'end')
            self.findnumericwindow.stopentry.insert(tkinter.END,self.roundvaluestr(self.tstop,8))
            self.findnumericwindow.toleranceentry.delete(0, 'end')
            self.findnumericwindow.toleranceentry.insert(tkinter.END,self.roundvaluestr(tolerance,8))
            self.findnumericwindow.maxNentry.delete(0, 'end')
            self.findnumericwindow.maxNentry.insert(tkinter.END,str(Nmaxinterations))
            self.findnumericwindow.runnumeric() # de numerieke methode al 1 keer uitvoeren
     
            
    # finding root of function using extra window
    # values are usind to call optimize.root_scalar 
    def showroot(self):                    
        start=eval(self.findnumericwindow.startentry.get())
        stop=eval(self.findnumericwindow.stopentry.get())
        fa=self.evalexpression(start)
        fb=self.evalexpression(stop)
        if self.signissame(fa,fb):
            self.findnumericwindow.textbox.delete("1.0", "end")
            self.findnumericwindow.textbox.insert(tkinter.END, "Root finding error\nFunction has same sign at left and right bounds")
            return
        tolerance=eval(self.findnumericwindow.toleranceentry.get())
        Nmaxinterations=eval(self.findnumericwindow.maxNentry.get())
        if Nmaxinterations>(sys.getrecursionlimit()-50): # controle op max. aantal interaties
            Nmaxinterations=sys.getrecursionlimit()-50
        
        # Scipy optimize.root_scalar functie used to find root
        sol = root_scalar(self.evalexpression, bracket=[start, stop], \
            method='brentq', maxiter=Nmaxinterations, xtol=tolerance)
        r, Ninterations=sol.root, sol.iterations    
        if sol.converged:
            rstr=f"{r:.12f}"
            f=self.evalexpression(r)
            fstr=f"{f:.12e}"
            output="Function f(x) = "+self.txt+"\nInterval "+str(start)+" to "+str(stop)
            output+="\nRoot "+rstr+"\nCheck "+fstr
            output+="\nNumber of iterations "+str(Ninterations)
            self.findnumericwindow.textbox.delete("1.0", "end")
            self.findnumericwindow.textbox.insert(tkinter.END, output)
        else: 
            self.findnumericwindow.textbox.delete("1.0", "end")
            self.findnumericwindow.textbox.insert(tkinter.END, str(sol))
      
                
    def setnumberofpoints(self):
        answer=simpledialog.askinteger("Number of points","Enter number of points to calculate for graph (100 .. 10000)",minvalue=100, maxvalue=10000,initialvalue=self.N)
        if not(answer is None):
            self.N=answer
            self.update()

    def setlinecolor(self):
        answer=colorchooser.askcolor(self.linecolor)
        if not(answer[1] is None):
            self.linecolor=answer[1]
            self.update()
            
    def setlabelcolor(self):
        answer=colorchooser.askcolor(self.labelcolor)
        if not(answer[1] is None):
            self.labelcolor=answer[1]
            self.update()
            
    def setgridcolor(self):
        answer=colorchooser.askcolor(self.gridcolor)
        if not(answer[1] is None):
            self.gridcolor=answer[1]
            self.update()
            
    def setaxiscolor(self):
        answer=colorchooser.askcolor(self.axiscolor)
        if not(answer[1] is None):
            self.axiscolor=answer[1]
            self.update()

            
    def setplotbackgroundcolor(self):
        answer=colorchooser.askcolor(self.plotbackgroundcolor)
        if not(answer[1] is None):
            self.plotbackgroundcolor=answer[1]
            self.update()          
            
    def setbackgroundcolor(self):
        answer=colorchooser.askcolor(self.backgroundcolor)
        if not(answer[1] is None):
            self.backgroundcolor=answer[1]
            self.update()    
              
            
    def setlinethickness(self):
        answer=simpledialog.askinteger("Line thickness","Enter new line thickness (1..10)",minvalue=1, maxvalue=10,initialvalue=self.linethickness)
        if not(answer is None):
            self.linethickness=answer
            self.update()       
            
    def setfontsize(self):
        answer=simpledialog.askinteger("Font size","Enter new font size",minvalue=6, maxvalue=50,initialvalue=self.fontsize)
        if not(answer is None):
            self.fontsize=answer
            self.update()
    
    # set presets for colors 
    def presetcolor(self,linecolor="#FFFFFF",axiscolor="#B0B0B0",labelcolor="#B0B0B0", \
        gridcolor="#B0B0B0",plotbackgroundcolor="#303030",backgroundcolor="#303030", colormap=cm.Greys_r):
        self.linecolor = linecolor
        self.axiscolor = axiscolor
        self.labelcolor = labelcolor
        self.gridcolor = gridcolor
        self.plotbackgroundcolor = plotbackgroundcolor
        self.backgroundcolor = backgroundcolor
        self.colormap=colormap
        self.update()
        
            
    # plot an example function out of the menu examples
    def plotfunction(self,txt,start,stop,xy,polar,line3d,surface3d):
        self.xymode.set(xy)
        self.polarmode.set(polar)
        self.line3dmode.set(line3d)
        self.surface3dmode.set(surface3d)
        self.entryxstart.delete(0, 'end')
        self.entryxstart.insert(tkinter.END,start)
        self.entryxstop.delete(0, 'end')
        self.entryxstop.insert(tkinter.END,stop)
        self.entryexpr.delete(0, 'end')
        self.entryexpr.insert(tkinter.END, txt)
        self.update()

    # set preset x-as ranges out of menu X ranges    
    def setrange(self, start,stop):
        self.entryxstart.delete(0, 'end')
        self.entryxstart.insert(tkinter.END,start)
        self.entryxstop.delete(0, 'end')
        self.entryxstop.insert(tkinter.END,stop)
        self.update()

    # values t en calculated values y seved in CSV file 
    # use filedialog.asksaveasfilename    
    def saveascsv(self):   
        my_filetypes = [('csv files', '.csv') , ('all files', '.*')]
        path = filedialog.asksaveasfilename(parent=self,initialfile="plotter.csv",
                                    initialdir=os.getcwd(),
                                    title="Please select a file name for saving:",
                                    filetypes=my_filetypes)
        if (path!='') and (path!=()): # als een geldig pad gegeven werd door dialoogbox
            self.update()
            with open(path, 'w', encoding='UTF8') as f:
                writer = csv.writer(f)
                writer.writerow(["x","f(x)"])
                writer.writerows(zip(self.t,self.y)) # zip() iterator gebruiken in combinatie met csv.writerows()
    
    # save plot als image file
    # using Figure.savefig() and filedialog.asksaveasfilename
    def saveasimg(self):
        
        my_filetypes = [('png raster graphics files', '.png'), ('svg vector image format files', '.svg')  , ('all files', '.*')]
        path = filedialog.asksaveasfilename(parent=self,initialfile="plotter.png",
                                    initialdir=os.getcwd(),
                                    title="Please select a file name for saving:",
                                    filetypes=my_filetypes)
        if (path!='') and (path!=()): # als een geldig pad gegeven werd door dialoogbox
            #self.update()
            with open(path, 'w', encoding='UTF8') as f:
                self.fig.savefig(path)
    
    
    # golden section search to find minimum of function
    def gssmin(self,f, a, b, tolerance=1e-5, N=200):
        while (b - a > tolerance) and (N>0):
            N-=1
            c = b - (b - a) * self.invphi
            d = a + (b - a) * self.invphi
            if f(c) < f(d):
                b = d
            else:  # f(c) > f(d) to find the maximum
                a = c
        return ((b + a) / 2,N)

    # golden section search to find maximum of function
    def gssmax(self,f, a, b, tolerance=1e-5, N=200):
        while (b - a > tolerance) and (N>0):
            N-=1
            c = b - (b - a) * self.invphi
            d = a + (b - a) * self.invphi
            if f(c) > f(d):
                b = d
            else:  # f(c) > f(d) to find the maximum
                a = c
        return ((b + a) / 2,N)

    # find maximum function using goldensection search
    # uses simple dialog box containing a textbox
    def findmaximum(self):
        if self.update(): #self.update() returns False when error in function            
            tolerance=1E-9
            Nmaxinterations=int(1E3)
            m,N=self.gssmax(self.evalexpression,self.tstart,self.tstop,tolerance,Nmaxinterations)            
            if not(isnan(m)):
                mstr=f"{m:.9f}"
                f=self.evalexpression(m)
                fstr=f"{f:.3e}"
                Ninterations=Nmaxinterations-N
                output="Function f(x) = "+self.txt+"\nInterval "+str(self.tstart)+" to "+str(self.tstop)
                output+="\nMaximum at x= "+mstr+"\nMaximum of function f(xmax)= "+fstr
                output+="\nNumber of iterations "+str(Ninterations)
                self.txtwindow=Txtwindow()
                self.txtwindow.textbox.insert(tkinter.END, output)
                self.txtwindow.title("Maximum of function")
                
    # find minimum function using goldensection search
    # uses simple dialog box containing a textbox
    def findminimum(self):
        if self.update(): #self.update() returns False when error in function            
            tolerance=1E-9
            Nmaxinterations=int(1E3)
            m,N=self.gssmin(self.evalexpression,self.tstart,self.tstop,tolerance,Nmaxinterations)            
            if not(isnan(m)):
                mstr=f"{m:.9f}"
                f=self.evalexpression(m)
                fstr=f"{f:.3e}"
                Ninterations=Nmaxinterations-N
                output="Function f(x) = "+self.txt+"\nInterval "+str(self.tstart)+" to "+str(self.tstop)
                output+="\nMinimum at x= "+mstr+"\nMinimum of function f(xmin)= "+fstr
                output+="\nNumber of iterations "+str(Ninterations)
                self.txtwindow=Txtwindow()
                self.txtwindow.textbox.insert(tkinter.END, output)
                self.txtwindow.title("Minimum of function")
     
                        
    
    # integraal calculated of functie with extra window
    # extra window of class self.findnumericwindow
    def findintegralscipyquad(self):
        if self.update() and (len(self.get_toplevel_windows())==0) \
            and (self.xymode.get()==False): #update succesvol en nog geen ander Toplevel() venster open
            tolerance=1E-8
            Nmaxinterations=5000
            self.findnumericwindow=Findnumericwindow("integral") # custom dialoog box creeren
            self.findnumericwindow.startentry.delete(0, 'end')
            self.findnumericwindow.startentry.insert(tkinter.END,self.roundvaluestr(self.tstart,8))
            self.findnumericwindow.stopentry.delete(0, 'end')
            self.findnumericwindow.stopentry.insert(tkinter.END,self.roundvaluestr(self.tstop,8))
            self.findnumericwindow.toleranceentry.delete(0, 'end')
            self.findnumericwindow.toleranceentry.insert(tkinter.END,self.roundvaluestr(tolerance,8))
            self.findnumericwindow.maxNentry.delete(0, 'end')
            self.findnumericwindow.maxNentry.insert(tkinter.END,str(Nmaxinterations))
            self.findnumericwindow.runnumeric() # de numerieke methode al 1 keer uitvoeren
          
        
    # integraal calculated of functie with extra window
    # values from extra window are used to call scipy integrate.quad 
    def showintegralscipyquad(self):  
        start=eval(self.findnumericwindow.startentry.get())
        stop=eval(self.findnumericwindow.stopentry.get())
        tolerance=eval(self.findnumericwindow.toleranceentry.get())
        Nmaxinterations=eval(self.findnumericwindow.maxNentry.get())
        # de Scipy integrate.quad functie gebruiken om de integraal te vinden
        (res,abserror)=quad(self.evalexpression,start,stop,epsabs=tolerance, \
            limit=Nmaxinterations)
        resstr=f"{res:.12f}"
        abserrorstr=f"{abserror:.12e}"
        output="Function f(x) = "+self.txt+"\nInterval "+str(start)+" to "+str(stop)
        output+="\nIntegral over interval "+resstr+"\nAbsolute error "+abserrorstr
        self.findnumericwindow.textbox.delete("1.0", "end")
        self.findnumericwindow.textbox.insert(tkinter.END, output)
        # plotfx(self,fillstart=0.0,fillstop=1.0,fillshow=False)
        if (self.polarmode.get()==False) and (self.xymode.get()==False):
            self.plotfx(fillstart=start,fillstop=stop,fillshow=True)
        

    # even handler for key presses
    def key_released(self,e): 
        if "canvas" in str(e.widget): # react on arrows when canvas has focus
            match e.keysym:
                case "Left"|"KP_Left": 
                    self.panleft()
                case "Right"|"KP_Right":
                    self.panright()
                case "KP_Add"|"plus":
                    self.zoomin()
                case "KP_Subtract"|"minus":
                    self.zoomout()
        elif "entry" in str(e.widget): # react on Enter if entries have focus
            if e.keysym=="KP_Enter": 
                self.update()
    
    # returns list of widgets which are instance of Toplevel
    # meaning list of open dialoogboxes 
    def get_toplevel_windows(self):
        tops = []
        for widget in self.winfo_children(): # Loop through each widget in main window
            if isinstance(widget,tkinter.Toplevel): # If widget is an instance of toplevel
                tops.append(widget) # Append to a list                 
        return(tops) 
         
        

# class for window with textbox and ok button
class Txtwindow(tkinter.Toplevel): # inherits van Tkinter.Toplevel
    def __init__(self): 
        super().__init__()
        self.textbox=tkinter.Text(self, width=50, height=12)        
        self.okbutton=tkinter.Button(master=self, text="Close", width=15, command=self.destroy)
        self.copybutton=tkinter.Button(master=self, text="Copy to clipboard", width=15, command=self.copytoclipboard)
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 0)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.textbox.grid(row=0,column=0,columnspan=2,sticky="WENS")
        self.copybutton.grid(row=1,column=0,sticky="E")
        self.okbutton.grid(row=1,column=1,sticky="E")        

    def copytoclipboard(self): # text out of textbox and place on clipboard
        txt = self.textbox.get(1.0, "end-1c")
        self.clipboard_clear()
        self.clipboard_append(txt)
        
        
# dialogbox for numerical methods with multiple entry boxes, labels and a  textbox
# based onTkinter.toplevel        
class Findnumericwindow(tkinter.Toplevel): # erft van Tkinter.Toplevel
    def __init__(self,action): 
        super().__init__()
        self.action=action # actie which Findnumericwindow is used for
        self.title(self.action.capitalize())
        
        # buttons defined
        self.okbutton=ttk.Button(master=self, text="Close", width=15, command=self.destroy)
        self.gobutton=ttk.Button(master=self, text="Find "+self.action, width=15, command=self.runnumeric)
        
        # labels and entries defined
        self.startlabel=ttk.Label(master=self, text="Start x value")
        self.startentry=tkinter.Entry(master=self, width="15",font=("FreeMono",12,"bold"),insertwidth=2)
        self.startentry.config({"background": "#303030","foreground": "#ffffff","insertbackground": "#ffffff"})
        self.stoplabel=ttk.Label(master=self, text="Stop x value")
        self.stopentry=tkinter.Entry(master=self, width="15",font=("FreeMono",12,"bold"),insertwidth=2)
        self.stopentry.config({"background": "#303030","foreground": "#ffffff","insertbackground": "#ffffff"})
        self.tolerancelabel=ttk.Label(master=self, text="Tolerance")
        self.toleranceentry=tkinter.Entry(master=self, width="15",font=("FreeMono",12,"bold"),insertwidth=2)
        self.toleranceentry.config({"background": "#303030","foreground": "#ffffff","insertbackground": "#ffffff"})
        self.maxNlabel=ttk.Label(master=self, text="Max. number of iterations")
        self.maxNentry=tkinter.Entry(master=self, width="15",font=("FreeMono",12,"bold"),insertwidth=2)
        self.maxNentry.config({"background": "#303030","foreground": "#ffffff","insertbackground": "#ffffff"})
        self.textlabel=ttk.Label(master=self, text="Result")
        
        # textbox for output defined
        self.textbox=tkinter.Text(self, width=40, height=6,font=("FreeMono",12,"bold"),insertwidth=2)
        self.textbox.config({"background": "#303030","foreground": "#ffffff","insertbackground": "#ffffff"})
        
        # widgets aligned using grid()
        self.startlabel.grid(row=0,column=0,columnspan=1,sticky="WENS") 
        self.startentry.grid(row=1,column=0,columnspan=1,sticky="WENS") 
        self.stoplabel.grid(row=0,column=1,columnspan=1,sticky="WENS") 
        self.stopentry.grid(row=1,column=1,columnspan=1,sticky="WENS") 
        self.tolerancelabel.grid(row=2,column=0,columnspan=1,sticky="WENS") 
        self.toleranceentry.grid(row=3,column=0,columnspan=1,sticky="WENS")         
        self.maxNlabel.grid(row=2,column=1,columnspan=1,sticky="WENS") 
        self.maxNentry.grid(row=3,column=1,columnspan=1,sticky="WENS")         
        self.textlabel.grid(row=4,column=0,columnspan=2,sticky="WENS") 
        self.textbox.grid(row=5,column=0,columnspan=2,sticky="WENS")
        self.okbutton.grid(row=6,column=0,sticky="WENS") 
        self.gobutton.grid(row=6,column=1,sticky="WENS")
        
        # define which row and columns scale
        self.rowconfigure(5, weight = 1)
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        
    # execute numerical methode which was given    
    def runnumeric(self):
        match self.action:
            case "root":
                self.master.showroot() 
            case "integral":
                self.master.showintegralscipyquad()


# een instance of Plotter()
plotter=Plotter()
# de mainloop starten
plotter.mainloop()
