from __future__ import print_function
from builtins import range
from builtins import object
import numpy as np
import netCDF4 as ncf
import gzip, random
from emisqa.helpers import data_blocks
from emisqa.default_paths import tmp_dir
from emisqa.io.fauxio import Grid
import os.path

# Subclass to Fauxio
class NCFFile(object):
    """
    Instance of a NCFFile.
    """
    def __init__(self, infile_name, verbosity, zip_dict):
        self.infile_name = infile_name
        self.verbosity = verbosity
        self.NCF = self.open_NCF(zip_dict)
        try:
            self.sdate = getattr(self.NCF, 'SDATE')
        except AttributeError:
            self.sdate = '2011001'
        self.species_list = list(self.NCF.variables.keys())

    def __str__(self):
        return self.infile_name

    def __call__(self):
        return self.NCF

    def get_species(self, species_name, grid, ignore_spec, inln, stacks):
        if species_name not in self.species_list:
            if ignore_spec:
                print('WARNING: The species %s does not exist in the file %s.' %(species_name, self.infile_name))
                spec_shape = self.NCF.variables[self.species_list[0]].shape
                data_in = np.zeros(spec_shape, np.float32)
            else:
                raise ValueError('The species %s does not exist in the file %s.' %(species_name, self.infile_name))
        else:
            data_in = self.NCF.variables[species_name][:]
        # Place inline data into a 2D grid
        if inln == True:
            data_in = self.grid_inln(data_in, stacks, grid)
        return data_in

    def open_NCF(self, zip_dict = {}):
        '''
        Opens the netCDF input file and returns an open file object.
        '''
        if self.verbosity: 
            print('Opening file for reading: %s' %self.infile_name)
        try: 
            file_in = ncf.Dataset(self.infile_name, 'r')
        except TypeError:
            raise IOError('%s not a valid netCDF file. Please check file format and selected input type (-c [TYPE]).' %self.infile_name)
        except IOError:
            print('WARNING: %s not available for access.  Attempting to open zipped version.' %self.infile_name)
            if self.verbosity: 
                print('Opening file for reading: %s.gz' %self.infile_name)
            # Try to read a zipped version of the input file
            try: 
                zip_in = gzip.open(self.infile_name+'.gz','rb')
            except IOError: 
                raise IOError('%s.gz not available for access.' %self.infile_name)
            else:
                with zip_in:
                    if self.infile_name in zip_dict:
                        # Check if the file has already been unzipped
                        print('Previously unzipped version found.')
                        file_in = ncf.Dataset(zip_dict[self.infile_name], 'r')
                        return file_in
                    tmp_filename = os.path.join(tmp_dir, 'pyqa-tmp-%s.ncf' %random.randint(100, 9999999))
                    tmp_file = open(tmp_filename, 'wb')
                    for data in data_blocks(zip_in):
                        tmp_file.write(data)
                    tmp_file.close()
                    zip_dict[self.infile_name] = tmp_filename  # Store the unzipped temporary file name in the zip dictionary
                    try:
                        file_in = ncf.Dataset(tmp_filename, 'r')
                    except TypeError:
                        raise TypeError('Extracted file from %s.gz is not a valid netCDF file.' %self.infile_name)
        return file_in

    def grid_inln(self, data_in, stacks, grid):
        """
        Process the input species and adjust based on the ratio table
        """
        data_out = np.zeros([data_in.shape[0],1,grid.NROWS,grid.NCOLS], np.float32)
        for col_row, stack_list in stacks.items():
            col = int(col_row[:4])
            row = int(col_row[4:])
            data_out[:,0,row,col] = np.sum(data_in[:,0,stack_list,0], axis=1)
        return data_out[:]

    def close_file(self):
        '''
        Closes the open file
        '''
        self.NCF.close()

