#!/usr/bin/env python

# Copyright (c) 2014-2019 Brian J Soher - All Rights Reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are not permitted without explicit permission.

# -----------------------------------------------------------------------------
# Version 0.1 - 2022-04-11
# - basic functionality established, read in GE Plotter files and display
#
# -----------------------------------------------------------------------------

# Python modules

# 3rd party modules
import wx
import numpy as np

# Our modules
import pyplotter_ge.util_config_pyplotter_ge as util_config_pyplotter_ge



class PrefsGePlotter(object):

    def __init__(self):

        self.foreground_color = "black"
        self.bgcolor = "white"
        self.zero_line_plot_show = True
        self.zero_line_plot_top = False
        self.zero_line_plot_middle = True
        self.zero_line_plot_bottom = False
        self.xaxis_show = False
        self.title_show = False
        self.show_gradx = True
        self.show_grady = True
        self.show_gradz = True
        self.show_ssp = True
        self.show_rho = True
        self.show_theta = True
        self.show_omega = True
        self.data_type_summed = False
        self.zero_line_plot_color = "goldenrod"
        self.zero_line_plot_style = "solid"
        self.line_color_real = "blue"
        self.line_color_imaginary = "red"
        self.line_color_magnitude = "purple"
        self.line_width = 1.0
        self.plot_view = "all"

    def set_from_config(self):

        config = util_config_pyplotter_ge.Config()

        tmp = config.get_main_pref('foreground_color')
        if tmp: self.foreground_color = tmp
        tmp = config.get_main_pref('bgcolor')
        if tmp: self.bgcolor = tmp

        attr = ['zero_line_plot_show',
                'zero_line_plot_top',
                'zero_line_plot_middle',
                'zero_line_plot_bottom',
                'xaxis_show',
                'show_gradx',
                'show_grady',
                'show_gradz',
                'show_ssp',
                'show_rho',
                'show_theta',
                'show_omega',
                'data_type_summed',
                ]

        for item in attr:
            tmp = config.get_main_pref(item)
            if tmp:
                setattr(self, item, tmp=='True')

        # tmp = config.get_main_pref('zero_line_plot_show')
        # if tmp: self.zero_line_plot_show = tmp == 'True'
        # tmp = config.get_main_pref('zero_line_plot_top')
        # if tmp: self.zero_line_plot_top = tmp == 'True'
        # tmp = config.get_main_pref('zero_line_plot_middle')
        # if tmp: self.zero_line_plot_middle = tmp == 'True'
        # tmp = config.get_main_pref('zero_line_plot_bottom')
        # if tmp: self.zero_line_plot_bottom = tmp == 'True'
        # tmp = config.get_main_pref('xaxis_show')
        # if tmp: self.xaxis_show = tmp == 'True'
        # tmp = config.get_main_pref('show_gradx')
        # if tmp: self.show_gradx = tmp == 'True'
        # tmp = config.get_main_pref('show_grady')
        # if tmp: self.show_grady = tmp == 'True'
        # tmp = config.get_main_pref('show_gradz')
        # if tmp: self.show_gradz = tmp == 'True'
        # tmp = config.get_main_pref('show_ssp')
        # if tmp: self.show_ssp = tmp == 'True'
        # tmp = config.get_main_pref('show_rho')
        # if tmp: self.show_rho = tmp == 'True'
        # tmp = config.get_main_pref('show_theta')
        # if tmp: self.show_theta = tmp == 'True'
        # tmp = config.get_main_pref('show_omega')
        # if tmp: self.show_omega = tmp == 'True'
        # tmp = config.get_main_pref('data_type_summed')
        # if tmp: self.data_type_summed = tmp == 'True'

        tmp = config.get_main_pref('zero_line_plot_color')
        if tmp: self.zero_line_plot_color = tmp
        tmp = config.get_main_pref('zero_line_plot_style')
        if tmp: self.zero_line_plot_style = tmp
        tmp = config.get_main_pref('line_color_real')
        if tmp: self.line_color_real = tmp
        tmp = config.get_main_pref('line_color_imaginary')
        if tmp: self.line_color_imaginary = tmp
        tmp = config.get_main_pref('line_color_magnitude')
        if tmp: self.line_color_magnitude = tmp
        tmp = config.get_main_pref('line_width')
        if tmp: self.line_width = float(tmp)
        tmp = config.get_main_pref('plot_view')
        if tmp: self.plot_view = tmp


