# -*- coding: utf-8 -*-
"""
Created on Sat Feb 26 20:03:49 2022
@author: Jay Yan

As of March 2022, this part is not in the xraylarch documentation

This is a crude adaptation from larch.wxlib.cif_browser.py 
(https://github.com/xraypy/xraylarch/blob/master/larch/wxlib/cif_browser.py)
An equivalent to the function in CIF browser in the XAS Viewer

It generates a feff input file (.inp) from a Crystallographic Information File (.cif), 
then compute scattering path files (.dat) by feff8 (or feff6) for EXAFS fitting

"""
import os

from larch.xrd import get_amscifdb, get_cif
from larch.xafs.feffrunner import feffrunner

def generate_feff_paths(cif_path, feff_path, catom, edge, csize, asite, version8):
    """ Run full pipeline to generate feff files from cif file. """
    feff_folder = output_dir(cif_path, feff_path, catom, edge, csize, asite)
    feffinp_path = setup_feff(cif_path, feff_folder, catom, edge, csize, asite, version8)
    run_feff(feffinp_path)
    clean_feff_folder(feff_folder)
    print(f"Scatter paths generated in {feff_folder}.")

def output_dir(cif_path, feff_path, catom, edge, csize, asite):
    """ Create output directory based on feff calculations parameters. """
    cif_name = os.path.basename(cif_path)[:-4]
    fname = f"{catom}{asite}_{edge}_c{csize}_{cif_name}"
    feff_folder = os.path.join(feff_path, fname)
    
    if not os.path.exists(feff_folder):
        os.makedirs(feff_folder)
        
    return feff_folder
        
def setup_feff(cif_path, feff_folder, catom, edge, csize, asite, version8):
    """ Read cif file, then generate feff input (.inp) file. """
    ini = get_amscifdb()
    cif_id = ini.add_ciffile(cif_path)
    cif = get_cif(cif_id)
    # ciftext = cif.ciftext
    fefftext = cif.get_feffinp(catom, edge=edge, cluster_size=csize, absorber_site=asite, version8=version8)
    
    # Save feff input file (.inp)
    feffinp_path = os.path.join(feff_folder, "feff_input.inp")
    with open(feffinp_path, "w") as output:
        output.write(fefftext)
    
    return feffinp_path

def run_feff(feffinp_path):
    """ Run feffrunner from larch. """
    feff = feffrunner(feffinp=feffinp_path)
    feff.run()
    
def clean_feff_folder(feff_folder):
    """ Clean up unused, intermediate Feff files (taken from larch's "cif_browser.py ") """
    for fname in os.listdir(feff_folder):
        if (fname.endswith('.json') or fname.endswith('.pad') or
            fname.endswith('.bin') or fname.startswith('log') or
            fname in ('chi.dat', 'xmu.dat', 'misc.dat')):
            os.unlink(os.path.join(feff_folder, fname))