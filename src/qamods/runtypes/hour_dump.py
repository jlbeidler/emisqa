from __future__ import print_function
from qamods.data_file import DataFile
import numpy as np
from qamods.species_array import SpeciesArray

def get_spec(species_name, opts):
    '''
    Dumps every grid cell for every hour for each species.
    '''
    file1 = DataFile(opts.file_name, opts.verbosity, opts.informat, opts.ptsr, opts.zip_dict)
    print('Writing Domain...')
    if opts.verbosity: 
        print('Creating domain total for species: %s' %species_name)
    if species_name not in file1.species_list and opts.ignore_spec:
        print('WARNING: The species %s does not exist in the file %s.  Skipping.' %(species_name, file1))
        DV = 0
    else:
        DV = SpeciesArray(file1.dump_val(species_name, opts.all_hours, opts.grid, opts.ignore_spec, 
          opts.inln, opts.layer, opts.stacks), species_name)
    return (species_name, DV)

