#!/usr/bin/env python

# Copyright (c) 2022 Brian J Soher - All Rights Reserved
# 
# Redistribution and use in source and binary forms, with or without
# modification, are not permitted without explicit permission.

# -----------------------------------------------------------------------------
# Version 0.1.0 - 2022-04-12
# - basic functionality established, read in Plotter files and display
# - added ability to show 3, 5, or All plots
# -----------------------------------------------------------------------------

# Python modules
import os
import xml.etree.cElementTree as ElementTree
from multiprocessing import Pool, cpu_count

# 3rd party modules
import wx
from wx.lib.embeddedimage import PyEmbeddedImage

# Our modules
import pyplotter_ge.common.misc as util_misc
import pyplotter_ge.common.common_dialogs as common_dialogs
import pyplotter_ge.util_config_pyplotter_ge as util_config_pyplotter_ge
import pyplotter_ge.auto_gui.pyplotter_ge as pyplotter_ge_gui

from pyplotter_ge.plot_panel_pyplotter_ge import PlotPanelGePlotter
from pyplotter_ge.util_pyplotter_ge import PlotterNode, PrefsGePlotter, util_create_menu_bar, is_intable



APP_NAME = 'PyPlotter_GE'

AppIcon = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAHFJ'
    b'REFUWIXt1jsKgDAQRdF7xY25cpcWC60kioI6Fm/ahHBCMh+BRmGMnAgEWnvPpzK8dvrFCCCA'
    b'coD8og4c5Lr6WB3Q3l1TBwLYPuF3YS1gn1HphgEEEABcKERrGy0E3B0HFJg7C1N/f/kTBBBA'
    b'+Vi+AMkgFEvBPD17AAAAAElFTkSuQmCC')




