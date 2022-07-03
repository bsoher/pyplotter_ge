#!/usr/bin/env python

# Copyright (c) 2014-2019 Brian J Soher - All Rights Reserved
# 
# Redistribution and use in source and binary forms, with or without
# modification, are not permitted without explicit permission.


# Python modules

# 3rd party modules
import wx

# Our modules
from pyplotter_ge.common.plot_panel_stairs import PlotPanelStairs
        

class PlotPanelGePlotter(PlotPanelStairs):
    
    def __init__(self, parent, tab, tab_dataset, **kwargs):
        
        PlotPanelStairs.__init__( self, parent, **kwargs )

        # tab is the containing widget for this plot_panel, it is used
        # in resize events, the tab attribute is the AUI Notebook tab
        # that contains this plot_panel

        self.top   = wx.GetApp().GetTopWindow()
        self.tab   = tab  
        self.tab_dataset = tab_dataset
        
        self.set_color( (255,255,255) )


    # EVENT FUNCTIONS -----------------------------------------------
    
    def on_motion(self, xdata, ydata, val, bounds, iaxis):
        
        value = 0.0
        if iaxis in list(range(self.naxes)):
            value = val
            
        self.top.statusbar.SetStatusText( " Xvalue [int] = %d" % (xdata, ), 0)
        self.top.statusbar.SetStatusText( " ", 1)
        self.top.statusbar.SetStatusText( " Value = "+str(value), 2)

    
    def on_scroll(self, button, step, iaxis):
        
        self.set_vertical_scale(step)

            
    def on_zoom_select(self, xmin, xmax, val, ymin, ymax, reset=False, iplot=None):
        if reset:
            # we only need to bother with setting the vertical scale in here
            # if we did a reset of the x,y axes.
            self.vertical_scale = self.dataymax


    def on_zoom_motion(self, xmin, xmax, val, ymin, ymax, iplot=None):
        
        tstr  = xmin
        tend  = xmax
        if tstr > tend: tstr, tend = tend, tstr
        tdelta = tend - tstr  # keeps delta positive
        self.top.statusbar.SetStatusText( " Xvalue [int] = " , 0)
        self.top.statusbar.SetStatusText( " Range = %.2f to %.2f" % (tstr, tend), 1)
        self.top.statusbar.SetStatusText( " dXvalue = %.2f" % (tdelta, ), 2)

        
    def on_refs_select(self, xmin, xmax, val, reset=False, iplot=None):
        pstr  = xmin
        pend  = xmax
        if pstr > pend: pstr, pend = pend, pstr
        delt = -1*(pstr - pend)  # keeps delta positive
        self.top.statusbar.SetStatusText( " Range = %.2f to %.2f  dXvalue = %.2f " % (pstr, pend, delt),3)


    def on_refs_motion(self, xmin, xmax, val, iplot=None):

        pstr  = xmin
        pend  = xmax
        if pstr > pend: pstr, pend = pend, pstr
        delt = -1*(pstr - pend)  # keeps delta positive
        self.top.statusbar.SetStatusText( " Xvalue [int] = " , 0)
        self.top.statusbar.SetStatusText( " Range = %.2f to %.2f" % (pstr, pend),1)
        self.top.statusbar.SetStatusText( " dXvalue = %.2f " % (delt, ), 2)


    def on_middle_select(self, xstr, ystr, xend, yend, iplot):
        pass


    def on_middle_press(self, xloc, yloc, iplot, bounds=None, xdata=None, ydata=None):
        pass

        
    def on_middle_motion(self, xcur, ycur, xprev, yprev, iplot):
        pass
        
    
        
  
    
