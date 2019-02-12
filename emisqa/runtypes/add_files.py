from __future__ import print_function
from emisqa.data_file import DataFile
import numpy as np
from emisqa.species_array import SpeciesArray

'''
Adds variables together across multiple files
'''

def get_spec(species_name, opts):
    '''
    Dumps all summed column and rows for the day.
    '''
    file_names = [fn.strip() for fn in opts.file_name.split(',') if fn.strip()]
    out_arr = False
    if len(file_names) < 2: 
        raise ValueError('You must specify two or more input filenames using the -f argument.')
    if opts.verbosity: 
        print('Adding for species: %s' %species_name)
    for fn in file_names:
        f_in = DataFile(fn, opts.verbosity, opts.informat, opts.ptsr, opts.zip_dict)
        if species_name not in f_in.species_list and opts.ignore_spec:
            print('WARNING: The species %s does not exist in the file %s.  Skipping.' %(species_name, fn))
        else:
            species = SpeciesArray(f_in.dump_val(species_name, opts.all_hours, opts.grid, opts.ignore_spec, 
              opts.inln, opts.interpolate, opts.layer, opts.stacks), species_name)
            if out_arr:
                out_arr.add_array(species.array)
            else:
                out_arr = species
    if out_arr:
        return (species_name, out_arr)
    else:
        raise ValueError('The species %s does not exist in any input file. Please remove from species list.' %species_name)