class PyPlotterGeMain(pyplotter_ge_gui.PyPlotterGeFrame):

    def __init__(self, position, size):
        # Create a frame using values from our INI file.
        self._left, self._top = position
        self._width, self._height = size

        self.prefs = PrefsGePlotter()
        self.prefs.set_from_config()

        style = wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | \
                wx.MAXIMIZE_BOX | wx.SYSTEM_MENU | wx.RESIZE_BORDER | \
                wx.CLIP_CHILDREN

        super().__init__(None, wx.ID_ANY, APP_NAME,
                         pos=(self._left, self._top),
                         size=(self._width, self._height),
                         style=style)

        self.SetSize(self._width, self._height)

        # -----------------------------------------------------------
        # Main Object

        self.fname1 = ''
        self.nplots = 7
        self.nodes = []

        self.node_number = 0
        self.first_scale_flag = True
        self.show_flags = [False, False, False, False, False, False, False]

        # -----------------------------------------------------------
        # Set up pool here to save time later when loading files

        n_cpu = cpu_count()-1 if cpu_count() <= 8 else 7
        self.pool = Pool(n_cpu)

        # -----------------------------------------------------------
        # GUI Creation

        self.SetIcon(AppIcon.GetIcon())

        menu_items = {}
        util_create_menu_bar(self, self.menu_data(), ids=menu_items)
        if self.prefs.zero_line_plot_show:   menu_items['&Show'].Check(True)
        if self.prefs.zero_line_plot_top:    menu_items['&Top'].Check(True)
        if self.prefs.zero_line_plot_middle: menu_items['&Middle'].Check(True)
        if self.prefs.zero_line_plot_bottom: menu_items['&Bottom'].Check(True)
        if self.prefs.xaxis_show: menu_items['X-Axis - Show'].Check(True)
        if self.prefs.title_show: menu_items['Plot Title - Show'].Check(True)

        if self.prefs.show_gradx:
            menu_items['X-Grad'].Check(True)
            self.show_flags[0] = True
        if self.prefs.show_grady:
            menu_items['Y-Grad'].Check(True)
            self.show_flags[1] = True
        if self.prefs.show_gradz:
            menu_items['Z-Grad'].Check(True)
            self.show_flags[2] = True
        if self.prefs.show_ssp:
            menu_items['SSP'].Check(True)
            self.show_flags[3] = True
        if self.prefs.show_rho:
            menu_items['RHO'].Check(True)
            self.show_flags[4] = True
        if self.prefs.show_theta:
            menu_items['THETA'].Check(True)
            self.show_flags[5] = True
        if self.prefs.show_omega:
            menu_items['OMEGA'].Check(True)
            self.show_flags[6] = True

        self.menu_items = menu_items

        self.statusbar = self.CreateStatusBar(4, 0)
        self.statusbar.SetStatusText('Select a folder with Plotter files.')

        self.plotting_enabled = False
        self.populate_controls()
        self.view.display_naxes(self.show_flags)
        self.plotting_enabled = True

        self.bind_events()


    def bind_events(self):
        self.Bind(wx.EVT_CLOSE, self.on_self_close)
        self.Bind(wx.EVT_SIZE, self.on_self_coordinate_change)
        self.Bind(wx.EVT_MOVE, self.on_self_coordinate_change)


    def on_cancel(self, event):
        self.on_self_close(event)


    def on_self_close(self, event):
        # I trap this so I can save my coordinates

        self.pool.terminate()

        config = util_config_pyplotter_ge.Config()
        config.set_window_coordinates("main", self._left, self._top, self._width, self._height)

        config.set_main_pref('foreground_color', self.prefs.foreground_color)
        config.set_main_pref('bgcolor', self.prefs.bgcolor)
        config.set_main_pref('zero_line_plot_show', str(self.prefs.zero_line_plot_show))
        config.set_main_pref('zero_line_plot_top', str(self.prefs.zero_line_plot_top))
        config.set_main_pref('zero_line_plot_middle', str(self.prefs.zero_line_plot_middle))
        config.set_main_pref('zero_line_plot_bottom', str(self.prefs.zero_line_plot_bottom))
        config.set_main_pref('show_gradx', str(self.prefs.show_gradx))
        config.set_main_pref('show_grady', str(self.prefs.show_grady))
        config.set_main_pref('show_gradz', str(self.prefs.show_gradz))
        config.set_main_pref('show_ssp', str(self.prefs.show_ssp))
        config.set_main_pref('show_rho', str(self.prefs.show_rho))
        config.set_main_pref('show_theta', str(self.prefs.show_theta))
        config.set_main_pref('show_omega', str(self.prefs.show_omega))
        config.set_main_pref('xaxis_show', self.prefs.xaxis_show)
        config.set_main_pref('title_show', self.prefs.title_show)
        config.set_main_pref('data_type_summed', str(self.prefs.data_type_summed))
        config.set_main_pref('zero_line_plot_color', self.prefs.zero_line_plot_color)
        config.set_main_pref('zero_line_plot_style', self.prefs.zero_line_plot_style)
        config.set_main_pref('line_color_real', self.prefs.line_color_real)
        config.set_main_pref('line_color_imaginary', self.prefs.line_color_imaginary)
        config.set_main_pref('line_color_magnitude', self.prefs.line_color_magnitude)
        config.set_main_pref('line_width', str(self.prefs.line_width))
        config.set_main_pref('plot_view', self.prefs.plot_view)

        config.write()
        self.Destroy()


    def on_self_coordinate_change(self, event):
        # This is invoked for move & size events
        if self.IsMaximized() or self.IsIconized():
            # Bah, forget about this. Recording coordinates doesn't make sense
            # when the window is maximized or minimized. This is only a
            # concern on Windows; GTK and OS X don't produce move or size
            # events when a window is minimized or maximized.
            pass
        else:
            if event.GetEventType() == wx.wxEVT_MOVE:
                self._left, self._top = self.GetPosition()
            else:
                # This is a size event
                self._width, self._height = self.GetSize()
            event.Skip()


    def populate_controls(self):

        # ---------------------------------------------------------------------
        # Dataset View setup
        # ---------------------------------------------------------------------

        plot_titles = ['Plot '+str(item) for item in range(self.nplots)]

        self.view = PlotPanelGePlotter(
            self.PanelPlot,
            self,
            self,
            naxes=self.nplots,
            zoom='span',
            reference=True,
            middle=True,
            # zoom_button=1,        # bjs - only in plot_panel_spectral for now?
            # middle_button=2,
            # refs_button=3,
            unlink=False,
            do_zoom_select_event=True,
            do_zoom_motion_event=True,
            do_middle_select_event=True,
            do_middle_motion_event=True,
            do_refs_select_event=True,
            do_refs_motion_event=True,
            do_scroll_event=True,
            props_zoom=dict(alpha=0.2, facecolor='yellow'),
            props_cursor=dict(alpha=0.2, facecolor='gray'),
            xscale_bump=0.0,
            yscale_bump=0.05,
            data=[],
            prefs=self.prefs,
            xtitle='DataPoint [int]',
            plot_titles=plot_titles,
            scaling='local'
        )

        # weird work around for Wx issue where it can't initialize and get RGBA buffer because height = 0?
        self.PanelPlot.SetSize((6, 8))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.view, 1, wx.LEFT | wx.TOP | wx.EXPAND)
        self.PanelPlot.SetSizer(sizer)
        self.view.Fit()

        # self.view.dataymax = [50.0 for i in range(self.nplots)]
        # self.view.set_vertical_scale_abs(self.view.dataymax)


    # -------------------------------------------------------------------------
    # Event handlers

    def on_load_files(self, event):

        sect  = 'path_browse1'
        msg   = 'Select directory with Plotter files'
        dpath = util_config_pyplotter_ge.get_path(sect)
        fpath = common_dialogs.pickdir(msg, default_path=dpath)

        if not fpath: return
        if not os.path.isdir(fpath): return

        # Get all files in directory and sub-directories
        # - remove any directories
        # - only take files ending in ints e.g. 'file.xml.10', this removes 'ssp' files

        fnames = []
        for root, _, all_fnames in os.walk(fpath):
            for fname in all_fnames:
                fnames.append(os.path.join(root, fname))

        fnames = [fname for fname in fnames if os.path.isfile(fname)]
        fnames = [fname for fname in fnames if is_intable(fname.split('.')[-1])]

        # we set up our Pool during __init__ call
        items = self.pool.map(read_node_multiprocess, fnames)

        self.nodes = [item for item in items if item is not None]       # failed reads return None
        n_nodes = len(self.nodes)

        self.nodes.sort(key=lambda x: x.id, reverse=False)
        self.fnames = [item.fname for item in self.nodes]

        titles = [item.title for item in self.nodes[0].sequencers]

        # reset the GUI information and parameters

        if self.node_number > n_nodes: self.node_number = n_nodes-1
        if self.nodes:

            self.TextSourceDir.SetLabelText(os.path.dirname(self.fnames[self.node_number]))
            self.TextCurrentFile.SetLabelText(os.path.basename(self.fnames[self.node_number]))

            last_val = self.SpinNodeNumber.GetValue()
            self.SpinNodeNumber.SetMinSize((50, -1))
            self.SpinNodeNumber.SetSize((50, -1))
            self.SpinNodeNumber.SetRange(0, n_nodes-1)
            if last_val > n_nodes-1:
                self.SpinNodeNumber.SetValue(n_nodes-1)

            self.view.set_titles(titles)

            self.first_scale_flag = True
            self.plot()

            path, _ = os.path.split(self.fnames[0])
            util_config_pyplotter_ge.set_path(sect, path)
        else:
            self.statusbar.SetStatusText('No plot nodes found - returning')


    def on_close(self, event):
        self.on_self_close(event)


    def on_zero_line_show(self, event):
        # won't need these with a real Prefs module
        self.prefs.zero_line_plot_show = not self.prefs.zero_line_plot_show
        # will need these
        self.view.update_axes()
        self.view.canvas.draw()

    def on_zero_line_top(self, event):
        # won't need these with a real Prefs module
        self.prefs.zero_line_plot_top = True
        self.prefs.zero_line_plot_middle = False
        self.prefs.zero_line_plot_bottom = False
        # will need these
        self.view.update_axes()
        self.view.canvas.draw()

    def on_zero_line_middle(self, event):
        # won't need these with a real Prefs module
        self.prefs.zero_line_plot_top = False
        self.prefs.zero_line_plot_middle = True
        self.prefs.zero_line_plot_bottom = False
        # will need these
        self.view.update_axes()
        self.view.canvas.draw()

    def on_zero_line_bottom(self, event):
        # won't need these with a real Prefs module
        self.prefs.zero_line_plot_top = False
        self.prefs.zero_line_plot_middle = False
        self.prefs.zero_line_plot_bottom = True
        # will need these
        self.view.update_axes()
        self.view.canvas.draw()

    def on_xaxis_show(self, event):
        # won't need these with a real Prefs module
        self.prefs.xaxis_show = not self.prefs.xaxis_show
        # will need these
        self.view.update_axes()
        self.view.canvas.draw()

    def on_title_show(self, event):
        # won't need these with a real Prefs module
        self.prefs.title_show = not self.prefs.title_show
        # will need these
        self.view.update_axes()
        self.view.canvas.draw()

    def on_placeholder(self, event):
        print( "Event handler for on_placeholder - not implemented")

    def _set_show_checks(self):
        self.menu_items['X-Grad'].Check(self.show_flags[0])
        self.menu_items['Y-Grad'].Check(self.show_flags[1])
        self.menu_items['Z-Grad'].Check(self.show_flags[2])
        self.menu_items['SSP'].Check(self.show_flags[3])
        self.menu_items['RHO'].Check(self.show_flags[4])
        self.menu_items['THETA'].Check(self.show_flags[5])
        self.menu_items['OMEGA'].Check(self.show_flags[6])
        self.prefs.show_gradx = self.show_flags[0]
        self.prefs.show_grady = self.show_flags[1]
        self.prefs.show_gradz = self.show_flags[2]
        self.prefs.show_ssp = self.show_flags[3]
        self.prefs.show_rho = self.show_flags[4]
        self.prefs.show_theta = self.show_flags[5]
        self.prefs.show_omega = self.show_flags[6]

    def on_show_all(self, event):
        self.show_flags = [True, True, True, True, True, True, True]
        self.view.display_naxes(self.show_flags)
        self._set_show_checks()

    def on_show_grad(self, event):
        self.show_flags = [True, True, True, False, False, False, False]
        self.view.display_naxes(self.show_flags)
        self._set_show_checks()

    def on_show_grad_rf(self, event):
        self.show_flags = [True, True, True, True, True, False, False]
        self.view.display_naxes(self.show_flags)
        self._set_show_checks()

    def on_show_gradx(self, event):
        indx = 0
        self.show_flags[indx] = not self.show_flags[indx]
        if self.show_flags.count(True) == 0:
            self.show_flags[indx] = True
            self.menu_items['X-GRAD'].Check(True)
            return
        self.prefs.show_gradx = not self.show_flags[indx]
        self.view.display_naxes(self.show_flags)

    def on_show_grady(self, event):
        indx = 1
        self.show_flags[indx] = not self.show_flags[indx]
        if self.show_flags.count(True) == 0:
            self.show_flags[indx] = True
            self.menu_items['Y-GRAD'].Check(True)
            return
        self.prefs.show_grady = not self.show_flags[indx]
        self.view.display_naxes(self.show_flags)

    def on_show_gradz(self, event):
        indx = 2
        self.show_flags[indx] = not self.show_flags[indx]
        if self.show_flags.count(True) == 0:
            self.show_flags[indx] = True
            self.menu_items['Z-GRAD'].Check(True)
            return
        self.prefs.show_gradz = not self.show_flags[indx]
        self.view.display_naxes(self.show_flags)

    def on_show_ssp(self, event):
        indx = 3
        self.show_flags[indx] = not self.show_flags[indx]
        if self.show_flags.count(True) == 0:
            self.show_flags[indx] = True
            self.menu_items['SSP'].Check(True)
            return
        self.prefs.show_ssp = not self.show_flags[indx]
        self.view.display_naxes(self.show_flags)

    def on_show_rho(self, event):
        indx = 4
        self.show_flags[indx] = not self.show_flags[indx]
        if self.show_flags.count(True) == 0:
            self.show_flags[indx] = True
            self.menu_items['RHO'].Check(True)
            return
        self.prefs.show_rho = not self.show_flags[indx]
        self.view.display_naxes(self.show_flags)

    def on_show_theta(self, event):
        indx = 5
        self.show_flags[indx] = not self.show_flags[indx]
        if self.show_flags.count(True) == 0:
            self.show_flags[indx] = True
            self.menu_items['THETA'].Check(True)
            return
        self.prefs.show_theta = not self.show_flags[indx]
        self.view.display_naxes(self.show_flags)

    def on_show_omega(self, event):
        indx = 6
        self.show_flags[indx] = not self.show_flags[indx]
        if self.show_flags.count(True) == 0:
            self.show_flags[indx] = True
            self.menu_items['OMEGA'].Check(True)
            return
        self.prefs.show_omega = not self.show_flags[indx]
        self.view.display_naxes(self.show_flags)

    def on_user_manual(self, event):
        print('Not Implemented - User Manual')

    def on_about(self, event):
        print('Not Implemented - About')


    def on_node_number(self, event):
        self.node_number = event.GetEventObject().GetValue()
        self.TextCurrentFile.SetLabelText(os.path.basename(self.fnames[self.node_number]))
        self.plot()


    # -------------------------------------------------------------------------
    # Helper methods

    def plot(self, is_replot=False, initialize=False):

        if not self.plotting_enabled:
            return

        if self.nodes is None:
            return

        n = self.node_number

        data = [{'edges': self.nodes[n].sequencers[i].edges,
                 'values': self.nodes[n].sequencers[i].values,
                 'line_color_real': 'black' } for i in range(self.nplots)]

        self.view.set_data(data)
        self.view.update(no_draw=True, set_scale=self.first_scale_flag)
        self.view.canvas.draw()

        if self.first_scale_flag: self.first_scale_flag = False


    def menu_data(self):
        r = [("&File", (
                ("Load Files", "", self.on_load_files),
                ("", "", ""),
                ("&Quit",    "Quit the program",  self.on_close)
            )),
            ("View", (
                ("Zero Line", (
                    ("&Show",    "", self.on_zero_line_show,   wx.ITEM_CHECK, None),
                    ("", "", ""),
                    ("&Top",     "", self.on_zero_line_top,    wx.ITEM_RADIO, None),
                    ("&Middle",  "", self.on_zero_line_middle, wx.ITEM_RADIO, True),
                    ("&Bottom",  "", self.on_zero_line_bottom, wx.ITEM_RADIO, None))),
                ("", "", ""),
                ("X-Axis - Show", "", self.on_xaxis_show,       wx.ITEM_CHECK, None),
                ("Plot Title - Show", "", self.on_title_show,   wx.ITEM_CHECK, None),
                ("", "", ""),
                ("Show All",       "", self.on_show_all),
                ("Show Gradients", "", self.on_show_grad),
                ("Show Grads+RF",  "", self.on_show_grad_rf),
                ("Show Custom", (
                    ("X-Grad",  "", self.on_show_gradx, wx.ITEM_CHECK, None),
                    ("Y-Grad",  "", self.on_show_grady, wx.ITEM_CHECK, None),
                    ("Z-Grad",  "", self.on_show_gradz, wx.ITEM_CHECK, None),
                    ("SSP",     "", self.on_show_ssp,   wx.ITEM_CHECK, None),
                    ("RHO",     "", self.on_show_rho,   wx.ITEM_CHECK, None),
                    ("THETA",   "", self.on_show_theta, wx.ITEM_CHECK, None),
                    ("OMEGA",   "", self.on_show_omega, wx.ITEM_CHECK, None))),
                ("", "", ""),
                ("&Placeholder",    "non-event",  self.on_placeholder)
            )),
            ("Help", (
                ("User Manual", "", self.on_user_manual),
                ("", "", ""),
                ("About",       "",  self.on_about)
            ))]

        return r


