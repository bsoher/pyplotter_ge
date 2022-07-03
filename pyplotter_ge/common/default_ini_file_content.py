# Python modules

# 3rd party modules

# Our modules 



"""When App needs to create an app's INI file, this is the content it uses
This could be part of constants.py, but the long triple-quoted strings make it
really hard to read so it's easier if this is isolated in its own module.

This module contains just one object which is a dict called 
DEFAULT_INI_FILE_CONTENT. The dict has a key for each INI file ("importer",
"volumizer", etc.) and associated with that key is the default content
for that INI file. 
"""

# The dict contents are mostly strings

# Colors are described in matplotlib's terms. Matplotlib understands standard
# color names like "red", "black", "blue", etc.
# One can also specify the color using an HTML hex string like #eeefff.
# If you use a string like that, you must put it in quotes, otherwise the
# hash mark will get interpreted as a comment marker. For example, to set
# a background to pale yellow:
#    bgcolor = "#f3f3bb"

DEFAULT_INI_FILE_CONTENT = {



    "pyplotter_ge": """
# The PyPlotterGe GE-Plotter application config file.

[main]
left = 40
top = 40
width = 1200
height = 800

[main_prefs]
bgcolor = "white"
foreground_color = "black"
zero_line_plot_show = False
zero_line_plot_top = False
zero_line_plot_middle = True
zero_line_plot_bottom = False
xaxis_show = False
title_show = False
show_gradx = True
show_grady = True
show_gradz = True
show_ssp = True
show_rho = True
show_theta = True
show_omega = True
data_type_summed = False
zero_line_plot_color = "goldenrod"
zero_line_plot_style = "solid"
line_color_real = "blue"
line_color_imaginary = "red"
line_color_magnitude = "purple"
line_width = 1.0
plot_view = "all"

"""
,}


