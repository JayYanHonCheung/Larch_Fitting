# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 19:06:28 2022
@author: Jay Yan

Notes on _feffit_result:

As usual to larch, it is organised into a group.

Notes on: fitter, fit_details, params
They are lmfit objects, which cause issue when pickling.

Notes on params:
The same variables/data seems to appear in multiple locations
1. _feffit_result.fitter.params
2. _feffit_result.fit_details.params
3. _feffit_result.params
4. _feffit_result.datasets.paths.params

"params" contains an attribute "_asteval" which causes a ".thread_lock" error pickling.
This is workaround by re-assigning param as dict(param), which should retain all the parameters while removing the _asteval.
No clue what _asteval actually does yet.

Notes on fit_details:
1. _feffit_result.fit_details
2. _feffit_result.fitter.result

Notes on fitter:

"fitter" contains a "userfcn" attribute which is a local function and causes "local function" error when pickling.
It is a "residual function" (no idea what it is)

Notes:
The cleaning procedures retrospectively cause an error on the feffit function, probably because it changes _feffit_dataset.
However, I couldn't pinpoint the exact problem.
The data seems to be presevered (as long as it is saved right after fitting) anyway.

"""
import os
import pickle
from larch.xafs import feffit_report
from lmfit import fit_report

def save(feffit_result, output_path):
    """ Save feffit and lmfit reports, then clean and pickle feffit results. 
        WIP: add safeguard in case error occurs in generating text reports.
    """
    
    save_feffit_report(feffit_result, output_path)
    save_lmfit_report(feffit_result, output_path)
    pickle_result(clean_feffit_result(feffit_result), output_path)
    
def load(pkl_path):
    """ Load pickled feffit results. """
    return pickle.load(open(pkl_path, "rb"))

def save_feffit_report(feffit_result, output_path):
    """ Generate .txt file with larch feffit report. """
    with open(os.path.join(output_path, "feffit_report.txt"), "w") as report:
        report.write(feffit_report(feffit_result))
        
def save_lmfit_report(feffit_result, output_path):
    """ Generate .txt file with lmfit fit report. """
    with open(os.path.join(output_path, "lmfit_report.txt"), "w") as report:
        report.write(fit_report(feffit_result.fit_details))

def clean_feffit_result(feffit_result):
    """ Clean out unpicklable objects within feffit_result, e.g. local functions and thread.lock objects. """

    # .fitter
    feffit_result.fitter.params = dict(feffit_result.fitter.params)
    feffit_result.fitter.userfcn = None
    
    # .fit_details
    feffit_result.fit_details.params = dict(feffit_result.fit_details.params)
    
    # .params
    feffit_result.params = dict(feffit_result.params)
    for data in feffit_result.datasets:
        for key in list(data.paths.keys()):
            data.paths[key].params = dict(data.paths[key].params)    
            
    return feffit_result

def pickle_result(result, output_path):
    """ Save object as pickle. """
    
    with open(os.path.join(output_path, "feffit_result.pkl"), "wb") as file:
        pickle.dump(result, file)