from __future__ import print_function
from builtins import range
from builtins import object
import sys
import netCDF4 as ncf

class StkGrp(object):
    """
    Develop the stack group col/row x-ref information
    """

    def __init__(self, infile_name, grid, verbosity=False):
        """
        """
        self.infile_name = infile_name
        self.verbosity = verbosity
        self.infile = self._load_infile()
        if self.infile.GDNAM.strip() == grid.GDNAM.strip():
            self.pt_xref = {}
            self.stk_num = 0
            self._get_xref(grid)
        else:
            raise ValueError('Stack group and output grid names must match')

    def _open_NCF(self):
        '''
        Opens the netCDF input file and returns an open file object.
        '''
        try: 
            infile = ncf.Dataset(self.infile_name)
        except TypeError: 
            raise TypeError('%s not available for access or not a netCDF.' %self.infile_name)
        else: 
            return infile 

    def _load_infile(self):
        """
        Set the infile name based on the SMOKE conventions.
        """
        if self.verbosity:
            print("Stack groups: " + self.infile_name)
        return self._open_NCF()

    def _get_xref(self, grid):
        """
        Process the col and row to create a x ref to stack
        """
        # Fetch a variable from the in file
        rows = self.infile.variables['ROW'][:]
        cols = self.infile.variables['COL'][:]
        self.stk_num = rows.shape[2]
        for stack in range(rows.shape[2]):
            row = int(rows[0][0][stack][0])-1
            col = int(cols[0][0][stack][0])-1
            if col in range(grid.NCOLS) and row in range(grid.NROWS): 
                key = '%0.4d%0.4d' %(col,row)
                self.pt_xref.setdefault(key, [])
                self.pt_xref[key].append(stack)

