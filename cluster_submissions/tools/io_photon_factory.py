# -*- coding: utf-8 -*-
"""
Created on Sat Feb 26 23:34:38 2022
@author: Jay Yan

Helper functions to read data files from Photon Factory using Larch.
The formula to convert from mono-angle to energy is obtained from Demeter::Plugin::PFBL12C 
(https://bruceravel.github.io/demeter/pods/Demeter/Plugins/PFBL12C.pm.html)

    data.energy = 2 * pi * hbarc / 2D * sin(data.angle)

where hbarc = 1973.27053324

Note: the computed energy is different to energy generated from Athena (unknown reason)

"""

from larch.io import read_ascii
import numpy as np

def read_fluor(fpath, d=None, hbarc=1973.27053324, name=None):
    """ Read photon factory fluorescence data. """
    data = read_ascii(fpath)
    
    if d is None:
        d = data.mono_dspace

    data.mu = (data.col7 + data.col8 + data.col9 + data.col10 + data.col11 + data.col12 + data.col13) / data.col4
    data.energy = 2 * np.pi * hbarc / (2 * d * np.sin(np.radians(data.angle_read)))
    
    if name is not None:
        data.__name__ = name
   
    return data

def read_trans(fpath, d=None, hbarc=1973.27053324, name=None):
    """ Read photon factory transmission data. """
    data = read_ascii(fpath)
    
    if d is None:
        d = data.mono_dspace
    
    data.mu = np.log(data.col4 / data.col5)
    data.energy = 2 * np.pi * hbarc / (2 * d * np.sin(np.radians(data.angle_read)))
    
    if name is not None:
        data.__name__ = name
        
    return data