def read_node_multiprocess(fname):
    """ This has to be outside the main object to be used in a Pool """
    try:
        with open(fname, 'rb') as f:
            tree = ElementTree.ElementTree(file=f)

        if tree:
            if tree.getroot().tag == 'PulseSequence':
                node = PlotterNode(attributes=tree)
                node.id = int(fname.split('.')[-1])
                node.fname = fname
                return node
            else:
                return None
        else:
            return None

    except Exception as e:
        return None



# ------------------------------------------------------------------------------

def main():
    # This function is for profiling with cProfile

    app = wx.App(0)

    # The app name must be set before the call to GetUserDataDir() below.
    app.SetAppName(APP_NAME)

    # Create the data directory if necessary - this version creates it in
    # the Windows 'AppData/Local' location as opposed to the call to
    # wx.StandardPaths.Get().GetUserDataDir() which returns '/Roaming'

    data_dir = util_misc.get_data_dir()
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    # My settings are in the INI filename defined in 'default_content.py'
    config = util_config_pyplotter_ge.Config()
    position, size = config.get_window_coordinates("main")

    frame = PyPlotterGeMain(position, size)
    app.SetTopWindow(frame)
    frame.Show()

    app.MainLoop()



if __name__ == "__main__":
    main()

    # Useful info - performance timing
    # import time
    # time1 = time.perf_counter()


    
