# -*- coding: utf-8 -*-
"""
Submission scripts for multi-spectra EXAFS fittings
Created on Wed Feb 16 19:46:04 2022

@author: Jay Yan
"""

# Base packages
import pandas as pd
import os

# Packages for reading data and normalisation
from larch.io import read_ascii
from larch.xafs import autobk

from tools import exafs_param_table as pt

# Packages for EXAFS fittings
from larch.xafs import feffit_transform, feffit_dataset, feffit

# Packages for reading EXAFS fittings results
from tools import io_results as io_res

""" 0. Preparing Data """

data_dir = r"data/spectra_9000/"
fnames = [fname for fname in os.listdir(data_dir)]

path_list = [os.path.join(data_dir, fnames[i]) for i in range(0, len(fnames), 180)]
fname_list = [fnames[i] for i in range(0, len(fnames), 180)]


""" 1. Batch Reading Data """

# Initialisation
data_list = [read_ascii(fpath, labels="null energy mu") for fpath in path_list]
for data, fname in zip(data_list, fnames):
    data.groupname = fname

# Pre-processing - EXAFS fittings only need a valid k space
    autobk(data, pre_edge_kws={"nnorm": 0, "nvict": 0}, rbkg=1.0)
    
""" 2.1 Setup feffit - feffit parameters + FT and fitting space """

# feff folders
feff_folder_cuo =  r"data/feff_paths/Cu1_K_c7_Tenorite_cif11639"
feff_folder_cu =  r"data/feff_paths/Cu1_K_c7_Copper_cif11145"

# Construsting Fitting Parameters Table
fit_table_cu = pt.param_table(feff_folder_cu)
fit_table_cu = fit_table_cu[fit_table_cu["reff"] < 3]

fit_table_cuo = pt.param_table(feff_folder_cuo)
fit_table_cuo = fit_table_cuo[fit_table_cuo["reff"] < 1.9475]

param_table = pd.concat([fit_table_cu, fit_table_cuo])

table_list = []
for i in range(len(data_list)):
    table = param_table.copy()
    table["spectra"] = f"spectra_{i}"
    table_list.append(table)
    
fit_table = pd.concat(table_list, ignore_index=True)

# Setup Fit Constraints in Fit Table

# 1. Set s02 as constant for the fit
fit_table["s02"] = 0.918

# 2. Set degeneracy as a fitting parameter
fit_table["degen"] = "n"

# 3. Group parameters based on scattering path (Note the subscripts added based on scattering material)
fit_table = pt.groupby_path(fit_table, ["degen", "sigma2", "deltar"]) 

# 4. Group parameters based on spectra (Note the added subscripts: d1, d2, d3, ...)
fit_table = pt.groupby_dataset(fit_table, ["degen", "deltar"])

# Save the constructed fit table
output_dir = r"output/exafs_multifit_fittable/"
pt.save_table(fit_table, output_dir)

# Feffit parameters and paths for fitting
feffit_params = pt.setup_feffit_params(fit_table)
feffit_paths = pt.setup_feffit_paths(fit_table)

feffit_trans = feffit_transform(kmin=3.0, kmax=10.000, dk=0.500, kw=2,
                                 window="hanning", fitspace='r', rmin=1.000, rmax=3.000)

feffit_datasets = [feffit_dataset(data=data, paths=path, transform=feffit_trans) for data, path in zip(data_list, feffit_paths)]
    
feffit_result = feffit(feffit_params, feffit_datasets)     

""" 3. Save Results """

output_dir = r"output/exafs_multifit_fittable/"
io_res.save(feffit_result, output_dir)

