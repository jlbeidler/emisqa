from __future__ import print_function
from emisqa.data_file import DataFile
from emisqa.species_array import SpeciesArray

def get_spec(species_name, opts):
    '''
    Sums up every grid cell for every hour for each species.
    '''
    if opts.region: 
        raise ValueError('This run type does not support grid to fips conversion.  Please remove -e argument from command line.')
    file1 = DataFile(opts.filename, opts.verbosity, opts.informat, opts.ptsr, opts.zip_dict)
    if opts.verbosity: 
        print('Creating domain total for species: %s' %species_name)
    if species_name not in file1.species_list and opts.ignore_spec:
        print('WARNING: The species %s does not exist in the file %s.  Skipping.' %(species_name, file1))
        DV = 0
    else:    
        DV = SpeciesArray(file1.sum_val(species_name, opts.all_hours, opts.grid, opts.ignore_spec, 
          opts.inln, opts.interpolate, opts.layer, opts.stacks), species_name)
        DV.sum_dims()
    return (species_name, DV)

