from __future__ import division
from __future__ import print_function
from builtins import range
from sys import exit
from emisqa.data_file import DataFile
import numpy as np
from emisqa.species_array import SpeciesArray
from emisqa.dateloop.inday import InDay
import os.path

def get_spec(species_name, opts):
    '''
    Calculates the daily values of NCF files from a start date through the number of run dates.
    '''
    if opts.verbosity: 
        print('Creating daily sum for species: %s' %species_name)
    current_day = InDay(opts.gsdate)
    for day in range(opts.run_days):
        dayMult = current_day.currentMult()
        # Skip days that have already been represented.
        if dayMult == 0:
            if day != (opts.run_days - 1): 
                current_day.iterday()
            continue
        if opts.sector.lower() == 'mrggrid':
            infile_name = os.path.join(in_path, 'emis_mole_all_%s_%s_%s_%s.ncf' %(current_day, otps.grid, opts.spec, opts.case))
        elif opts.sector.lower() == 'mrggrid_withbeis':
            infile_name = os.path.join(opts.inpath, 'emis_mole_all_%s_%s_withbeis_%s.ncf' %(current_day, 
              opts.grid.GDNAM, opts.case))
        elif opts.sector.lower() == 'mrggrid_nobeis':
            infile_name = os.path.join(opts.inpath, 'emis_mole_all_%s_%s_nobeis_%s.ncf' %(current_day, 
              opts.grid.GDNAM, opts.case))
        else:
            infile_name = os.path.join(opts.in_path, opts.sector, 
              '%s_mole_%s_%s_%s_%s.ncf' %(opts.in_prefix, opts.sector, opts.current_day, 
              opts.grid, opts.spec, opts.case))  # v5 directory structure 
        in_file = DataFile(infile_name)
        if species_name not in list(in_file.NCF.variables.keys()) and opts.ignore_spec:
            print('WARNING: The species %s does not exist in the file %s.  Skipping.' %(species_name, in_file))
            break
        in_array = in_file.sum_val(species_name, opts.layer, opts.all_hours) * day_mult
        if day == 0: 
            SUM = SpeciesArray(in_array, species_name)
        else:
            SUM.add_array(in_array)
        in_file.close_file()
        if day != (opts.run_days - 1): 
            current_day.iterday()
    if species_name in list(in_file.NCF.variables.keys()):
        return (species_name, SUM()/opts.run_days)
    else:
        return (species_name, 0)

