# -*- coding: utf-8 -*-
"""
Submission scripts for multi-spectra EXAFS fittings
Created on Wed Feb 16 19:46:04 2022

@author: Jay Yan
"""

from larch.xafs import feffit, feffit_dataset, feffit_transform
from larch.xafs import autobk, feffpath
from larch.fitting import  param_group, param
from larch.io import read_ascii

import os
import copy
from tools import io_results as io_res

""" 0. Preparing Data """

data_dir = r"data/spectra_9000/"
fnames = [fname for fname in os.listdir(data_dir)]

path_list = [os.path.join(data_dir, fnames[i]) for i in range(0, len(fnames), 90)]
fname_list = [fnames[i] for i in range(0, len(fnames), 90)]

""" 1. Batch Reading Data """

# Initialisation
data_list = [read_ascii(fpath, labels="null energy mu") for fpath in path_list]
for data, fname in zip(data_list, fname_list):
    data.groupname = fname[:-4]
    
# Pre-processing - EXAFS fittings only need a valid k space
    autobk(data, pre_edge_kws={"nnorm": 0, "nvict": 0}, rbkg=1.00) 
    
""" 2.1 Setup feffit - feffit parameters + FT and fitting space """

# Create feffit Parameter Group to hold fit parameters (Core parameters)
_feffit_params = param_group(s02=param(0.907, min=0, vary=False),
                             e0=param(0.1, min=-10, max=10, vary=True),
                             sigma2_cu=param(0.008, min=0.001, max=0.009, vary=True),
                             sigma2_o=param(0.008, min=0.001, max=0.009, vary=True))

# Create feffit Parameter Group to hold fit parameters (Repeating parameters)
data_num = len(data_list)

fit_params = ["n_cucu_", "n_cuo_", "delr_cu_", "delr_o_"]
fit_values = [param(1.0, vary=True),
              param(1.0, vary=True),
              param(0.001, min=-0.5, max=0.5, vary=True),
              param(0.001, min=-0.5, max=0.5, vary=True)]

all_fit_params = [param + str(i) for i in range(data_num) for param in fit_params]
all_fit_values = fit_values * data_num

for key, value in zip(all_fit_params, all_fit_values):
    setattr(_feffit_params, key, value)
    
# Define Fourier transform and fitting space
_feffit_trans = feffit_transform(kmin=3.000, kmax=10.000, dk=3.0000, kw=2,
                                 window="hanning", fitspace='r', rmin=1.000, rmax=4.000)


""" 2.2 Setup up paths for all datasets. """

# Create list of base paths
_paths = []

_paths_names = ["Cu_", "O_"]
_all_paths_names = [pname + str(i) for i in range(data_num) for pname in _paths_names]

_path_cu = feffpath(r"data/feff_paths/Cu1_K_Copper_cif11145/feff0001.dat",
                degen=1, e0='e0', sigma2='sigma2_cu')
_path_o = feffpath(r"data/feff_paths/Cu1_K_Tenorite_cif11639/feff0001.dat",
               degen=1, e0='e0', sigma2='sigma2_o')

_path_keys = ["label", "s02", "deltar"]
_path_values_cu = ["Cu_", "s02 * n_cucu_", "delr_cu_"]
_path_values_o = ["O_", "s02 * n_cuo_", "delr_o_"]

for i in range(data_num):
    
    # Setup for Cu-Cu paths
    _path_cu_temp = copy.deepcopy(_path_cu)
    for key, value in zip(_path_keys, _path_values_cu):
        setattr(_path_cu_temp, key, value + str(i))

    # Setup for Cu-O paths    
    _path_o_temp = copy.deepcopy(_path_o)
    for key, value in zip(_path_keys, _path_values_o):
        setattr(_path_o_temp, key, value + str(i))
        
    _paths_dict = {_paths_names[0] + str(i): _path_cu_temp,
                   _paths_names[1] + str(i): _path_o_temp}
    
    _paths.append(_paths_dict)
    
""" 2.3 Build and Run feffit dataset"""

_feffit_dataset_list = [feffit_dataset(data=data, paths=path, transform=_feffit_trans) for data, path in zip(data_list, _paths)]
_feffit_result = feffit(_feffit_params, _feffit_dataset_list)

""" 3. Save Results """

output_dir = r"output/exafs_multifit_101/"
io_res.save(_feffit_result, output_dir)

