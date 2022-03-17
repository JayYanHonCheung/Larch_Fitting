# -*- coding: utf-8 -*-
"""
Submission script for multi-path Cu Standard EXAFS Fitting

Created on Thu Feb  3 01:35:08 2022
@author: Jay Yan
"""

from larch import Group
from larch.xafs import feffit, feffit_dataset, feffit_transform, feffit_report
from larch.xafs import autobk, feffpath
from larch.fitting import  param_group, param

import os
import h5py
import numpy as np

# cwd = os.getcwd()

file_path = r"data/Cu_foil_STD_merge_norm.nxs" # Normalised .nxs file

# Reading .nxs by h5py
file = h5py.File(file_path, "r")
energy = np.array(file["processed"]["result"]["energy"])
data = np.array(file["processed"]["result"]["data"])

# Loading into a larch group and autobk (see note 2)
std_cu = Group(name="Cu Standard", energy=energy, mu=data)
autobk(std_cu, pre_edge_kws={"nnorm": 0, "nvict": 0}, rbkg=1.0) 

# Scattering path files
from tools import get_feff_info as finfo

feff_folder = r"data/feff_paths/"
info = finfo.get_path_info(feff_folder)

# Define Fourier transform and fitting space (Actual FT parameters for EXAFS fitting)
_feffit_trans = feffit_transform(kmin=3.000, kmax=15.000, dk=1.0000, kw=2,
                                 window="hanning", fitspace='r', rmin=1.000, rmax=6.200)

from iteration_utilities import deepflatten

# Create feffit Parameter Group to hold fit parameters (Core parameters)
_feffit_params = param_group(s02=param(1.0, min=0, vary=True),
                             e0=param(0.1, min=-25, max=25, vary=True))

# Create feffit Parameter Group to hold fit parameters (Repeating parameters)
# The paths information from "info" is referred
scatter_paths = [os.path.join(feff_folder, fname) for fname in info["file"].values[:19]]
ncucu = info["deg"].values
path_num = len(scatter_paths)

fit_params = ["n_cucu", "delr_cu", "sigma2_cu"]
def fit_constraints(n):
    constraints = [param(n, vary=False),
                   param(0.001, min=-0.5, max=0.5, vary=True),
                   param(0.008, min=0.001, max=0.009, vary=True)]
    
    return constraints

def flatten_list(_list):
    return np.array(_list).ravel().tolist()

all_fit_params = [param + str(i) for i in range(path_num) for param in fit_params]
all_fit_cons = list(deepflatten([fit_constraints(n) for i, n in zip(range(path_num), ncucu)]))

# Put organised fit parameters and constraints into feffit parameter group
for key, value in zip(all_fit_params, all_fit_cons):
    setattr(_feffit_params, key, value)
    
# Generate dictionary containing scattering paths
_paths_dict = {}

def generate_feffpath(file_path, label, degen, e0, sigma2, s02, deltar):
    return feffpath(file_path, label=label, degen=degen, e0=e0, sigma2=sigma2, s02=s02, deltar=deltar)
    
for i, scatter_path in enumerate(scatter_paths):
    _paths_dict["Cu" + str(i)] = generate_feffpath(scatter_path,
                                                   label="Cu"+str(i),
                                                   degen=1,
                                                   e0="e0",
                                                   sigma2="sigma2_cu"+str(i),
                                                   s02="s02 * n_cucu"+str(i),
                                                   deltar="delr_cu"+str(i))

# Build feffit dataset, run feffit
_feffit_dataset = feffit_dataset(data=std_cu, transform=_feffit_trans, paths=_paths_dict)
_feffit_result = feffit(_feffit_params, _feffit_dataset)

# Save feffit results into output files
import os
# from lmfit import fit_report
from tools import io_results as io_res

output_dir = r"output/"

# with open(os.path.join(output_dir, "feffit_report.txt"), "w") as report:
#     report.write(feffit_report(_feffit_result))

# with open(os.path.join(output_dir, "lmfit_report.txt"), "w") as lmreport:
#     lmreport.write(fit_report(_feffit_result.fit_details))
    
io_res.save(_feffit_result, output_dir)

