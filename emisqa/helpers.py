from __future__ import division
from past.utils import old_div
from builtins import str
from builtins import zip
from builtins import range
import os
from datetime import timedelta, date, datetime
import numpy as np
from emisqa.chem_mechs import *

# Helper procedures    
def check_ev(ev_name):
    """
    Checks if an environment variable is set.
    """
    try: 
        var = os.environ[ev_name]
    except KeyError: 
        return '' 
    else: 
        return var

def parse_float(x):
    """
    Returns a floating point with the correct number of trailing zeros based on the .Dx
    """
    from math import pow
    from numpy import float64
    if 'D' in x:    
        num = float(x.strip().split('D')[0])
        exp = int(x.strip().split('D')[1])
        return float64(num * pow(10, exp))
    else:
        return float64(x)

def conv2jul(gsdate):
    """
    Returns Julian date from Gregorian date.
    """
    gdate = datetime.strptime(str(gsdate), '%Y%m%d')
    return int(datetime.strftime(gdate, '%Y%j'))

def conv2greg(jul_date):
    """
    Returns Gregorian date from a Julian date.
    """
    jdate = datetime.strptime(str(jul_date), '%Y%j')
    return datetime.strftime(jdate, '%Y%m%d')

def moles2tons(val, species_name, in_format, mech = 'cmaq_cb05'):
    """
    Converts a value or array of values from moles/s to tons/hr
    """
    mechDct = molecDct[mech]

    if species_name in mechDct: 
        factor = mechDct[species_name]
    else: 
        factor = 1

    val = val * factor   # Convert moles per second to grams per second

    if in_format != 'UAM':
        val = val * 3600   # Convert tons per second to tons per hour

    val = val * (0.00000110231131)  # Convert grams per hour to tons per hour 

    return val  

def data_blocks(infile, size=1024):
    """
    Reads in binary files by blocks
    """
    while True:
        block = infile.read(size)
        if len(block) == 0:
            break
        yield block

class RatioTable():
    '''
    Defines a degridding ratio table
    self.arr = [fips, row, col] = cell to county factor
    self.fips = list of fips in axis = 0 array order
    '''
    
    def __init__(self):
        self.arr = False
        self.fips = []

    def parse_ratio(self, region, grid, srg_file):
        """
        Parses in the county to grid conversion ratios.
        """
        with open(srg_file) as infile:
            cell_size = grid.XCELL
            cell_area = cell_size * cell_size
            ratio_table = {}    
            for line in infile:
                line = [cell.strip() for cell in line.split('\t') if cell and cell != '!']
                if line[0].startswith('#') or line[0].strip() == '': 
                    if line[0].strip() == '#GRID':
                        # Calculate grid cell offset from surrogate grid and cell range for our grid
                        xorig = float(line[2])
                        yorig = float(line[3])
                        col_offset = abs(int(old_div((xorig - grid.XORIG), cell_size)))
                        row_offset = abs(int(old_div((yorig - grid.YORIG), cell_size)))
                        col_range = range(1 + col_offset, grid.NCOLS + 1 + col_offset)
                        row_range = range(1 + row_offset, grid.NROWS + 1 + row_offset)
                else:
                    cols = ['code','fips','col','row','fac','cellarea','ctyarea','fac2']
                    row_dict = dict(list(zip(cols, line)))
                    if region == 'state': 
                        fips = row_dict['fips'][:2]
                    elif region in ('county','countyavg'): 
                        fips = row_dict['fips']
                    # Check to see if the surrogate grid col and row is within the range of our grid
                    if int(row_dict['col']) in col_range and int(row_dict['row']) in row_range:
                        ratio_table.setdefault(fips, np.zeros([grid.NROWS, grid.NCOLS], 'f'))
                        # Offset the columns and rows starting at (0,0) 
                        col = int(row_dict['col']) - col_offset - 1
                        row = int(row_dict['row']) - row_offset - 1
                        if col in range(grid.NCOLS) and row in range(grid.NROWS):
                            if region == 'countyavg':
                                divisor = float(row_dict['ctyarea'].strip())
                            else:
                                divisor = cell_area
                            ratio = old_div(float(row_dict['cellarea']), divisor)
                            ratio_table[fips][row,col] = ratio
        self.fips = sorted(ratio_table.keys())
        self.arr = np.zeros([len(self.fips), grid.NROWS, grid.NCOLS], 'f')
        for n, fips in enumerate(self.fips):
            self.arr[n,:] = ratio_table[fips][:]
        self.arr = np.ma.masked_equal(self.arr, 0)
        np.ma.set_fill_value(self.arr, 0)

def clean_temp(zip_dict):
    """
    Cleans up the temporary zip output files at the end of a run.
    """
    if len(zip_dict) == 0: 
        return
    for name in zip_dict:
        os.remove(zip_dict[name])