class PlotterNode():

    def __init__(self, attributes=''):

        self.id = 0
        self.name = ''
        self.date = ''
        self.author = ''
        self.begin_time = ''
        self.end_time = ''
        self.sequencers = []
        self.fname = ''

        if attributes:
            self.inflate(attributes)

    @property
    def date_str(self):
        return self.date[1:8]

    @property
    def time_str(self):
        return self.date[9:]

    def inflate(self, source):
        root = source.getroot()
        # Quacks like an ElementTree.Element
        for item in ("name", "date", "author"):
            val = root.get(item)
            if val:
                setattr(self, item, val)
        val = root.get('beginTime')
        if val: self.begin_time = val
        val = root.get('endTime')
        if val: self.end_time = val

        nodes = root.findall('sequencer')
        for node in nodes:
            self.sequencers.append(SequencerNode(node))

        # TODO bjs - sort sequencers list by 'id' attribute


class SequencerNode():

    def __init__(self, attributes=''):
        self.id = 0
        self.title = ''
        self.xtitle = ''
        self.ytitle = ''
        self.data = ''
        self.edges = None
        self.values = None

        if attributes:
            self.inflate(attributes)

    @property
    def channel(self):
        items = self.title.split('|')
        return items[-1].strip()

    def inflate(self, source):

        # Quacks like an ElementTree.Element
        for item in ("id", ):
            val = source.get(item)
            if val:
                setattr(self, item, int(val))

        for item in ("title", "xtitle", "ytitle"):
            val = source.get(item)
            if val:
                setattr(self, item, val)

        val = source.findtext('data')
        if val:
            self.data = val
            edges, values = self.parse_data(val)
            self.edges = np.array(edges)
            self.values = np.array(values)

    def parse_data(self, val):
        edges = []
        values = []
        items = val.split('\n')
        for item in items:
            if item:
                tmp = item.split('\t')
                edges.append(int(tmp[0]))
                values.append(int(tmp[1]))

        e = edges[::2].copy()
        v = values[::2].copy()
        v = v[0:-1].copy()
        return e, v


def is_intable(s):
    """True if the passed value can be turned into a int, False otherwise"""
    try:
        int(s)
        return True
    except ValueError:
        return False


def util_create_menu_bar(self, entries, ids=None):
    """
    Example of the menuData function that needs to be in the program
    in which you are creating a Menu

        def menuData(self):
            return [("&File", (
                        ("&New",  "New Sketch file",  self.OnNew),
                        ("&Open", "Open sketch file", self.OnOpen),
                        ("&Save", "Save sketch file", self.OnSave),
                        ("", "", ""),
                        ("&Color", (
                            ("&Black",    "", self.OnColor,      wx.ITEM_RADIO),
                            ("&Red",      "", self.OnColor,      wx.ITEM_RADIO),
                            ("&Green",    "", self.OnColor,      wx.ITEM_RADIO),
                            ("&Blue",     "", self.OnColor,      wx.ITEM_RADIO),
                            ("&Other...", "", self.OnOtherColor, wx.ITEM_RADIO))),
                        ("", "", ""),
                        ("About...", "Show about window", self.OnAbout),
                        ("&Quit",    "Quit the program",  self.OnCloseWindow)))]
    """
    def create_menu(self, items, ids=None):
        menu = wx.Menu()
        for item in items:
            if len(item) == 2:
                label = item[0]
                sub_menu = create_menu(self, item[1], ids=ids)
                item = menu.Append(wx.ID_ANY, label, sub_menu)
                if ids is not None:
                    ids[label] = item
            elif len(item) == 3:
                create_menu_item(self, menu, item[0], item[1], item[2], ids=ids)
            else:
                #create_menu_item(self, menu, *item, ids=ids)
                create_menu_item(self, menu, item[0], item[1], item[2], kind=item[3], ids=ids)
        return menu

    def create_menu_item(self, menu, label, status, handler, kind=wx.ITEM_NORMAL, ids=None):
        if not label:
            menu.AppendSeparator()
            return
        item = menu.Append(-1, label, status, kind)
        if ids is not None:
            ids[label] = item
        self.Bind(wx.EVT_MENU, handler, item)

    menuBar = wx.MenuBar()

    for entry in entries:
        label = entry[0]
        items = entry[1]
        menuBar.Append(create_menu(self, items, ids=ids), label)

    self.SetMenuBar(menuBar)