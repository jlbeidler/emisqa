from __future__ import print_function
from builtins import range
from emisqa.data_file import DataFile
from emisqa.species_array import SpeciesArray
from emisqa.dateloop.inday import InDay
from emisqa.default_paths import *
import os.path
import numpy as np

def get_spec(species_name, opts):
    '''
    Sums the daily values of NCF files from a start date through the number of run dates.
    '''
    if opts.verbosity: 
        print('Creating daily sum for species: %s' %species_name)
    current_day = InDay(opts.gsdate, opts.rep_days, opts.run_days, smkDatesPath)
    for day in range(opts.run_days):
        day_mult = current_day.current_mult()
        # Skip days that have already been represented.
        if day_mult == 0:
            if day != (opts.run_days - 1): 
                current_day.iterday()
            continue
        # Set the input file name prefix for inline versus 2D
        if opts.inln:
            inPrefix = 'inln'
        else:
            inPrefix = 'emis'
        if opts.sector.lower() == 'mrggrid':
            infile_name = os.path.join(opts.inpath, 'emis_mole_all_%s_%s_nobeis_%s.ncf' %(current_day, 
              opts.grid.GDNAM, opts.case))
        else:
            infile_name = os.path.join(opts.inpath, opts.sector, '%s_mole_%s_%s_%s_%s_%s.ncf' %(inPrefix, 
              opts.sector, current_day, opts.grid.GDNAM, opts.spec, opts.case))  # v5 directory structure 
        infile = DataFile(infile_name, opts.verbosity, opts.informat, opts.ptsr, opts.zip_dict)
        if species_name not in infile.species_list and opts.ignore_spec:
            print('WARNING: The species %s does not exist in the file %s.  Skipping.' %(species_name, infile))
            SUM = SpeciesArray(np.zeros([1,opts.grid.NROWS,opts.grid.NCOLS]), species_name)
            break
        inArray = infile.sum_val(species_name, opts.all_hours, opts.grid, 
          opts.ignore_spec, opts.inln, opts.interpolate, opts.layer, 
          opts.stacks) * day_mult
        if day == 0: 
            SUM = SpeciesArray(inArray, species_name)
        else:
            SUM.add_array(inArray)
        infile.close_file()
        if day != (opts.run_days - 1): 
            current_day.iterday()
    return (species_name, SUM)

