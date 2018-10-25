from __future__ import print_function
from qamods.data_file import DataFile
import numpy as np
from qamods.species_array import SpeciesArray

def get_spec(species_name, opts):
    '''
    Adds together two NCF files
    '''
    if len(opts.file_name.split(',')) != 2: 
        raise ValueError('You must specify two input filenames using the -f argument.')
    file1 = DataFile(opts.file_name.split(',')[0])
    file2 = DataFile(opts.file_name.split(',')[1])
    out_dict = {}  # Create the output dictionary that will be of shape { row: { col: { speciesname: val ... } ... } ... }
    for species_name in opts.species_list:
        if opts.verbosity: 
            print('Adding for species: %s' %species_name)
        if species_name not in file1.species_list and opts.ignore_spec:
            print('WARNING: The species %s does not exist in the file %s.  Skipping.' %(species_name, file1))
            array1 = 0
        else:
            array1 = SpeciesArray(file1.dump_val(species_name, opts.all_hours, opts.grid, opts.ignore_spec, 
              opts.inln, opts.interpolate, opts.layer, opts.stacks), species_name)
            array2 = SpeciesArray(file2.dump_val(species_name, opts.all_hours, opts.grid, opts.ignore_spec, 
              opts.inln, opts.interpolate, opts.layer, opts.stacks), species_name)
            array1.add_array(array2())
        return (species_name, array1)

