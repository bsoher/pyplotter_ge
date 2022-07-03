# Python modules
from __future__ import division

# 3rd party modules
import setuptools


VERSION = open("VERSION").read().strip()

NAME = "PyPlotter_GE"

DESCRIPTION = """PyPlotter_GE is an offline version of the GE plotter application to plot XML waveform files."""

LONG_DESCRIPTION = """
PyPlotter_GE is an offline version of the GE plotter application to plot XML waveform files. 
"""
MAINTAINER = "Dr. Brian J. Soher"
MAINTAINER_EMAIL = "bsoher ~at~ briansoher ~dot com~"
# http://pypi.python.org/pypi?:action=list_classifiers
CLASSIFIERS = [ "Development Status :: 2 - Beta",
                "Intended Audience :: Science/Research",
                "Intended Audience :: Healthcare Industry",
                "License :: OSI Approved :: BSD-3-Clause",
                "Operating System :: Microsoft :: Windows",
                "Operating System :: POSIX :: Linux",
                "Programming Language :: Python :: 3.9",
              ]
LICENSE = "https://opensource.org/licenses/BSD-3-Clause"
PLATFORMS = 'Windows, Linux, MacOS'
KEYWORDS = "mri, mrs, pulse sequence, plotting"

packages = setuptools.find_packages()

setuptools.setup(name=NAME,
                 version=VERSION,
                 packages=packages,
                 entry_points = {
                         "console_scripts": ['pyplotter_ge = pyplotter_ge.pyplotter_ge:main']
                 },
                 maintainer=MAINTAINER,
                 maintainer_email=MAINTAINER_EMAIL,
                 zip_safe=False,
                 include_package_data=True,
#                 classifiers=CLASSIFIERS,
#                 license=LICENSE,
                 description=DESCRIPTION,
                 long_description=LONG_DESCRIPTION,
                 platforms=PLATFORMS,
                 keywords=KEYWORDS,
                 # setuptools should be installed along with PyPlotter_GE; the latter requires the
                 # former to run. (PyPlotter_GE uses setuptools' pkg_resources in get_vespa_version()
                 # to get the package version.) Since PyPlotter_GE is distributed as a wheel which can
                 # only be installed by pip, and pip installs setuptools, this 'install_requires'
                 # is probably superfluous and just serves as documentation.
                 install_requires=['setuptools'],
                 )
