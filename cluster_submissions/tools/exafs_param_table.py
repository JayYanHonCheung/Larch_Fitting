# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 23:58:57 2022

@author: Jay Yan

Module to construct and manipulate a pandas dataframe for fitting parameters
"""
import numpy as np
import pandas as pd
from pandas.api.types import is_string_dtype

from tools import get_feff_info as finfo
from larch.xafs import feffpath
from larch.fitting import param_group, param

import os

def param_table(feff_folder):

    columns = ["scatter material", "spectra", "nlegs", "reff", "shell", "amp ratio", 
               "s02", "e0", "degen", "sigma2", "deltar", "fpath"]

    df = pd.DataFrame(columns=columns)
    feff_paths = finfo.get_path_info(feff_folder)
    
    df["fpath"] = [os.path.join(feff_folder, file) for file in feff_paths["file"]]
    df["amp ratio"] = feff_paths["amp ratio"]
    df["degen"] = feff_paths["deg"]
    df["nlegs"] = feff_paths["nlegs"]
    df["reff"] = feff_paths["r effective"]
    df["scatter material"] = finfo.get_path_formula(feff_folder)
    
    for column in columns:
        if df[column].isna().all():
            df[column] = column

    return df

def form_shells(param_table):
    """ Categorise feff paths into shells labelled as a new column. 
        (WIP) For now, same reff is grouped into one shell
    """
    
    reff0 = None
    shell_num = 0
    shell = []
    for reff in param_table["reff"]:
        if reff == reff0:
            pass
        else:
            shell_num += 1
            
        reff0 = reff
        shell.append(shell_num)
    
    param_table["shell"] = shell
    
    return param_table

def groupby_path(param_table, keys):
    """ Group parameters based on scattering path/material. """
    
    for key in keys:
        param_table[key] = [f"{param}_{mat}" for param, mat in zip(param_table[key], param_table["scatter material"])]
    
    return param_table

def groupby_shell(param_table, keys):
    """ Group parameters based on scattering shell. """
    
    for key in keys:
        param_table[key] = [f"{param}_s{i}" for i, param in zip(param_table["shell"], param_table[key])]
    
    return param_table

def groupby_dataset(param_table, keys):
    """ Group parameters based on dataset. """
    
    for key in keys:
        param_table[key] = [f"{param}_d{i+1}" for param, dataset in zip(param_table[key], param_table["spectra"]) for i, _ in enumerate(param_table["spectra"].unique()) if _ == dataset]
    
    return param_table

def constant_param(param_table, key, param=None):
    """ Set constant params. """
     
    if param == None:
        param = key
        
    param_table[key] = param
    
    return param_table

def independent_params(param_table, keys):
    """ Set all parameters as independent. """
    
    for key in keys:
        param_table[key] = [f"{key}_{str(i+1)}" for i in param_table.index]
    
    return param_table

def _1st_shell_e0(param_table):
    """ Separate e0 into 1st shell and the rest. (Shelly Kelly's strategy) """
    
    e0 = []
    for i in param_table["shell"]:
        if i == 1:
            e0.append("e0_s1")
        else:
            e0.append("e0_s2")
    
    param_table["e0"] = e0
    
    return param_table

def setup_feffit_params(param_table):
    """ Helper function to setup feffit_params for feffit. """
    feffit_params = param_group()
    
    # Default parameters
    params_dict = {"s02": param(1.0, min=0.6, max=12.0, vary=True),
                   "degen": param(1, min=-1.0, vary=True),
                   "sigma2": param(0.008, min=0.001, max=0.015, vary=True),
                   "e0": param(0.1, min=-25.0, max=25.0, vary=True),
                   "deltar": param(0.1, max=0.5, vary=True),
                   "alpha": param(0.0, min=-0.1, max=0.1, vary=True)} 
    
    for key in params_dict:
        if key in param_table:
            if is_string_dtype(param_table[key]):
                for i, string in enumerate(param_table[key].unique()):
                    if not np.any([symbol in string for symbol in ["*", "/", "-", "+"]]):
                        setattr(feffit_params, string, params_dict[key])

    return feffit_params

def _feffit_paths(param_table):
    """ Helper function to setup path_dict for feffit. """
    paths_dict = {}
    
    for i, row in param_table.iterrows():
        label = f"{row['scatter material']}_{row['reff']}_{i}"
        paths_dict[label] = feffpath(row["fpath"],
                                     label=label,
                                     degen=row["degen"],
                                     e0=row["e0"],
                                     sigma2=row["sigma2"],
                                     s02=row["s02"],
                                     deltar=row["deltar"])
    
    return paths_dict

def setup_feffit_paths(param_table):
    """ Setup feffit paths for multiple datasets. """
    param_table_list = [table for _, table in param_table.groupby("spectra")]
    feffit_paths = [_feffit_paths(df) for df in param_table_list]
    
    if len(feffit_paths) == 1:
        return feffit_paths[0]
    else: 
        return feffit_paths
    
    