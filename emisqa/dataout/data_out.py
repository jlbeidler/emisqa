from __future__ import print_function
from builtins import str
from builtins import range
from builtins import object
import numpy as np
from datetime import date, datetime, timedelta
from emisqa.helpers import conv2jul, RatioTable
import emisqa.io.fauxio as io

class DataOut(object):
    """
    Outfile class.
    """

    def __init__(self, outfile_name, out_type, gsdate, verbosity = False):
        self.outfile_name = outfile_name
        self.out_type = out_type.upper()
        self.gsdate = gsdate
        self.verbosity = verbosity    
        if self.verbosity == True: 
            print('Opening %s file for writing: %s' %(self.out_type, self.outfile_name))
        if self.out_type == 'NCF':
            self.outfile = self._open_NCF()
        elif self.out_type == 'CSV':
            self.outfile = self._open_CSV()
        else:
            raise ValueError('Wrong outfile type specified.')

    def __str__(self):
        return self.outfile_name

    def __call__(self):
        return self.outfile

    def write_outfile(self, out_dict, grid, region, tons, units, srg_file):
        species_list = list(out_dict.keys())
        while '0' in species_list:  # Dunno why this gets inserted?
            species_list.remove('0')
        self.species_list = sorted(species_list)
        if self.out_type == 'NCF':
            self._write_NCF(out_dict, self.species_list, grid, tons, units)
        elif self.out_type == 'CSV':
            if region == 'state' or region == 'county':
                self._write_FIPS_CSV(out_dict, self.species_list, grid, tons, region, srg_file)
            else: 
                self._write_grid_CSV(out_dict, self.species_list, tons)

    def _open_CSV(self):
        try: 
            outfile = open(self.outfile_name, 'w')
        except IOError:
            raise IOError('%s not available for access.' %self.outfile_name)
        else: 
            return outfile 

    def _write_grid_CSV(self, out_dict, species_list, tons):
        '''
        Writes the dictionary to an output file in csv format by grid cell.  Takes output dictionary and the species_list.
        '''
        hours = out_dict[species_list[0]]().shape[0]
        if hours == 1:
            hour_type = 'sum'
        else:
            hour_type = 'hourly' 
        self.outfile.write('hour,row,col,' + ','.join(species_name for species_name in species_list) + '\n')
        for hour in range(hours):
            if hour_type == 'sum':
                out_hour = 'sum'
            else:
                out_hour = hour
            for row in range(out_dict[species_list[0]]().shape[1]):
                srow = str(row)
                for col in range(out_dict[species_list[0]]().shape[2]):
                    scol = str(col) 
                    outline = '%s,%s,%s' %(out_hour, row + 1, col + 1)
                    for species_name in species_list:
                        outline = '%s,%s' %(outline, out_dict[species_name]()[hour,row,col])
                    self.outfile.write(outline + '\n')

    def _write_FIPS_CSV(self, out_dict, species_list, grid, tons, region, srg_file):
        '''
        Writes the dictionary to an output file in csv format by fips.  Takes output dictionary and the species_list.
        '''
        if not grid: 
            raise ValueError('No grid specified.  Grid needed to write state or county based csv.')
        import pandas as pd
        ratio_table = RatioTable()
        ratio_table.parse_ratio(region, grid, srg_file)
        hours = out_dict[species_list[0]]().shape[0]
        df = pd.DataFrame()
        for n, fips in enumerate(ratio_table.fips):
            fipsdf = pd.DataFrame()
            factors = np.tile(ratio_table.arr[n,:], (hours,1,1))
            for species_name in species_list:
                vals = pd.DataFrame((out_dict[species_name]() * factors).sum(axis=(1,2)), 
                  columns=[species_name,]) 
                vals['hour'] = vals.index 
                vals['fips'] = fips
                if len(fipsdf) == 0:
                    fipsdf = vals
                else:
                    fipsdf = pd.concat((fipsdf, vals[species_name]), axis=1)
            df = pd.concat((df, fipsdf))
        cols = ['hour','fips'] + species_list
        df.to_csv(self.outfile, columns=cols, index=False)

    def _awrite_FIPS_CSV(self, out_dict, species_list, grid, tons, region, srg_file):
        '''
        Writes the dictionary to an output file in csv format by fips.  Takes output dictionary and the species_list.
        '''
        if not grid: 
            raise ValueError('No grid specified.  Grid needed to write state or county based csv.')
        import pandas as pd
        ratio_table = parse_ratio(region, grid, srg_file)
        fips_list = sorted(ratio_table.keys())
        hours = out_dict[species_list[0]]().shape[0]
        df = pd.DataFrame()
        for fips in fips_list:
            fipsdf = pd.DataFrame()
            factors = np.tile(ratio_table[fips][:], (hours,1,1))
            for species_name in species_list:
                vals = pd.DataFrame((out_dict[species_name]()[:] * factors).sum(axis=(1,2)), 
                  columns=[species_name,]) 
                vals['hour'] = vals.index 
                vals['fips'] = fips
                if len(fipsdf) == 0:
                    fipsdf = vals
                else:
                    fipsdf = pd.concat((fipsdf, vals[species_name]), axis=1)
            df = pd.concat((df, fipsdf))
        cols = ['hour','fips'] + species_list
        df.to_csv(self.outfile, columns=cols, index=False)

    def _open_NCF(self):
        '''
        Opens the netCDF input file and returns an open file object.
        '''
        try: 
            outfile = io.IODataset(self.outfile_name, 'w')
        except TypeError:
            raise IOError('%s not available for access.' %self.outfile_name)
        else: 
            return outfile 

    def _write_NCF(self, out_dict, species_list, grid, tons = False, units = ''):
        '''
        Writes the dictionary to an output file in NCF format.  Takes output dictionary and the species_list.
        '''
        hours = out_dict[species_list[0]]().shape[0]
        self.outfile.set_dimensions('GRID', LAY=1, ROW=grid.NROWS, COL=grid.NCOLS, VAR=len(species_list))
        for species_name in species_list:
            self._write_species(out_dict, species_name, tons, units)
        self._outfile_settings(hours, grid)
        self.outfile.write_TFLAG()
        self.outfile.close()
            
    def _write_species(self, out_dict, species_name, tons = False, units = '', long_name = '', var_desc = ''):
        """
        Takes the output dictionary, species name, and optionally long name, units, and variable description.
        Creates a species of name species_name with the standard smoke shape of TSTEP, LAY, ROW, and COL.
        Returns a multidimensional array of shape TSTEP, LAY, ROW, COL.
        """
        if not units:
            if tons:
                units = 'tons/day'
            else:
                units = 'moles/s'
        if not long_name: 
            long_name = species_name
        if not var_desc: 
            var_desc = 'Model species ' + species_name
        d_shape = [out_dict[species_name]().shape[0],1,out_dict[species_name]().shape[1],out_dict[species_name]().shape[2]]
        species_out = self.outfile.create_variable(species_name, 'REAL', ('TSTEP','LAY','ROW','COL'), 
          long_name=long_name, units=units, var_desc=var_desc)
        data_out = np.zeros(d_shape, np.float32)
        for lay in range(data_out.shape[1]):
                try:
                    data_out[:,lay,:,:] = out_dict[species_name]()
                except ValueError:
                    raise ValueError('Array size mismatch. Please check that input domain matches the size of the intended output domain (-G [GRID]).')
        species_out[:] = data_out

    def _outfile_settings(self, hours, grid):
        '''
        Set the output file dimensions and IOAPI metadata
        '''
        # Set the time step based on how many hours are in the DS
        if hours > 1:
            hstep = 10000
        else:
            hstep = 240000
        esdate = conv2jul(self.gsdate)
        self.outfile.set_attributes(esdate, grid, FILEDESC='EMISQA'.ljust(80), TSTEP=hstep)

