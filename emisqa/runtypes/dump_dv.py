from __future__ import print_function
from emisqa.data_file import DataFile
import numpy as np
from emisqa.species_array import SpeciesArray

def get_spec(species_name, opts):
    '''
    Dumps all summed column and rows for the day.
    '''
    file1 = DataFile(opts.file_name, opts.verbosity, opts.informat, opts.ptsr, opts.zip_dict)
    if opts.verbosity: 
        print('Creating summed dump for species: %s' %species_name)
    if species_name not in file1.species_list and opts.ignore_spec:
        print('WARNING: The species %s does not exist in the file %s.  Skipping.' %(species_name, file1))
        DV = 0
    else:
        DV = SpeciesArray(file1.sum_val(species_name, opts.all_hours, opts.grid, opts.ignore_spec, 
          opts.inln, opts.interpolate, opts.layer, opts.stacks), species_name)
    return (species_name, DV)

